@echo off
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-mcp.ps1"
exit /b %errorlevel%
