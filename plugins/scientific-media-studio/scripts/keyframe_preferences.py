from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from PIL import Image, ImageFilter, ImageStat
except ImportError as exc:  # pragma: no cover - dependency checked at runtime
    raise SystemExit("Pillow is required: install the local Scientific Media Studio runtime dependencies") from exc


SCHEMA_VERSION = "1.0"
CRITICAL_TYPES = {"colorbar", "legend", "annotation", "callout", "highlight", "caption", "timestamp"}
SCIENTIFIC_REQUIRED = ("legend_visible", "units_visible", "timestamp_meaning_visible")
DEFAULT_HARD_TAGS = {
    "colorbar:hue-clash",
    "colorbar:illegible",
    "colorbar:wrong-range",
    "colorbar:missing-units",
    "annotation:overlap-colorbar",
    "annotation:low-contrast",
    "annotation:outside-safe-area",
    "text:cropped",
    "layout:critical-overlap",
    "science:meaning-changed",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_object(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def save_object(path: str | Path, value: dict[str, Any]) -> Path:
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return target


def split_tags(value: str | Iterable[str] | None) -> list[str]:
    if value is None:
        return []
    raw = value if not isinstance(value, str) else value.split(",")
    return sorted({str(item).strip().lower() for item in raw if str(item).strip()})


def parse_region(value: str | None) -> list[float] | None:
    if not value:
        return None
    parts = [float(item.strip()) for item in value.split(",")]
    if len(parts) != 4 or any(item < 0 or item > 1 for item in parts):
        raise ValueError("region must be normalized x,y,width,height values in [0,1]")
    if parts[2] <= 0 or parts[3] <= 0 or parts[0] + parts[2] > 1 or parts[1] + parts[3] > 1:
        raise ValueError("region must have positive size and remain inside the frame")
    return parts


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pixel_values(image: Image.Image) -> list[int]:
    modern = getattr(image, "get_flattened_data", None)
    return list(modern() if modern is not None else image.getdata())


def dhash(image: Image.Image, size: int = 8) -> str:
    gray = image.convert("L").resize((size + 1, size), Image.Resampling.LANCZOS)
    pixels = pixel_values(gray)
    bits: list[bool] = []
    for y in range(size):
        row = y * (size + 1)
        bits.extend(pixels[row + x] > pixels[row + x + 1] for x in range(size))
    number = sum((1 << index) for index, bit in enumerate(bits) if bit)
    return f"{number:0{size * size // 4}x}"


def feature_vector(image_path: str | Path, region: list[float] | None = None) -> dict[str, Any]:
    source = Path(image_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    with Image.open(source) as opened:
        image = opened.convert("RGB")
        full_width, full_height = image.size
        if region:
            x, y, width, height = region
            image = image.crop((
                round(x * full_width), round(y * full_height),
                round((x + width) * full_width), round((y + height) * full_height),
            ))
        sample = image.resize((96, 96), Image.Resampling.LANCZOS)
        hsv = sample.convert("HSV")
        gray = sample.convert("L")
        rgb_mean = ImageStat.Stat(sample).mean[:3]
        luma_values = pixel_values(gray)
        saturation_values = pixel_values(hsv.getchannel("S"))
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_values = pixel_values(edges)
        hue_values = pixel_values(hsv.getchannel("H"))
        hue_hist = [0] * 12
        for hue, saturation in zip(hue_values, saturation_values):
            if saturation >= 24:
                hue_hist[min(11, int(hue * 12 / 256))] += 1
        hue_total = sum(hue_hist) or 1
        return {
            "source_width": full_width,
            "source_height": full_height,
            "aspect_ratio": round(full_width / full_height, 6),
            "rgb_mean": [round(value / 255, 6) for value in rgb_mean],
            "luma_mean": round(statistics.fmean(luma_values) / 255, 6),
            "luma_std": round(statistics.pstdev(luma_values) / 255, 6),
            "saturation_mean": round(statistics.fmean(saturation_values) / 255, 6),
            "edge_density": round(sum(value >= 36 for value in edge_values) / len(edge_values), 6),
            "dark_fraction": round(sum(value <= 32 for value in luma_values) / len(luma_values), 6),
            "bright_fraction": round(sum(value >= 224 for value in luma_values) / len(luma_values), 6),
            "hue_histogram": [round(value / hue_total, 6) for value in hue_hist],
            "dhash": dhash(sample),
        }


def hamming_similarity(left: str, right: str) -> float:
    try:
        left_value, right_value = int(left, 16), int(right, 16)
    except (TypeError, ValueError):
        return 0.0
    bits = max(len(left), len(right)) * 4
    return 1 - ((left_value ^ right_value).bit_count() / max(bits, 1))


def numeric_similarity(left: dict[str, Any], right: dict[str, Any]) -> float:
    fields = ("luma_mean", "luma_std", "saturation_mean", "edge_density", "dark_fraction", "bright_fraction")
    distances = [abs(float(left.get(key, 0)) - float(right.get(key, 0))) for key in fields]
    rgb_distance = math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(left.get("rgb_mean", [0, 0, 0]), right.get("rgb_mean", [0, 0, 0])))) / math.sqrt(3)
    hist_distance = sum(abs(float(a) - float(b)) for a, b in zip(left.get("hue_histogram", []), right.get("hue_histogram", []))) / 2
    return max(0.0, 1 - (statistics.fmean([*distances, rgb_distance, hist_distance])))


def visual_similarity(left: dict[str, Any], right: dict[str, Any]) -> float:
    return round(0.45 * hamming_similarity(str(left.get("dhash", "")), str(right.get("dhash", ""))) + 0.55 * numeric_similarity(left, right), 6)


def default_profile(project: str) -> dict[str, Any]:
    timestamp = now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "project": project,
        "created_at": timestamp,
        "updated_at": timestamp,
        "policy": {
            "max_iterations": 4,
            "minimum_pass_score": 82,
            "safe_margin_ratio": 0.035,
            "critical_overlap_ratio": 0.02,
            "negative_similarity_warning": 0.82,
            "positive_similarity_bonus_floor": 0.72,
            "require_scientific_manifest": True,
            "preserve_positive_animation": True,
        },
        "hard_block_tags": sorted(DEFAULT_HARD_TAGS),
        "preferred_tags": {},
        "learned_block_tags": {},
        "examples": [],
        "decisions": [],
    }


def increment_map(mapping: dict[str, Any], tags: Iterable[str], amount: float) -> None:
    for tag in tags:
        mapping[tag] = round(float(mapping.get(tag, 0)) + amount, 3)


def add_feedback(profile: dict[str, Any], frame_path: str, sentiment: str, weight: int, tags: list[str], notes: str, region: list[float] | None, timestamp_seconds: float | None) -> dict[str, Any]:
    source = Path(frame_path).expanduser().resolve()
    features = feature_vector(source, region)
    item = {
        "id": f"example-{len(profile.get('examples', [])) + 1:04d}",
        "sentiment": sentiment,
        "weight": weight,
        "frame_path": str(source),
        "frame_sha256": sha256_file(source),
        "timestamp_seconds": timestamp_seconds,
        "region": region,
        "tags": tags,
        "notes": notes,
        "features": features,
        "created_at": now_iso(),
    }
    profile.setdefault("examples", []).append(item)
    if sentiment == "positive":
        increment_map(profile.setdefault("preferred_tags", {}), tags, weight)
    else:
        increment_map(profile.setdefault("learned_block_tags", {}), tags, weight)
        # A concrete negative cause is a hard rule. Generic labels are warnings only.
        concrete = {tag for tag in tags if ":" in tag and not tag.startswith("style:")}
        profile["hard_block_tags"] = sorted(set(profile.get("hard_block_tags", [])) | concrete)
    profile["updated_at"] = now_iso()
    return item


def relative_bbox(component: dict[str, Any], width: float, height: float) -> tuple[float, float, float, float] | None:
    bbox = component.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 4:
        return None
    x, y, w, h = (float(value) for value in bbox)
    if max(abs(x), abs(y), abs(w), abs(h)) > 1:
        if width <= 0 or height <= 0:
            return None
        x, y, w, h = x / width, y / height, w / width, h / height
    return x, y, w, h


def overlap_ratio(left: tuple[float, float, float, float], right: tuple[float, float, float, float]) -> float:
    lx, ly, lw, lh = left
    rx, ry, rw, rh = right
    intersection = max(0, min(lx + lw, rx + rw) - max(lx, rx)) * max(0, min(ly + lh, ry + rh) - max(ly, ry))
    return intersection / max(min(lw * lh, rw * rh), 1e-9)


def hex_rgb(value: str) -> tuple[float, float, float] | None:
    text = str(value).strip().lstrip("#")
    if len(text) == 3:
        text = "".join(char * 2 for char in text)
    if len(text) != 6:
        return None
    try:
        return tuple(int(text[index:index + 2], 16) / 255 for index in (0, 2, 4))  # type: ignore[return-value]
    except ValueError:
        return None


def contrast_ratio(foreground: str, background: str) -> float | None:
    def luminance(rgb: tuple[float, float, float]) -> float:
        channels = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in rgb]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
    fg, bg = hex_rgb(foreground), hex_rgb(background)
    if fg is None or bg is None:
        return None
    bright, dark = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (bright + 0.05) / (dark + 0.05)


def manifest_checks(manifest: dict[str, Any], profile: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    policy = profile.get("policy", {})
    frame = manifest.get("frame", {})
    width, height = float(frame.get("width", 1)), float(frame.get("height", 1))
    margin = float(policy.get("safe_margin_ratio", 0.035))
    components = manifest.get("components", []) if isinstance(manifest.get("components", []), list) else []
    normalized: list[tuple[dict[str, Any], tuple[float, float, float, float]]] = []
    for component in components:
        if not isinstance(component, dict):
            continue
        bbox = relative_bbox(component, width, height)
        if bbox is None:
            warnings.append({"code": "component:missing-bbox", "component": component.get("id"), "message": "组件缺少可验证的 bbox"})
            continue
        normalized.append((component, bbox))
        x, y, w, h = bbox
        if x < margin or y < margin or x + w > 1 - margin or y + h > 1 - margin:
            severity = "blocker" if str(component.get("type", "")).lower() in CRITICAL_TYPES else "warning"
            issue = {"code": "annotation:outside-safe-area", "component": component.get("id"), "message": "关键组件超出安全边距"}
            (blockers if severity == "blocker" else warnings).append(issue)
        ratio = contrast_ratio(str(component.get("foreground", "")), str(component.get("background", "")))
        if ratio is not None and ratio < 4.5 and str(component.get("type", "")).lower() in {"annotation", "callout", "caption", "timestamp", "text"}:
            blockers.append({"code": "annotation:low-contrast", "component": component.get("id"), "value": round(ratio, 2), "message": "文字对比度低于 4.5:1"})
    for index, (left, left_bbox) in enumerate(normalized):
        for right, right_bbox in normalized[index + 1:]:
            left_type, right_type = str(left.get("type", "")).lower(), str(right.get("type", "")).lower()
            if {left_type, right_type} & {"colorbar", "legend"} and {left_type, right_type} & {"annotation", "callout", "highlight", "caption", "text"}:
                ratio = overlap_ratio(left_bbox, right_bbox)
                if ratio > float(policy.get("critical_overlap_ratio", 0.02)):
                    blockers.append({"code": "annotation:overlap-colorbar", "components": [left.get("id"), right.get("id")], "value": round(ratio, 4), "message": "注释或高亮与色标/图例重叠"})
    scientific = manifest.get("scientific")
    if policy.get("require_scientific_manifest", True) and not isinstance(scientific, dict):
        blockers.append({"code": "science:missing-manifest", "message": "缺少科学含义核验清单"})
    elif isinstance(scientific, dict):
        for field in SCIENTIFIC_REQUIRED:
            if scientific.get(field) is not True:
                blockers.append({"code": f"science:{field}", "message": f"科学核验项未通过: {field}"})
        if scientific.get("solver_frame_modified") is True:
            blockers.append({"code": "science:meaning-changed", "message": "求解器画面被标记为可能改变数据含义"})
    return blockers, warnings


def relevant_examples(profile: dict[str, Any], observed_tags: set[str], sentiment: str) -> list[dict[str, Any]]:
    examples = [item for item in profile.get("examples", []) if item.get("sentiment") == sentiment]
    # A visual score is only meaningful inside the same explicitly tagged component context.
    # Falling back to unrelated examples would punish a new simulation state for looking different.
    return [item for item in examples if observed_tags.intersection(item.get("tags", []))]


def score_candidate(profile: dict[str, Any], frame_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
    features = feature_vector(frame_path)
    observed_tags = set(split_tags(manifest.get("observed_tags", [])))
    blockers, warnings = manifest_checks(manifest, profile)
    hard_tags = set(profile.get("hard_block_tags", []))
    for tag in sorted(observed_tags & hard_tags):
        blockers.append({"code": tag, "message": f"候选帧命中已学习的禁止项: {tag}"})
    positive = relevant_examples(profile, observed_tags, "positive")
    negative = relevant_examples(profile, observed_tags, "negative")
    positive_similarity = max((visual_similarity(features, item.get("features", {})) for item in positive), default=0.0)
    negative_similarity = max((visual_similarity(features, item.get("features", {})) for item in negative), default=0.0)
    threshold = float(profile.get("policy", {}).get("negative_similarity_warning", 0.82))
    if negative_similarity >= threshold:
        warnings.append({"code": "style:negative-similarity", "value": negative_similarity, "message": "画面与负样例整体视觉相近；需人工确认具体原因，不能仅凭相似度封禁"})
    preferred = profile.get("preferred_tags", {})
    positive_tag_bonus = min(10.0, sum(float(preferred.get(tag, 0)) for tag in observed_tags) * 1.5)
    score = 78 + 12 * positive_similarity - 10 * negative_similarity + positive_tag_bonus - 3 * len(warnings)
    if blockers:
        score = min(score, 49)
    score = round(max(0, min(100, score)), 2)
    minimum = float(profile.get("policy", {}).get("minimum_pass_score", 82))
    return {
        "schema_version": SCHEMA_VERSION,
        "frame_path": str(Path(frame_path).expanduser().resolve()),
        "profile_project": profile.get("project", ""),
        "created_at": now_iso(),
        "status": "pass" if not blockers and score >= minimum else "revise",
        "score": score,
        "minimum_pass_score": minimum,
        "positive_similarity": positive_similarity,
        "negative_similarity": negative_similarity,
        "positive_tag_bonus": round(positive_tag_bonus, 2),
        "observed_tags": sorted(observed_tags),
        "blockers": blockers,
        "warnings": warnings,
        "revision_actions": revision_actions(blockers, warnings),
        "features": features,
    }


def revision_actions(blockers: list[dict[str, Any]], warnings: list[dict[str, Any]]) -> list[str]:
    lookup = {
        "annotation:overlap-colorbar": "移动或缩放注释/高亮框，保留色标与单位的完整可读区域。",
        "annotation:outside-safe-area": "将关键组件移入安全边距；在 Remotion Studio 中拖拽后写回内联样式。",
        "annotation:low-contrast": "调整注释文字或底色，使正文对比度至少达到 4.5:1。",
        "colorbar:hue-clash": "保持数据色映射不变，改用中性色容器和非竞争色的注释系统；必要时从 Abaqus 重新导出。",
        "science:missing-manifest": "补充图例、单位、时间含义、变形比例和求解器画面真实性清单。",
        "science:meaning-changed": "撤销改变云图数值映射或求解器含义的处理，重新导出正确画面。",
        "style:negative-similarity": "对照负样例的区域标签确认原因，不要机械复刻或机械否决整帧。",
    }
    actions: list[str] = []
    for issue in [*blockers, *warnings]:
        code = str(issue.get("code", ""))
        action = lookup.get(code)
        if action is None and code.startswith("science:"):
            action = "恢复并验证图例、单位、时间、边界条件或变形比例等科学信息。"
        if action is None and ":" in code:
            action = f"消除已标记问题 `{code}`，重新渲染该代表帧后再评分。"
        if action and action not in actions:
            actions.append(action)
    return actions


def build_plan(profile: dict[str, Any], reports: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [report for report in reports if report.get("status") != "pass"]
    actions: list[str] = []
    for report in failed:
        for action in report.get("revision_actions", []):
            if action not in actions:
                actions.append(action)
    return {
        "schema_version": SCHEMA_VERSION,
        "project": profile.get("project", ""),
        "created_at": now_iso(),
        "all_keyframes_pass": not failed,
        "passed": len(reports) - len(failed),
        "total": len(reports),
        "next_action": "render_full_video" if not failed else "revise_components_and_rerender_stills",
        "iteration_limit": profile.get("policy", {}).get("max_iterations", 4),
        "preserve": [tag for tag, weight in profile.get("preferred_tags", {}).items() if float(weight) > 0],
        "hard_blocks": profile.get("hard_block_tags", []),
        "revision_actions": actions,
        "failed_frames": [{"frame_path": item.get("frame_path"), "score": item.get("score"), "blockers": item.get("blockers", [])} for item in failed],
    }


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Learn and enforce interpretable keyframe preferences for scientific video.")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create a preference profile")
    init.add_argument("--project", required=True)
    init.add_argument("--output", required=True)
    add = sub.add_parser("add", help="Add positive or negative frame feedback")
    add.add_argument("--profile", required=True)
    add.add_argument("--frame", required=True)
    add.add_argument("--sentiment", choices=("positive", "negative"), required=True)
    add.add_argument("--weight", type=int, choices=(1, 2), default=1)
    add.add_argument("--tags", default="")
    add.add_argument("--notes", default="")
    add.add_argument("--region", help="Normalized x,y,width,height")
    add.add_argument("--timestamp", type=float)
    score = sub.add_parser("score", help="Score a candidate keyframe")
    score.add_argument("--profile", required=True)
    score.add_argument("--frame", required=True)
    score.add_argument("--manifest", required=True)
    score.add_argument("--output", required=True)
    plan = sub.add_parser("plan", help="Combine score reports into a revision plan")
    plan.add_argument("--profile", required=True)
    plan.add_argument("--reports", nargs="+", required=True)
    plan.add_argument("--output", required=True)
    return parser


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = make_parser().parse_args()
    if args.command == "init":
        target = save_object(args.output, default_profile(args.project))
        print(json.dumps({"profile": str(target), "status": "created"}, ensure_ascii=False))
        return
    profile = load_object(args.profile)
    if args.command == "add":
        item = add_feedback(profile, args.frame, args.sentiment, args.weight, split_tags(args.tags), args.notes, parse_region(args.region), args.timestamp)
        target = save_object(args.profile, profile)
        print(json.dumps({"profile": str(target), "example": item["id"], "hard_block_tags": profile["hard_block_tags"]}, ensure_ascii=False))
        return
    if args.command == "score":
        report = score_candidate(profile, args.frame, load_object(args.manifest))
        target = save_object(args.output, report)
        print(json.dumps({"report": str(target), "status": report["status"], "score": report["score"]}, ensure_ascii=False))
        return
    reports = [load_object(path) for path in args.reports]
    plan = build_plan(profile, reports)
    target = save_object(args.output, plan)
    print(json.dumps({"plan": str(target), "all_keyframes_pass": plan["all_keyframes_pass"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
