# Preference model and iteration protocol

## Why this is not a single learned score

Whole-frame similarity confounds content, simulation state, crop, palette, and layout. Use it only to find possible matches. Hard rules come from explicit causes selected by the user or deterministic manifest checks.

## Controlled tag vocabulary

Use a component prefix and a concrete cause.

- `colorbar:hue-clash`, `colorbar:too-wide`, `colorbar:illegible`, `colorbar:wrong-range`, `colorbar:missing-units`
- `annotation:overlap-colorbar`, `annotation:low-contrast`, `annotation:outside-safe-area`, `annotation:too-dense`
- `highlight:good-focus`, `highlight:too-loud`, `highlight:obscures-data`
- `layout:balanced`, `layout:critical-overlap`, `layout:weak-hierarchy`, `layout:preferred-safe-zone`
- `text:cropped`, `text:good-density`, `text:too-small`
- `animation:micro-reveal`, `animation:good-easing`, `animation:good-continuity`, `animation:too-busy`
- `science:meaning-changed`, `science:legend-preserved`, `science:time-preserved`
- `style:*` is always a soft preference or warning; it never becomes a hard blocker automatically.

## Feedback protocol

- Weight 2 means “strong and recurring”; weight 1 means “useful but contextual.”
- Crop to the relevant region or provide normalized `x,y,width,height`. Prefer one cause per negative region.
- If the user likes the animation but dislikes the composition, add two records: a positive region/tag for animation and a negative region/tag for composition.
- Contradictory feedback is allowed across contexts. Use distinct projects or add context tags such as `format:vertical` and `format:landscape`.

## Candidate manifest contract

Bounding boxes may be normalized or expressed in pixels when frame dimensions are provided. Every critical overlay should have a stable `id`, `type`, and `bbox`. Text components should include foreground and background hex colors for contrast checks.

The `scientific` object is a gate, not a style score. Its values must reflect real inspection:

- `legend_visible`
- `units_visible`
- `timestamp_meaning_visible`
- `solver_frame_modified`

## Iteration loop

1. Render stills at the first frame, extrema, overlay transitions, layout switches, and final frame.
2. Generate/update sidecar manifests from Remotion props.
3. Score all stills.
4. Fix blockers first, warnings second; preserve positive tags.
5. Rerender only affected stills.
6. Stop when all pass or after four loops. At the limit, show a contact sheet and ask for a focused choice.
7. Render the full video, then check codec, duration, frame rate, audio, captions, and representative frames again.

## Colorbar rule

The data colormap and the editorial interface palette are separate systems. The colorbar expresses numeric data; annotation and background colors should support it without competing. Changing only the appearance of an already rasterized cloud map can invalidate the legend, so re-export from the solver when the numerical map or range changes.
