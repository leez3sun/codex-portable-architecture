---
name: design-science-poster
description: Design editable scientific posters, graphical abstracts, research infographics, social-media science graphics, and conference visual summaries as SVG. Use when a layout needs an original editorial visual system, a strong hero result, scientific provenance, non-repetitive composition, or adaptation across print and screen formats.
---

# Design Science Poster

## Procedure

1. Define one audience, one communication objective, and one central takeaway.
2. Complete cross-platform reference research and extract principles rather than copying surface style.
3. Propose three structurally different concepts; reject generic card grids and template replacement.
4. Build an asymmetric editorial layout with a hero visual, evidence rail, takeaway, and provenance zone.
5. Generate editable SVG with `../../scripts/poster_factory.py` from a JSON spec.
6. Inspect typography, reading order, contrast, image cropping, units, legends, and print/screen dimensions.
7. Keep a source manifest for every figure, icon, image, and claim.

Example:

```powershell
python ../../scripts/poster_factory.py --spec poster.json --output poster.svg
```

Start from `../../assets/poster-spec.example.json`. Read [references/poster-quality.md](references/poster-quality.md) before delivery.
