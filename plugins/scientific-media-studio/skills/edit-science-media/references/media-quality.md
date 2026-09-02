# Media quality gate

- Probe source and output with FFprobe.
- Preserve aspect ratio unless cropping is explicit.
- Preserve scientific overlays, legends, units, timestamps, and frame meaning.
- Record whether frame-rate conversion duplicates, drops, or interpolates frames.
- Prefer H.264, yuv420p, AAC, and faststart for broadly compatible MP4 delivery.
- Use CRF-based encoding for quality-controlled local masters; retain lossless originals.
- Check opening, midpoint, maximum-response, and ending frames.
- Confirm audio presence, loudness intent, subtitle timing, duration, resolution, and codec.
