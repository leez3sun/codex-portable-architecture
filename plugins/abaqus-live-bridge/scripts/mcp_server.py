import json
import os
import socket
import sys
import traceback


HOST = os.environ.get("ABAQUS_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("ABAQUS_BRIDGE_PORT", "50001"))
PROTOCOL_VERSION = "2024-11-05"


def read_message():
    headers = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        key, value = line.decode("ascii").split(":", 1)
        headers[key.strip().lower()] = value.strip()

    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    body = sys.stdin.buffer.read(length)
    return json.loads(body.decode("utf-8"))


def write_message(message):
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    sys.stdout.buffer.write(b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n\r\n")
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def text_result(text, is_error=False):
    return {
        "content": [{"type": "text", "text": str(text)}],
        "isError": bool(is_error),
    }


def send_to_abaqus(command, payload=None, timeout=120):
    request = {"command": command, "payload": payload or {}}
    data = (json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8")
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            sock.settimeout(timeout)
            sock.sendall(data)
            sock.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
    except OSError as exc:
        bridge_script = os.path.join(os.path.dirname(__file__), "abaqus_mcp_bridge.py")
        raise RuntimeError(
            "Cannot reach Abaqus bridge at %s:%s. Start Abaqus/CAE and run "
            "%s first. Original error: %s" % (HOST, PORT, bridge_script, exc)
        )
    if not chunks:
        raise RuntimeError("Abaqus bridge returned no data.")
    response = json.loads(b"".join(chunks).decode("utf-8"))
    if not response.get("ok"):
        raise RuntimeError(response.get("error", "Abaqus command failed."))
    return response.get("result", "")


TOOLS = [
    {
        "name": "abaqus_status",
        "description": "Check whether the Abaqus/CAE local bridge is running.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "abaqus_exec",
        "description": "Execute Python code inside the connected Abaqus/CAE kernel.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute in Abaqus/CAE.",
                },
                "timeout": {
                    "type": "number",
                    "description": "Socket timeout in seconds.",
                    "default": 120,
                },
            },
            "required": ["code"],
        },
    },
    {
        "name": "abaqus_eval",
        "description": "Evaluate a Python expression inside the connected Abaqus/CAE kernel and return repr(value).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Python expression to evaluate in Abaqus/CAE.",
                },
                "timeout": {
                    "type": "number",
                    "description": "Socket timeout in seconds.",
                    "default": 120,
                },
            },
            "required": ["expression"],
        },
    },
]


def handle_request(message):
    method = message.get("method")
    msg_id = message.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "abaqus-mcp", "version": "0.1.0"},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = message.get("params", {})
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            if name == "abaqus_status":
                result = send_to_abaqus("status", timeout=10)
                return {"jsonrpc": "2.0", "id": msg_id, "result": text_result(result)}
            if name == "abaqus_exec":
                result = send_to_abaqus("exec", {"code": args["code"]}, timeout=float(args.get("timeout", 120)))
                return {"jsonrpc": "2.0", "id": msg_id, "result": text_result(result)}
            if name == "abaqus_eval":
                result = send_to_abaqus("eval", {"expression": args["expression"]}, timeout=float(args.get("timeout", 120)))
                return {"jsonrpc": "2.0", "id": msg_id, "result": text_result(result)}
            raise RuntimeError("Unknown tool: %s" % name)
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": msg_id, "result": text_result(str(exc), is_error=True)}

    if msg_id is None:
        return None
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": "Method not found: %s" % method},
    }


def main():
    while True:
        try:
            message = read_message()
            if message is None:
                break
            response = handle_request(message)
            if response is not None:
                write_message(response)
        except Exception:
            traceback.print_exc(file=sys.stderr)
            break


if __name__ == "__main__":
    main()
