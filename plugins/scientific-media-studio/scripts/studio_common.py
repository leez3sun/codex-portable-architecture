from __future__ import annotations

import glob
import html
import json
import os
import shutil
from pathlib import Path
from typing import Iterable


DEFAULT_PALETTE = ["#0B6E69", "#D97706", "#2563EB", "#B42318", "#6B5DD3", "#475467"]


def ensure_parent(path: str | Path) -> Path:
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


def wrap_text(text: str, max_chars: int) -> list[str]:
    words = str(text).replace("\n", " \n ").split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        if word == "\n":
            lines.append(" ".join(current))
            current = []
            continue
        candidate = " ".join([*current, word])
        if current and len(candidate) > max_chars:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines or [""]


def resolve_executable(name: str) -> str:
    direct = shutil.which(name)
    if direct:
        return direct
    if os.name == "nt" and name.lower() in {"ffmpeg", "ffprobe"}:
        local = os.environ.get("LOCALAPPDATA", "")
        patterns = [
            os.path.join(local, "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg_*", "ffmpeg-*-full_build", "bin", f"{name}.exe"),
            os.path.join(local, "Microsoft", "WinGet", "Links", f"{name}.exe"),
        ]
        matches: list[str] = []
        for pattern in patterns:
            matches.extend(glob.glob(pattern))
        if matches:
            return sorted(matches)[-1]
    raise FileNotFoundError(f"Required executable not found: {name}")


def svg_text_lines(
    lines: Iterable[str],
    x: float,
    y: float,
    font_size: float,
    line_height: float,
    fill: str = "#101828",
    weight: int = 400,
    anchor: str = "start",
) -> str:
    spans = []
    for index, line in enumerate(lines):
        spans.append(
            f'<tspan x="{x:.2f}" dy="{0 if index == 0 else line_height:.2f}">{escape(line)}</tspan>'
        )
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{font_size:.2f}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}">{"".join(spans)}</text>'
    )
