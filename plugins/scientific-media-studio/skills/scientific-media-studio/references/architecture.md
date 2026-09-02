# Architecture

Use four layers:

1. Evidence: source data, Abaqus exports, papers, images, and provenance manifests.
2. Deterministic transforms: local Python, SVG, Pillow, FFmpeg, and FFprobe scripts.
3. Creative composition: native SVG/HTML, PowerPoint, or Remotion components.
4. Quality gates: visual previews, metadata inspection, scientific invariants, and delivery checks.

Keep fragile creative judgment in Skills. Expose only stable deterministic actions through the local MCP: environment checks, SVG plots, panel composition, poster rendering, media probing, thumbnail extraction, and controlled transcoding. Never add an arbitrary shell or arbitrary Python execution tool.
