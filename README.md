# Codex Portable Architecture

Portable backup and migration bundle for the local Codex skills, personal plugins, and MCP servers inventoried on 2026-09-02.

For the full Chinese installation and security guide, see [README.zh-CN.md](README.zh-CN.md).

Quick install after downloading and extracting the release ZIP on the destination Windows PC:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\Install-CodexPortable.ps1 -InstallDependencies
```

The bundle never contains Codex authentication, browser profiles, cookies, sessions, memories, logs, API keys, ANSYS/Abaqus binaries, solver results, or Python virtual environments.
