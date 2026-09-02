---
name: ansys-workbench
description: Use local ANSYS Workbench and Mechanical through reviewed MCP journal, queue, socket, meshing, solve, and result-extraction workflows.
---

# ANSYS Workbench

1. Start with `workbench_detect_tool` and `mechanical_readiness_tool`.
2. For a live Mechanical session, call `workbench_queue_install_info_tool` and follow the returned ACT/bridge installation guidance from `server/README.zh-CN.md`.
3. Prefer inventory and validation tools before operations that launch Workbench, change a model, mesh, solve, or export files.
4. Run only journals or Python supplied by the user or reviewed in the current task. Keep generated jobs in new output folders and preserve source projects.
5. Use the job/status/log tools for long-running work rather than repeatedly launching duplicate jobs.
6. Report the detected ANSYS release, bridge transport, job identifier, output paths, and any incomplete prerequisites.

The packaged server source and detailed ACT setup instructions are under `server/`.
