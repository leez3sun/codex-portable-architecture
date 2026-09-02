from __future__ import print_function

import contextlib
import io
import json
import socket
import sys
import threading
import traceback


HOST = "127.0.0.1"
PORT = 50001


try:
    from abaqus import mdb, session
    from abaqusConstants import *
except Exception:
    mdb = None
    session = None


GLOBALS = globals()


def _execute(command, payload):
    if command == "status":
        model_count = len(getattr(mdb, "models", {})) if mdb is not None else 0
        return "Abaqus MCP bridge is running on %s:%s. models=%s" % (HOST, PORT, model_count)

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        if command == "exec":
            code = payload.get("code", "")
            exec(compile(code, "<codex-abaqus-exec>", "exec"), GLOBALS, GLOBALS)
            output = stdout.getvalue()
            return output if output else "OK"
        if command == "eval":
            expression = payload.get("expression", "")
            value = eval(compile(expression, "<codex-abaqus-eval>", "eval"), GLOBALS, GLOBALS)
            output = stdout.getvalue()
            prefix = output if output else ""
            return prefix + repr(value)

    raise ValueError("Unknown command: %s" % command)


def _handle_client(conn):
    try:
        chunks = []
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
        request = json.loads(b"".join(chunks).decode("utf-8").strip())
        result = _execute(request.get("command"), request.get("payload") or {})
        response = {"ok": True, "result": result}
    except Exception:
        response = {"ok": False, "error": traceback.format_exc()}
    try:
        conn.sendall(json.dumps(response, ensure_ascii=False).encode("utf-8"))
    finally:
        conn.close()


def _serve():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(8)
    print("Abaqus MCP bridge listening on %s:%s" % (HOST, PORT))
    while True:
        conn, _addr = server.accept()
        thread = threading.Thread(target=_handle_client, args=(conn,))
        thread.daemon = True
        thread.start()


def start_bridge():
    thread = threading.Thread(target=_serve)
    thread.daemon = True
    thread.start()
    return thread


if __name__ == "__main__":
    start_bridge()
    print("Bridge started. Keep this Abaqus/CAE session open.")
    if "getInput" in globals():
        getInput("Abaqus MCP bridge is running. Leave this dialog open or press Cancel to continue.")
    else:
        try:
            while True:
                threading.Event().wait(3600)
        except KeyboardInterrupt:
            sys.exit(0)
