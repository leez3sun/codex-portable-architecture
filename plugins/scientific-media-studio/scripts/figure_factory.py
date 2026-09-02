from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from studio_common import DEFAULT_PALETTE, ensure_parent, escape


def read_numeric_csv(path: str, columns: list[str]) -> dict[str, list[float]]:
    result = {column: [] for column in columns}
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header")
        missing = [column for column in columns if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing CSV columns: {', '.join(missing)}")
        for row_number, row in enumerate(reader, start=2):
            values: dict[str, float] = {}
            try:
                for column in columns:
                    values[column] = float(row[column])
            except (TypeError, ValueError):
                continue
            if all(math.isfinite(value) for value in values.values()):
                for column, value in values.items():
                    result[column].append(value)
    if not result[columns[0]]:
        raise ValueError("CSV contains no finite numeric rows for the selected columns")
    return result


def nice_ticks(low: float, high: float, count: int = 5) -> list[float]:
    if low == high:
        padding = 1.0 if low == 0 else abs(low) * 0.05
        low -= padding
        high += padding
    raw_step = (high - low) / max(count, 1)
    exponent = math.floor(math.log10(abs(raw_step))) if raw_step else 0
    fraction = raw_step / (10**exponent)
    nice_fraction = 1 if fraction <= 1 else 2 if fraction <= 2 else 2.5 if fraction <= 2.5 else 5 if fraction <= 5 else 10
    step = nice_fraction * (10**exponent)
    start = math.floor(low / step) * step
    end = math.ceil(high / step) * step
    values = []
    current = start
    for _ in range(100):
        if current > end + step * 0.25:
            break
        values.append(current)
        current += step
    return values


def fmt(value: float) -> str:
    if value == 0:
        return "0"
    if abs(value) >= 10000 or abs(value) < 0.001:
        return f"{value:.2e}"
    return f"{value:.4g}"


def build_plot(args: argparse.Namespace) -> None:
    y_columns = [part.strip() for part in args.y.split(",") if part.strip()]
    data = read_numeric_csv(args.csv, [args.x, *y_columns])
    width, height = args.width, args.height
    left, right, top, bottom = 104, 36, 64, 88
    plot_w, plot_h = width - left - right, height - top - bottom
    x_values = data[args.x]
    y_values = [value for column in y_columns for value in data[column]]
    x_ticks = nice_ticks(min(x_values), max(x_values), 6)
    y_ticks = nice_ticks(min(y_values), max(y_values), 6)
    x_min, x_max = x_ticks[0], x_ticks[-1]
    y_min, y_max = y_ticks[0], y_ticks[-1]

    def sx(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_w

    def sy(value: float) -> float:
        return top + plot_h - (value - y_min) / (y_max - y_min) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FFFFFF"/>',
        f'<text x="{left}" y="34" font-family="Arial, Helvetica, sans-serif" font-size="24" font-weight="700" fill="#101828">{escape(args.title)}</text>',
    ]
    for value in y_ticks:
        y = sy(value)
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}" stroke="#E4E7EC" stroke-width="1"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 5:.2f}" text-anchor="end" font-family="Arial" font-size="14" fill="#475467">{fmt(value)}</text>')
    for value in x_ticks:
        x = sx(value)
        parts.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}" stroke="#F2F4F7" stroke-width="1"/>')
        parts.append(f'<text x="{x:.2f}" y="{top + plot_h + 25}" text-anchor="middle" font-family="Arial" font-size="14" fill="#475467">{fmt(value)}</text>')
    parts.extend([
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#101828" stroke-width="1.5"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#101828" stroke-width="1.5"/>',
        f'<text x="{left + plot_w / 2:.2f}" y="{height - 24}" text-anchor="middle" font-family="Arial" font-size="17" fill="#101828">{escape(args.xlabel or args.x)}</text>',
        f'<text x="25" y="{top + plot_h / 2:.2f}" transform="rotate(-90 25 {top + plot_h / 2:.2f})" text-anchor="middle" font-family="Arial" font-size="17" fill="#101828">{escape(args.ylabel or ", ".join(y_columns))}</text>',
    ])
    legend_x = left + 8
    for index, column in enumerate(y_columns):
        color = DEFAULT_PALETTE[index % len(DEFAULT_PALETTE)]
        points = [(sx(x), sy(y)) for x, y in zip(data[args.x], data[column])]
        if args.kind == "line":
            path = " ".join(("M" if idx == 0 else "L") + f" {x:.2f} {y:.2f}" for idx, (x, y) in enumerate(points))
            parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
        for x, y in points:
            radius = 3.3 if args.kind == "line" else 4.4
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{color}" stroke="#FFFFFF" stroke-width="1"/>')
        item_x = legend_x + index * 160
        parts.append(f'<line x1="{item_x}" y1="{top + 14}" x2="{item_x + 28}" y2="{top + 14}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{item_x + 36}" y="{top + 19}" font-family="Arial" font-size="14" fill="#344054">{escape(column)}</text>')
    parts.append('</svg>')
    output = ensure_parent(args.output)
    output.write_text("\n".join(parts), encoding="utf-8")
    print(output)


def build_panel(args: argparse.Namespace) -> None:
    paths = [Path(item).expanduser().resolve() for item in args.inputs]
    images = [Image.open(path).convert("RGB") for path in paths]
    columns = max(1, min(args.columns, len(images)))
    rows = math.ceil(len(images) / columns)
    cell_w = args.cell_width or max(image.width for image in images)
    cell_h = args.cell_height or max(image.height for image in images)
    canvas_w = args.padding * 2 + columns * cell_w + (columns - 1) * args.gap
    canvas_h = args.padding * 2 + rows * cell_h + (rows - 1) * args.gap
    canvas = Image.new("RGB", (canvas_w, canvas_h), args.background)
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arialbd.ttf", args.label_size)
    except OSError:
        font = ImageFont.load_default()
    for index, image in enumerate(images):
        row, column = divmod(index, columns)
        scale = min(cell_w / image.width, cell_h / image.height, 1.0 if not args.allow_upscale else float("inf"))
        if math.isfinite(scale) and scale != 1.0:
            image = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.Resampling.LANCZOS)
        x = args.padding + column * (cell_w + args.gap) + (cell_w - image.width) // 2
        y = args.padding + row * (cell_h + args.gap) + (cell_h - image.height) // 2
        canvas.paste(image, (x, y))
        label = chr(ord("A") + index) if index < 26 else str(index + 1)
        draw.rounded_rectangle((x + 10, y + 10, x + 10 + args.label_size * 1.4, y + 14 + args.label_size * 1.25), radius=5, fill="white")
        draw.text((x + 18, y + 14), label, fill="#101828", font=font)
    output = ensure_parent(args.output)
    canvas.save(output, dpi=(args.dpi, args.dpi), quality=95)
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create editable scientific SVG plots and raster multi-panel figures.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    plot = subparsers.add_parser("plot")
    plot.add_argument("--csv", required=True)
    plot.add_argument("--x", required=True)
    plot.add_argument("--y", required=True, help="Comma-separated y columns")
    plot.add_argument("--kind", choices=["line", "scatter"], default="line")
    plot.add_argument("--title", default="")
    plot.add_argument("--xlabel", default="")
    plot.add_argument("--ylabel", default="")
    plot.add_argument("--width", type=int, default=960)
    plot.add_argument("--height", type=int, default=640)
    plot.add_argument("--output", required=True)
    plot.set_defaults(func=build_plot)
    panel = subparsers.add_parser("panel")
    panel.add_argument("--inputs", nargs="+", required=True)
    panel.add_argument("--columns", type=int, default=2)
    panel.add_argument("--gap", type=int, default=24)
    panel.add_argument("--padding", type=int, default=30)
    panel.add_argument("--label-size", type=int, default=34)
    panel.add_argument("--cell-width", type=int, help="Target cell width in pixels")
    panel.add_argument("--cell-height", type=int, help="Target cell height in pixels")
    panel.add_argument("--allow-upscale", action="store_true")
    panel.add_argument("--background", default="white")
    panel.add_argument("--dpi", type=int, default=300)
    panel.add_argument("--output", required=True)
    panel.set_defaults(func=build_panel)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
