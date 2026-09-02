---
name: abaqus-cae
description: Use local Abaqus/CAE through MCP to inspect the installation, execute CAE Python modeling scripts, or create a billiard collision simulation.
---

# Abaqus/CAE

Use `abaqus_environment` first when installation status is unknown. Use `abaqus_create_billiards` for the collision example and `abaqus_create_pool_game` for the visual 2.5D table game with six pockets and 3D balls. The `project_dir` must be a path that does not exist. Never open, import, overwrite, save, rename, delete, or otherwise modify any pre-existing `.cae` file or CAE project. If a requested output path exists, stop and choose a new project name. Report only newly generated `.cae`, `.inp`, job, and result paths.
