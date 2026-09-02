import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


FLUENT = os.environ.get("FLUENT_EXE", "fluent")
SPACECLAIM = os.environ.get("SPACECLAIM_EXE", "SpaceClaim.exe")
LMUTIL = os.environ.get("ANSYS_LMUTIL", "lmutil")
LICENSE_SERVER = os.environ.get("ANSYSLMD_LICENSE_FILE", "1055@localhost")
ANSYS_ROOT = Path(os.environ.get("AWP_ROOT241", ""))
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
PROBE = Path(__file__).with_name("pyfluent_probe.py")
ASCII_WORKDIR = Path(tempfile.gettempdir()) / "ansys-codex"


TOOLS = [
    {
        "name": "ansys_environment",
        "description": "Check the installed ANSYS, Fluent, SpaceClaim, CFD-Post, Python, and PyFluent bridge paths.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ansys_license_features",
        "description": "Check the local license server and the Fluent, SpaceClaim, and SolidWorks translator features.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "fluent_solver_smoke_test",
        "description": "Launch the local Fluent solver through PyFluent, execute a small RPC expression, and exit.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "fluent_meshing_smoke_test",
        "description": "Launch Fluent Meshing through PyFluent, initialize Watertight Geometry, verify Import Geometry, and exit.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_cad_models",
        "description": "List supported CAD model files under a project directory without changing them.",
        "inputSchema": {
            "type": "object",
            "properties": {"project_dir": {"type": "string"}},
            "required": ["project_dir"],
        },
    },
    {
        "name": "spaceclaim_open_model",
        "description": "Open one existing CAD file in the local SpaceClaim GUI for inspection. The source model is not saved or modified by this tool.",
        "inputSchema": {
            "type": "object",
            "properties": {"model_path": {"type": "string"}},
            "required": ["model_path"],
        },
    },
    {
        "name": "fluent_run_journal",
        "description": "Run a reviewed Fluent journal in solver or meshing mode. The journal must be inside the given working directory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "journal_path": {"type": "string"},
                "workdir": {"type": "string"},
                "mode": {"type": "string", "enum": ["solver", "meshing"]},
                "processor_count": {"type": "integer", "minimum": 1, "maximum": 32},
                "timeout_seconds": {"type": "integer", "minimum": 30, "maximum": 86400},
            },
            "required": ["journal_path", "workdir", "mode"],
        },
    },
]


def run(args, cwd=None, timeout=300):
    result = subprocess.run(
        args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        timeout=timeout,
        shell=False,
    )
    return result.returncode, result.stdout


def text_result(value, error=False):
    return {"content": [{"type": "text", "text": str(value)}], "isError": error}


def inside(child, parent):
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def environment_report():
    paths = {
        "ansys_root": ANSYS_ROOT,
        "fluent": Path(FLUENT),
        "spaceclaim": Path(SPACECLAIM),
        "workbench": ANSYS_ROOT / "Framework" / "bin" / "Win64" / "RunWB2.exe",
        "cfd_post": ANSYS_ROOT / "CFD-Post" / "bin" / "cfdpost.exe",
        "pyfluent_probe": PROBE,
    }
    lines = ["ANSYS_VERSION=" + os.environ.get("ANSYS_VERSION", "unknown")]
    lines.extend(f"{name}={path} exists={path.exists()}" for name, path in paths.items())
    lines.append("python=" + sys.executable)
    lines.append("license_server=" + LICENSE_SERVER)
    return "\n".join(lines)


def license_report():
    chunks = []
    for feature in ("acfd_fluent", "a_spaceclaim_dirmod", "xlate_solidworks"):
        code, output = run([LMUTIL, "lmstat", "-f", feature, "-c", LICENSE_SERVER], timeout=60)
        chunks.append(f"[{feature}] exit_code={code}\n{output.strip()}")
    return "\n\n".join(chunks)


def call_tool(name, args):
    ASCII_WORKDIR.mkdir(parents=True, exist_ok=True)
    if name == "ansys_environment":
        return text_result(environment_report())
    if name == "ansys_license_features":
        report = license_report()
        return text_result(report, "license server UP" not in report)
    if name in ("fluent_solver_smoke_test", "fluent_meshing_smoke_test"):
        mode = "solver" if name == "fluent_solver_smoke_test" else "meshing"
        code, output = run([sys.executable, str(PROBE), mode], cwd=str(ASCII_WORKDIR), timeout=240)
        return text_result(f"exit_code={code}\n{output[-16000:]}", code != 0 or "PROBE_OK" not in output)
    if name == "list_cad_models":
        project = Path(args.get("project_dir", "")).expanduser().resolve()
        if not project.is_dir():
            return text_result("Project directory does not exist: " + str(project), True)
        extensions = {".sldprt", ".sldasm", ".step", ".stp", ".x_t", ".x_b", ".iges", ".igs", ".scdoc"}
        files = sorted(path for path in project.rglob("*") if path.is_file() and path.suffix.lower() in extensions)
        return text_result("\n".join(str(path) for path in files) or "No supported CAD files found.")
    if name == "spaceclaim_open_model":
        model = Path(args.get("model_path", "")).expanduser().resolve()
        if not model.is_file():
            return text_result("Model does not exist: " + str(model), True)
        allowed = {".sldprt", ".sldasm", ".step", ".stp", ".x_t", ".x_b", ".iges", ".igs", ".scdoc"}
        if model.suffix.lower() not in allowed:
            return text_result("Unsupported CAD extension: " + model.suffix, True)
        subprocess.Popen([SPACECLAIM, str(model)], cwd=str(ASCII_WORKDIR), shell=False)
        return text_result("Opened in SpaceClaim: " + str(model))
    if name == "fluent_run_journal":
        workdir = Path(args.get("workdir", "")).expanduser().resolve()
        journal = Path(args.get("journal_path", "")).expanduser().resolve()
        if not workdir.is_dir():
            return text_result("Working directory does not exist: " + str(workdir), True)
        if not journal.is_file() or not inside(journal, workdir):
            return text_result("Safety refusal: journal must exist inside workdir.", True)
        if len(str(workdir).encode("ascii", errors="ignore")) != len(str(workdir)):
            return text_result("Use an ASCII-only workdir for ANSYS 2024 R1 PyFluent compatibility.", True)
        mode = args.get("mode")
        processors = int(args.get("processor_count", 2))
        timeout = int(args.get("timeout_seconds", 3600))
        command = [FLUENT, "3ddp"]
        if mode == "meshing":
            command.append("-meshing")
        command.extend(["-g", f"-t{processors}", "-i", str(journal)])
        code, output = run(command, cwd=str(workdir), timeout=timeout)
        return text_result(f"exit_code={code}\n{output[-16000:]}", code != 0)
    return text_result("Unknown tool: " + name, True)


def reply(request, result=None, error=None):
    message = {"jsonrpc": "2.0", "id": request.get("id")}
    if error is not None:
        message["error"] = error
    else:
        message["result"] = result
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


for line in sys.stdin:
    try:
        request = json.loads(line)
        method = request.get("method")
        if method == "initialize":
            reply(
                request,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "ansys-fluent", "version": "0.1.0"},
                },
            )
        elif method == "tools/list":
            reply(request, {"tools": TOOLS})
        elif method == "tools/call":
            params = request.get("params", {})
            reply(request, call_tool(params.get("name"), params.get("arguments", {})))
        elif "id" in request:
            reply(request, {})
    except Exception as exc:
        if "request" in locals() and "id" in request:
            reply(request, error={"code": -32603, "message": str(exc)})
