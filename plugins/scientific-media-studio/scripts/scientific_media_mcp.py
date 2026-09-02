from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


TOOLS = [
    {
        "name": "studio_doctor",
        "description": "Check local Python modules and media executables used by Scientific Media Studio.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "create_svg_plot",
        "description": "Create an editable scientific SVG line or scatter plot from numeric CSV columns.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "csv_path": {"type": "string"},
                "x_column": {"type": "string"},
                "y_columns": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "output_path": {"type": "string"},
                "kind": {"type": "string", "enum": ["line", "scatter"], "default": "line"},
                "title": {"type": "string", "default": ""},
                "x_label": {"type": "string", "default": ""},
                "y_label": {"type": "string", "default": ""}
            },
            "required": ["csv_path", "x_column", "y_columns", "output_path"],
            "additionalProperties": False
        },
    },
    {
        "name": "compose_image_panels",
        "description": "Compose raster images into a labeled A/B/C multi-panel figure without changing the originals.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_paths": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "output_path": {"type": "string"},
                "columns": {"type": "integer", "minimum": 1, "default": 2},
                "cell_width": {"type": "integer", "minimum": 64},
                "cell_height": {"type": "integer", "minimum": 64},
                "dpi": {"type": "integer", "minimum": 72, "default": 300}
            },
            "required": ["input_paths", "output_path"],
            "additionalProperties": False
        },
    },
    {
        "name": "render_science_poster",
        "description": "Render an editable asymmetric scientific poster SVG from a local JSON specification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_path": {"type": "string"},
                "output_path": {"type": "string"}
            },
            "required": ["spec_path", "output_path"],
            "additionalProperties": False
        },
    },
    {
        "name": "probe_media",
        "description": "Inspect media streams, dimensions, duration, frame rate, codecs, and metadata with FFprobe.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string"},
                "output_json_path": {"type": "string"}
            },
            "required": ["input_path"],
            "additionalProperties": False
        },
    },
    {
        "name": "extract_video_thumbnail",
        "description": "Extract one video frame at an explicit time to a new image file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string"},
                "time_seconds": {"type": "number", "minimum": 0, "default": 0},
                "output_path": {"type": "string"}
            },
            "required": ["input_path", "output_path"],
            "additionalProperties": False
        },
    },
    {
        "name": "transcode_video",
        "description": "Transcode video locally to a new H.264/AAC MP4 with optional width, height, and frame rate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string"},
                "output_path": {"type": "string"},
                "width": {"type": "integer", "minimum": 2},
                "height": {"type": "integer", "minimum": 2},
                "fps": {"type": "number", "exclusiveMinimum": 0},
                "crf": {"type": "integer", "minimum": 0, "maximum": 51, "default": 18}
            },
            "required": ["input_path", "output_path"],
            "additionalProperties": False
        },
    },
    {
        "name": "init_video_preference_profile",
        "description": "Create a local, interpretable project profile for positive and negative scientific-video keyframe feedback.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "output_path": {"type": "string"}
            },
            "required": ["project", "output_path"],
            "additionalProperties": False
        },
    },
    {
        "name": "add_video_keyframe_feedback",
        "description": "Add a positive or negative keyframe/region example and convert concrete negative tags into enforceable local rules.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile_path": {"type": "string"},
                "frame_path": {"type": "string"},
                "sentiment": {"type": "string", "enum": ["positive", "negative"]},
                "weight": {"type": "integer", "enum": [1, 2], "default": 1},
                "tags": {"type": "array", "items": {"type": "string"}},
                "notes": {"type": "string", "default": ""},
                "region": {"type": "array", "items": {"type": "number", "minimum": 0, "maximum": 1}, "minItems": 4, "maxItems": 4},
                "timestamp_seconds": {"type": "number", "minimum": 0}
            },
            "required": ["profile_path", "frame_path", "sentiment", "tags"],
            "additionalProperties": False
        },
    },
    {
        "name": "score_video_keyframe",
        "description": "Score one candidate keyframe against scientific gates, learned blockers, layout checks, and positive preferences.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile_path": {"type": "string"},
                "frame_path": {"type": "string"},
                "manifest_path": {"type": "string"},
                "output_path": {"type": "string"}
            },
            "required": ["profile_path", "frame_path", "manifest_path", "output_path"],
            "additionalProperties": False
        },
    },
    {
        "name": "build_video_revision_plan",
        "description": "Combine keyframe score reports into a blocker-first revision plan and decide whether full rendering may proceed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile_path": {"type": "string"},
                "report_paths": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "output_path": {"type": "string"}
            },
            "required": ["profile_path", "report_paths", "output_path"],
            "additionalProperties": False
        },
    },
]


def require_string(arguments: dict[str, Any], name: str) -> str:
    value = arguments.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def execute_script(script: str, args: list[str]) -> str:
    command = [sys.executable, "-X", "utf8", str(ROOT / script), *args]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "Unknown child-process error").strip()
        raise RuntimeError(f"{script} failed with exit code {result.returncode}: {detail}")
    return result.stdout.strip() or "Completed"


def call_tool(name: str, arguments: dict[str, Any]) -> str:
    if name == "studio_doctor":
        return execute_script("doctor.py", [])
    if name == "create_svg_plot":
        ys = arguments.get("y_columns")
        if not isinstance(ys, list) or not ys or not all(isinstance(item, str) and item for item in ys):
            raise ValueError("y_columns must be a non-empty string array")
        args = [
            "plot", "--csv", require_string(arguments, "csv_path"),
            "--x", require_string(arguments, "x_column"), "--y", ",".join(ys),
            "--kind", str(arguments.get("kind", "line")),
            "--title", str(arguments.get("title", "")),
            "--xlabel", str(arguments.get("x_label", "")),
            "--ylabel", str(arguments.get("y_label", "")),
            "--output", require_string(arguments, "output_path"),
        ]
        return execute_script("figure_factory.py", args)
    if name == "compose_image_panels":
        inputs = arguments.get("input_paths")
        if not isinstance(inputs, list) or not inputs or not all(isinstance(item, str) and item for item in inputs):
            raise ValueError("input_paths must be a non-empty string array")
        args = ["panel", "--inputs", *inputs, "--columns", str(arguments.get("columns", 2)), "--dpi", str(arguments.get("dpi", 300)), "--output", require_string(arguments, "output_path")]
        if "cell_width" in arguments:
            args.extend(["--cell-width", str(arguments["cell_width"])])
        if "cell_height" in arguments:
            args.extend(["--cell-height", str(arguments["cell_height"])])
        return execute_script("figure_factory.py", args)
    if name == "render_science_poster":
        return execute_script("poster_factory.py", ["--spec", require_string(arguments, "spec_path"), "--output", require_string(arguments, "output_path")])
    if name == "probe_media":
        args = ["probe", "--input", require_string(arguments, "input_path")]
        if arguments.get("output_json_path"):
            args.extend(["--output", require_string(arguments, "output_json_path")])
        return execute_script("media_pipeline.py", args)
    if name == "extract_video_thumbnail":
        return execute_script("media_pipeline.py", ["thumbnail", "--input", require_string(arguments, "input_path"), "--time", str(arguments.get("time_seconds", 0)), "--output", require_string(arguments, "output_path")])
    if name == "transcode_video":
        args = ["transcode", "--input", require_string(arguments, "input_path"), "--output", require_string(arguments, "output_path"), "--crf", str(arguments.get("crf", 18))]
        for field in ("width", "height", "fps"):
            if field in arguments:
                args.extend([f"--{field}", str(arguments[field])])
        return execute_script("media_pipeline.py", args)
    if name == "init_video_preference_profile":
        return execute_script("keyframe_preferences.py", ["init", "--project", require_string(arguments, "project"), "--output", require_string(arguments, "output_path")])
    if name == "add_video_keyframe_feedback":
        tags = arguments.get("tags")
        if not isinstance(tags, list) or not all(isinstance(item, str) and item.strip() for item in tags):
            raise ValueError("tags must be a string array")
        args = [
            "add", "--profile", require_string(arguments, "profile_path"),
            "--frame", require_string(arguments, "frame_path"),
            "--sentiment", require_string(arguments, "sentiment"),
            "--weight", str(arguments.get("weight", 1)),
            "--tags", ",".join(tags),
            "--notes", str(arguments.get("notes", "")),
        ]
        if "region" in arguments:
            region = arguments["region"]
            if not isinstance(region, list) or len(region) != 4:
                raise ValueError("region must contain four normalized numbers")
            args.extend(["--region", ",".join(str(item) for item in region)])
        if "timestamp_seconds" in arguments:
            args.extend(["--timestamp", str(arguments["timestamp_seconds"])])
        return execute_script("keyframe_preferences.py", args)
    if name == "score_video_keyframe":
        return execute_script("keyframe_preferences.py", [
            "score", "--profile", require_string(arguments, "profile_path"),
            "--frame", require_string(arguments, "frame_path"),
            "--manifest", require_string(arguments, "manifest_path"),
            "--output", require_string(arguments, "output_path"),
        ])
    if name == "build_video_revision_plan":
        reports = arguments.get("report_paths")
        if not isinstance(reports, list) or not reports or not all(isinstance(item, str) and item for item in reports):
            raise ValueError("report_paths must be a non-empty string array")
        return execute_script("keyframe_preferences.py", [
            "plan", "--profile", require_string(arguments, "profile_path"),
            "--reports", *reports, "--output", require_string(arguments, "output_path"),
        ])
    raise ValueError(f"Unknown tool: {name}")


def response(message_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": message_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    return payload


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    message_id = message.get("id")
    if method == "initialize":
        requested = message.get("params", {}).get("protocolVersion", "2024-11-05")
        return response(message_id, {"protocolVersion": requested, "capabilities": {"tools": {}}, "serverInfo": {"name": "scientific-media-studio", "version": "0.1.0"}})
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return response(message_id, {})
    if method == "tools/list":
        return response(message_id, {"tools": TOOLS})
    if method == "tools/call":
        params = message.get("params", {})
        try:
            output = call_tool(str(params.get("name", "")), params.get("arguments") or {})
            return response(message_id, {"content": [{"type": "text", "text": output}], "isError": False})
        except Exception as exc:
            return response(message_id, {"content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}], "isError": True})
    if message_id is not None:
        return response(message_id, error={"code": -32601, "message": f"Method not found: {method}"})
    return None


def main() -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
            outgoing = handle(message)
            if outgoing is not None:
                sys.stdout.write(json.dumps(outgoing, ensure_ascii=False, separators=(",", ":")) + "\n")
                sys.stdout.flush()
        except Exception as exc:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(exc)}}, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
