---
name: ansys-fluent
description: Use the local ANSYS 2024 R1 installation through controlled MCP tools to diagnose Fluent, license, SpaceClaim/SolidWorks import, Fluent Meshing, PyFluent, and reviewed journal workflows. Trigger for ANSYS Fluent setup, water-cooling CFD, water-jacket simulation, local ANSYS automation, or ANSYS MCP requests.
---

# Local ANSYS Fluent

Use this skill for the locally installed ANSYS release detected by the plugin launcher. If auto-detection fails, set `ANSYS_ROOT` to the machine's `ANSYS Inc\v###` directory before starting Codex.

## Routing

1. Call `ansys_environment` before claiming the installation is ready.
2. Call `ansys_license_features` when a Fluent, SpaceClaim, CAD translator, or meshing launch fails.
3. Call both smoke tests before starting a new automated CFD project:
   - `fluent_solver_smoke_test`
   - `fluent_meshing_smoke_test`
4. Use `list_cad_models` to inventory project inputs without changing them.
5. Use `spaceclaim_open_model` only when the user wants a supplied CAD model opened in the local GUI. This does not prove that a fluid volume has been extracted.
6. Use `fluent_run_journal` only for a reviewed journal inside its stated working directory. The tool refuses journals outside that directory.

## Local compatibility notes

- The installed bridge is PyFluent 0.17.1 under ANSYS's Python 3.10 and matches Fluent 2024 R1.
- Run ANSYS automation from an ASCII-only working directory. Old PyFluent emits invalid UTF-8 warnings when the working path contains Chinese characters.
- SolidWorks MCP is not required for importing `.sldprt` into SpaceClaim. Use it only for parametric feature editing inside SolidWorks.
- Ordinary constant wall-temperature water cooling needs no Fortran or UDF.
- Never describe generated plots or estimates as solver results. Preserve units, boundary conditions, convergence evidence, and source paths.

## Water-jacket workflow

For water-jacket CFD, keep the stages explicit:

1. Import and repair CAD in SpaceClaim.
2. Extract and verify the closed water volume.
3. Name inlet, outlet, hot wall, other walls, and fluid body.
4. Generate and quality-check the mesh in Fluent Meshing.
5. Configure energy, water properties, turbulence, inlet flow/temperature, outlet pressure, and thermal boundary conditions.
6. Solve to residual and monitor convergence.
7. Export outlet mass-weighted temperature, pressure drop, velocity/temperature/pressure contours, streamlines, and convergence histories.

Do not infer that a `.sldprt` opened successfully means its internal fluid domain is automatically valid.
