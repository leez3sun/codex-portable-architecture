# Abaqus Live Bridge

This plugin connects Codex to the Python kernel of an already running Abaqus/CAE session.

Open Abaqus/CAE and run `scripts/abaqus_mcp_bridge.py` with **File > Run Script**. Keep Abaqus/CAE open while using the plugin. The bridge binds to `127.0.0.1:50001`; override the MCP-side host or port with `ABAQUS_BRIDGE_HOST` and `ABAQUS_BRIDGE_PORT` only when required.

The bridge exposes arbitrary Python execution in the live CAE process. Keep it local, review code before execution, and close Abaqus/CAE when finished.
