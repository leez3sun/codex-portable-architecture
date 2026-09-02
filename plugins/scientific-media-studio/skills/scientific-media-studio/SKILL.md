---
name: scientific-media-studio
description: Route local, zero-subscription production of scientific figures, multi-panel images, graphical abstracts, posters, image edits, video edits, and simulation explainers. Use for broad or mixed scientific-media requests, especially when a task spans data, figures, layouts, captions, animation, FFmpeg, Remotion, or delivery QA.
---

# Scientific Media Studio

Route the request to the smallest focused skill set:

| Need | Primary skill |
|---|---|
| Quantitative plots, multi-panel figures, figure QA | `create-sci-figures` |
| Posters, graphical abstracts, visual summaries | `design-science-poster` |
| Crop, composite, transcode, subtitle, inspect media | `edit-science-media` |
| Storyboard and produce a simulation explainer | `build-science-video` |
| Learn from liked/disliked keyframes and automate frame revision | `learn-video-preferences` |

## Workflow

1. Inspect source files and record provenance, units, dimensions, color space, and transformation history.
2. Complete the repository internet-first research gate for non-trivial creative work.
3. Propose three distinct directions when visual or narrative judgment is material.
4. Choose a direction using scientific accuracy, clarity, originality, reproducibility, and maintenance cost.
5. Use local scripts under `../../scripts/` for deterministic operations.
6. Preserve originals; write outputs to a new explicit destination.
7. Run representative visual checks and technical QA before delivery.

Run `python ../../scripts/doctor.py` when local dependencies are uncertain. Read [references/architecture.md](references/architecture.md) when extending the plugin or deciding whether to add an MCP layer.

## Non-negotiable rules

- Do not invent data, results, units, citations, solver frames, or uncertainty.
- Do not use paid plugins, purchased credits, or uncertain-cost services.
- Do not treat AI-generated or interpolated imagery as solver output.
- Do not copy a creator's recognizable style or copyrighted assets.
- Prefer editable vector deliverables for charts, diagrams, and posters.
