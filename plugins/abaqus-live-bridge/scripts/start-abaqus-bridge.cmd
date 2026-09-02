@echo off
setlocal
where abaqus >nul 2>nul
if errorlevel 1 (
  echo Abaqus command was not found. Add the SIMULIA Commands folder to PATH or run the bridge from Abaqus/CAE with File ^> Run Script.
  exit /b 1
)
abaqus cae noGUI="%~dp0abaqus_mcp_bridge.py"
