---
name: create-sci-figures
description: Create and edit publication-ready scientific plots, Abaqus result charts, comparison figures, ablation plots, and labeled multi-panel figures from CSV data or raster images. Use when figures need editable SVG output, exact units, journal-quality visual hierarchy, 300-DPI panel composition, or transformation and provenance checks.
---

# Create SCI Figures

## Procedure

1. Inspect data types, units, missing values, outliers, coordinate conventions, and source provenance.
2. Choose the figure form based on the scientific claim; do not use decorative chart types.
3. Keep raw values unchanged unless the user approves a documented transformation.
4. Generate vector plots with `../../scripts/figure_factory.py plot`.
5. Assemble raster panels with `../../scripts/figure_factory.py panel` only when vector composition is unavailable.
6. Inspect the SVG text, axes, legend, ticks, clipping, and representative raster preview.
7. Report every transformation and output dimension.

For mixed aspect ratios, set `--cell-width` and `--cell-height` explicitly. Keep `--allow-upscale` off unless the user accepts interpolation.

Example:

```powershell
python ../../scripts/figure_factory.py plot --csv data.csv --x time_s --y stress_mpa --kind line --xlabel "Time (s)" --ylabel "Stress (MPa)" --title "Transient response" --output stress.svg
```

Read [references/figure-quality.md](references/figure-quality.md) before finalizing a journal figure.
