from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from studio_common import ensure_parent, resolve_executable


def run(command: list[str], dry_run: bool = False) -> None:
    print(json.dumps(command, ensure_ascii=False))
    if not dry_run:
        subprocess.run(command, check=True)


def probe(args: argparse.Namespace) -> None:
    command = [
        resolve_executable("ffprobe"), "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(Path(args.input).resolve()),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    data = json.loads(result.stdout)
    if args.output:
        output = ensure_parent(args.output)
        output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(output)
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


def transcode(args: argparse.Namespace) -> None:
    output = ensure_parent(args.output)
    filters: list[str] = []
    if args.width or args.height:
        width = args.width if args.width else -2
        height = args.height if args.height else -2
        filters.append(f"scale={width}:{height}:force_original_aspect_ratio=decrease")
        filters.append("pad=ceil(iw/2)*2:ceil(ih/2)*2")
    if args.fps:
        filters.append(f"fps={args.fps}")
    if args.burn_subtitles:
        escaped = str(Path(args.burn_subtitles).resolve()).replace("\\", "/").replace(":", "\\:")
        filters.append(f"subtitles='{escaped}'")
    command = [resolve_executable("ffmpeg"), "-y", "-i", str(Path(args.input).resolve())]
    if filters:
        command.extend(["-vf", ",".join(filters)])
    command.extend([
        "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", args.audio_bitrate, str(output),
    ])
    run(command, args.dry_run)


def thumbnail(args: argparse.Namespace) -> None:
    output = ensure_parent(args.output)
    command = [
        resolve_executable("ffmpeg"), "-y", "-ss", str(args.time), "-i", str(Path(args.input).resolve()),
        "-frames:v", "1", "-update", "1", "-q:v", "2", str(output),
    ]
    run(command, args.dry_run)


def extract_frames(args: argparse.Namespace) -> None:
    output_pattern = ensure_parent(args.output_pattern)
    command = [resolve_executable("ffmpeg"), "-y", "-i", str(Path(args.input).resolve())]
    if args.fps:
        command.extend(["-vf", f"fps={args.fps}"])
    command.append(str(output_pattern))
    run(command, args.dry_run)


def concat(args: argparse.Namespace) -> None:
    inputs = [Path(item).resolve() for item in args.inputs]
    list_path = ensure_parent(args.list_file or Path(args.output).with_suffix(".concat.txt"))
    list_path.write_text("\n".join(f"file '{str(path).replace("'", "'\\''")}'" for path in inputs), encoding="utf-8")
    output = ensure_parent(args.output)
    if args.reencode:
        command = [resolve_executable("ffmpeg"), "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c:v", "libx264", "-crf", str(args.crf), "-c:a", "aac", str(output)]
    else:
        command = [resolve_executable("ffmpeg"), "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c", "copy", str(output)]
    run(command, args.dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Non-destructive local FFmpeg/FFprobe operations for scientific media.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("probe")
    p.add_argument("--input", required=True)
    p.add_argument("--output")
    p.set_defaults(func=probe)
    t = sub.add_parser("transcode")
    t.add_argument("--input", required=True)
    t.add_argument("--output", required=True)
    t.add_argument("--width", type=int)
    t.add_argument("--height", type=int)
    t.add_argument("--fps", type=float)
    t.add_argument("--crf", type=int, default=18)
    t.add_argument("--preset", default="medium")
    t.add_argument("--audio-bitrate", default="192k")
    t.add_argument("--burn-subtitles")
    t.add_argument("--dry-run", action="store_true")
    t.set_defaults(func=transcode)
    thumb = sub.add_parser("thumbnail")
    thumb.add_argument("--input", required=True)
    thumb.add_argument("--time", type=float, default=0)
    thumb.add_argument("--output", required=True)
    thumb.add_argument("--dry-run", action="store_true")
    thumb.set_defaults(func=thumbnail)
    frames = sub.add_parser("frames")
    frames.add_argument("--input", required=True)
    frames.add_argument("--output-pattern", required=True)
    frames.add_argument("--fps", type=float)
    frames.add_argument("--dry-run", action="store_true")
    frames.set_defaults(func=extract_frames)
    join = sub.add_parser("concat")
    join.add_argument("--inputs", nargs="+", required=True)
    join.add_argument("--output", required=True)
    join.add_argument("--list-file")
    join.add_argument("--reencode", action="store_true")
    join.add_argument("--crf", type=int, default=18)
    join.add_argument("--dry-run", action="store_true")
    join.set_defaults(func=concat)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
