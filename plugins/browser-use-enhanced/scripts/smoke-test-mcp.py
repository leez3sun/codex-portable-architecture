import asyncio
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    plugin_root = Path(__file__).resolve().parent.parent
    runtime_base = Path(os.environ.get("CODEX_PORTABLE_RUNTIME_ROOT", Path(os.environ["LOCALAPPDATA"]) / "CodexPortable" / "runtimes"))
    state_base = Path(os.environ.get("CODEX_PORTABLE_STATE_ROOT", Path(os.environ["LOCALAPPDATA"]) / "CodexPortable" / "state"))
    runtime_root = runtime_base / "browser-use-enhanced"
    state_root = state_base / "browser-use-enhanced"
    env = dict(os.environ)
    env.update(
        {
            "BH_HOME": str(state_root),
            "BH_AGENT_WORKSPACE": str(state_root / "agent-workspace"),
            "XDG_CONFIG_HOME": str(state_root / "config"),
            "XDG_CACHE_HOME": str(state_root / "cache"),
            "BROWSER_USE_CONFIG_DIR": str(state_root / "config" / "browseruse"),
            "ANONYMIZED_TELEMETRY": "false",
            "BROWSER_USE_CLOUD_SYNC": "false",
            "BROWSER_USE_VERSION_CHECK": "false",
            "BROWSER_USE_LOGGING_LEVEL": "critical",
            "BROWSER_USE_SETUP_LOGGING": "false",
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        }
    )
    server = StdioServerParameters(
        command=str(runtime_root / ".venv" / "Scripts" / "browser-use.exe"),
        args=["--cli-mcp"],
        env=env,
    )
    async with stdio_client(server) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("MCP_OK")
            for tool in tools.tools:
                print(tool.name)


if __name__ == "__main__":
    asyncio.run(main())
