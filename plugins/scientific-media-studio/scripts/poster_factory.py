from __future__ import annotations

import argparse
import base64
import mimetypes
from pathlib import Path

from studio_common import ensure_parent, escape, load_json, svg_text_lines, wrap_text


def data_uri(path: str, base: Path) -> str:
    source = (base / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    mime = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(source.read_bytes()).decode('ascii')}"


def build(spec_path: str, output_path: str) -> None:
    spec_file = Path(spec_path).expanduser().resolve()
    spec = load_json(spec_file)
    width = int(spec.get("width", 1400))
    height = int(spec.get("height", 2000))
    accent = str(spec.get("accent", "#0B6E69"))
    ink = "#101828"
    muted = "#475467"
    margin = int(spec.get("margin", 84))
    hero_w = int(width * 0.58)
    rail_x = margin + hero_w + 56
    rail_w = width - rail_x - margin
    title = str(spec.get("title", "Scientific Story"))
    subtitle = str(spec.get("subtitle", "Evidence-led visual communication"))
    sections = spec.get("sections", [])
    if not isinstance(sections, list):
        raise ValueError("sections must be a list")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#F8FAFC"/>',
        f'<rect x="0" y="0" width="24" height="{height}" fill="{escape(accent)}"/>',
        svg_text_lines(wrap_text(title, 30), margin, 120, 58, 66, ink, 760),
        svg_text_lines(wrap_text(subtitle, 62), margin, 260, 24, 34, muted, 400),
        f'<line x1="{margin}" y1="330" x2="{width-margin}" y2="330" stroke="{escape(accent)}" stroke-width="5"/>',
    ]
    hero = spec.get("hero_image")
    if hero:
        uri = data_uri(str(hero), spec_file.parent)
        parts.extend([
            f'<defs><clipPath id="heroClip"><rect x="{margin}" y="390" width="{hero_w}" height="720" rx="24"/></clipPath></defs>',
            f'<image href="{uri}" x="{margin}" y="390" width="{hero_w}" height="720" preserveAspectRatio="xMidYMid slice" clip-path="url(#heroClip)"/>',
        ])
    else:
        parts.append(f'<rect x="{margin}" y="390" width="{hero_w}" height="720" rx="24" fill="#E4E7EC"/>')
        parts.append(svg_text_lines(["Add a hero scientific image"], margin + hero_w / 2, 750, 26, 32, muted, 600, "middle"))

    y = 410
    for index, section in enumerate(sections[:4]):
        if not isinstance(section, dict):
            continue
        heading = str(section.get("heading", f"Section {index + 1}"))
        body = str(section.get("body", ""))
        parts.append(f'<text x="{rail_x}" y="{y}" font-family="Arial" font-size="18" font-weight="700" fill="{escape(accent)}">{index + 1:02d}</text>')
        parts.append(svg_text_lines(wrap_text(heading, 24), rail_x, y + 40, 29, 34, ink, 720))
        body_lines = wrap_text(body, 38)[:8]
        parts.append(svg_text_lines(body_lines, rail_x, y + 118, 18, 27, muted, 400))
        used = 145 + len(body_lines) * 27
        parts.append(f'<line x1="{rail_x}" y1="{y + used}" x2="{rail_x + rail_w}" y2="{y + used}" stroke="#D0D5DD"/>')
        y += used + 34

    lower_y = 1180
    takeaway = str(spec.get("takeaway", "State the one finding the audience should remember."))
    parts.extend([
        f'<rect x="{margin}" y="{lower_y}" width="{width-2*margin}" height="320" rx="28" fill="#FFFFFF" stroke="#D0D5DD"/>',
        f'<text x="{margin+46}" y="{lower_y+62}" font-family="Arial" font-size="17" font-weight="700" letter-spacing="2" fill="{escape(accent)}">KEY TAKEAWAY</text>',
        svg_text_lines(wrap_text(takeaway, 64)[:5], margin + 46, lower_y + 132, 35, 44, ink, 720),
    ])
    methods = str(spec.get("methods", "Methods, boundary conditions, uncertainty, and source notes."))
    source = str(spec.get("source", "Source: add DOI, dataset, simulation job, or repository URL."))
    parts.extend([
        svg_text_lines(["METHODS & PROVENANCE"], margin, 1590, 18, 24, accent, 720),
        svg_text_lines(wrap_text(methods, 96)[:5], margin, 1640, 20, 30, muted, 400),
        f'<line x1="{margin}" y1="1850" x2="{width-margin}" y2="1850" stroke="#D0D5DD"/>',
        svg_text_lines(wrap_text(source, 110)[:3], margin, 1900, 17, 25, muted, 400),
        '</svg>',
    ])
    output = ensure_parent(output_path)
    output.write_text("\n".join(parts), encoding="utf-8")
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an editable, asymmetric scientific poster as SVG.")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    build(args.spec, args.output)


if __name__ == "__main__":
    main()
