---
name: edit-science-media
description: Inspect and edit scientific images and videos locally using deterministic Pillow and FFmpeg workflows. Use for probing codecs, extracting frames, thumbnails, resizing, transcoding, concatenation, subtitle burning, panel composition, delivery optimization, and verification of simulation media without altering source evidence.
---

# Edit Science Media

## Procedure

1. Preserve the source file and probe it before editing.
2. State the intended transformation, output format, dimensions, frame rate, codec, and scientific invariants.
3. Use `../../scripts/media_pipeline.py` for FFprobe and FFmpeg operations.
4. Use `../../scripts/figure_factory.py panel` for labeled raster panels.
5. Write to a new path; never silently overwrite the source.
6. Probe the output and compare duration, dimensions, frame rate, audio streams, and codec against the target.
7. Preview representative frames, including the opening, midpoint, maximum response, and ending.

Common commands:

```powershell
python ../../scripts/media_pipeline.py probe --input result.mp4 --output result.probe.json
python ../../scripts/media_pipeline.py transcode --input result.mp4 --output result_delivery.mp4 --width 1920 --fps 30 --crf 18
python ../../scripts/media_pipeline.py thumbnail --input result.mp4 --time 2.5 --output preview.jpg
```

Read [references/media-quality.md](references/media-quality.md) for scientific and delivery QA.
