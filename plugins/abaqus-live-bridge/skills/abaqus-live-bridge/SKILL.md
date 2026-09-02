---
name: abaqus-live-bridge
description: Use a localhost-only MCP bridge to inspect or execute explicitly reviewed Python in an already running Abaqus/CAE session.
---

# Abaqus Live Bridge

Use this skill only when the user wants to work with the currently open Abaqus/CAE kernel rather than create a separate no-GUI job.

1. Ask the user to open Abaqus/CAE and run `scripts/abaqus_mcp_bridge.py` through **File > Run Script**. The bridge listens only on `127.0.0.1:50001` by default.
2. Call `abaqus_status` before any execution.
3. Treat `abaqus_exec` and `abaqus_eval` as direct code execution in the user's live CAE session. Show or summarize the exact code and obtain any confirmation required for destructive model changes, job deletion, overwrite, or external file writes.
4. Prefer read-only inspection first. Never broaden the bridge to a non-loopback address.
5. Report the active model/session context and any files changed.
