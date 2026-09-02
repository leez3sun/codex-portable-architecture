import json
import os
import subprocess
import sys

ABAQUS = os.environ.get("ABAQUS_COMMAND", "abaqus")

TOOLS = [
    {"name": "abaqus_environment", "description": "Check the installed Abaqus release and command.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "abaqus_create_billiards", "description": "Create the included 3D Explicit billiard collision as a brand-new project. Refuses existing paths and never edits existing CAE files.", "inputSchema": {"type": "object", "properties": {"project_dir": {"type": "string", "description": "A new project directory that must not already exist."}}, "required": ["project_dir"]}},
    {"name": "abaqus_create_pool_game", "description": "Create a new 2.5D pool table with 3D balls and functional pockets.", "inputSchema": {"type": "object", "properties": {"project_dir": {"type": "string"}}, "required": ["project_dir"]}},
    {"name": "abaqus_create_three_shot_game", "description": "Create three animation jobs: triangular-rack break and two pocket shots.", "inputSchema": {"type": "object", "properties": {"project_dir": {"type": "string"}}, "required": ["project_dir"]}},
    {"name": "abaqus_create_continuous_visual_game", "description": "Create one continuous visual pool-game CAE with colored balls, animated yellow cues, rigid white rails and timed pocket stops.", "inputSchema": {"type": "object", "properties": {"project_dir": {"type": "string"}}, "required": ["project_dir"]}}
]

def run(args, cwd=None, timeout=300):
    p = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, shell=False)
    return p.returncode, p.stdout

def text_result(text, error=False):
    return {"content": [{"type": "text", "text": text}], "isError": error}

def call_tool(name, a):
    if name == "abaqus_environment":
        code, out = run([ABAQUS, "information=release"], timeout=60)
        return text_result(out.strip(), code != 0)
    if name in ("abaqus_create_billiards", "abaqus_create_pool_game", "abaqus_create_three_shot_game", "abaqus_create_continuous_visual_game"):
        workdir = os.path.abspath(a.get("project_dir", ""))
        if os.path.exists(workdir):
            return text_result("Safety refusal: project_dir already exists. Choose a new path; existing CAE projects are never opened or modified: " + workdir, True)
        parent = os.path.dirname(workdir)
        if not os.path.isdir(parent):
            return text_result("Parent directory does not exist: " + parent, True)
        os.mkdir(workdir)
        scripts={"abaqus_create_billiards":"create_billiards.py","abaqus_create_pool_game":"create_pool_game.py","abaqus_create_three_shot_game":"create_three_shot_game.py","abaqus_create_continuous_visual_game":"create_continuous_final.py"}
        script = os.path.join(os.path.dirname(__file__),scripts[name])
    else:
        return text_result("Unknown tool: " + name, True)
    code, out = run([ABAQUS, "cae", "noGUI=" + script], cwd=workdir, timeout=900)
    return text_result("exit_code=%d\n%s" % (code, out[-12000:]), code != 0)

def reply(req, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": req.get("id")}
    if error: msg["error"] = error
    else: msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n"); sys.stdout.flush()

for line in sys.stdin:
    try:
        req = json.loads(line); method = req.get("method")
        if method == "initialize":
            reply(req, {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "abaqus-cae", "version": "0.1.0"}})
        elif method == "tools/list": reply(req, {"tools": TOOLS})
        elif method == "tools/call": reply(req, call_tool(req["params"]["name"], req["params"].get("arguments", {})))
        elif "id" in req: reply(req, {})
    except Exception as e:
        if 'req' in locals() and "id" in req: reply(req, error={"code": -32603, "message": str(e)})
