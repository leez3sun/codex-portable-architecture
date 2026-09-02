from __future__ import annotations

import importlib
import json
import platform
import sys

from studio_common import resolve_executable


def main() -> None:
    report: dict[str, object] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "modules": {},
        "executables": {},
    }
    for name in ["PIL", "numpy", "pandas"]:
        try:
            module = importlib.import_module(name)
            report["modules"][name] = {"available": True, "version": getattr(module, "__version__", "unknown")}
        except Exception as exc:
            report["modules"][name] = {"available": False, "error": str(exc)}
    for name in ["ffmpeg", "ffprobe", "node"]:
        try:
            report["executables"][name] = {"available": True, "path": resolve_executable(name)}
        except Exception as exc:
            report["executables"][name] = {"available": False, "error": str(exc)}
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
