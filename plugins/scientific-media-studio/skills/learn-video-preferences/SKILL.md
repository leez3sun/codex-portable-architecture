---
name: learn-video-preferences
description: Learn and enforce a user's positive and negative preferences from scientific-video keyframes. Use when the user likes or dislikes particular frames, animations, cloud-map colorbars, highlights, callouts, captions, typography, overlay positions, or overall composition; when manual placement keeps recurring; or when representative frames should be scored and revised automatically before a full Remotion render.
---

# Learn Video Preferences

Turn subjective feedback into an interpretable project profile. Positive examples add reusable component-level preferences; negative examples add explicit blockers. Never infer a hard prohibition from whole-frame similarity alone.

## Workflow

1. Create one profile per visual system or project family with `../../scripts/keyframe_preferences.py init`.
2. Extract or render representative frames: opening, extrema, every layout change, every annotation state, and closing frame.
3. Ask the user to rate only relevant regions when possible. Record:
   - `positive`, weight 1 or 2: preserve the named animation, spacing, callout, hierarchy, or color relationship.
   - `negative`, weight 1 or 2: forbid the named cause, not unrelated content in the frame.
4. Use controlled tags from [references/preference-model.md](references/preference-model.md). Always include a component tag such as `colorbar:*`, `annotation:*`, `layout:*`, or `animation:*`.
5. For every candidate still, write a sidecar manifest based on `assets/candidate-manifest.example.json`. Include component bounding boxes and scientific-integrity fields.
6. Run `score`. Treat any blocker as a failed gate even when the numeric score is high.
7. Apply the returned revision actions, rerender the affected stills, and rescore. Stop after the profile's iteration limit and request focused user judgment if a frame still fails.
8. Render the full video only when all representative frames pass. Then run normal video technical QA.

## Remotion implementation

- Build overlays as named interactive components: `ScientificColorbar`, `CalloutBox`, `HighlightFrame`, `CaptionRail`, and `SimulationMetadata`.
- Expose position, width, height, padding, colors, and timing through direct props and inline styles so Remotion Studio can write edits back to code.
- Keep the solver render and the explanatory overlay on separate layers.
- Render low-resolution stills for iteration; do not repeatedly render the full video.
- A positive animation preference applies to timing/easing/component behavior, not permission to copy an unrelated creator's identity.

## Scientific gates

- Never recolor a rasterized cloud map in a way that changes its numerical mapping. Re-export from Abaqus when the data palette or range must change.
- Keep colorbar range, ticks, units, deformation scale, time meaning, legend visibility, and boundary-condition context intact.
- Prefer perceptually uniform, ordered, color-vision-accessible maps where the solver/export path permits it.
- Do not allow highlights, captions, or callouts to cover the colorbar, units, extrema, timestamp, or critical response region.

## Commands

```powershell
python ../../scripts/keyframe_preferences.py init --project impact-study --output preference-profile.json
python ../../scripts/keyframe_preferences.py add --profile preference-profile.json --frame liked.png --sentiment positive --weight 2 --tags animation:micro-reveal,callout:compact --region 0.10,0.10,0.32,0.20
python ../../scripts/keyframe_preferences.py add --profile preference-profile.json --frame disliked.png --sentiment negative --weight 2 --tags colorbar:hue-clash,annotation:overlap-colorbar
python ../../scripts/keyframe_preferences.py score --profile preference-profile.json --frame candidate.png --manifest candidate.json --output candidate-report.json
python ../../scripts/keyframe_preferences.py plan --profile preference-profile.json --reports candidate-report.json --output revision-plan.json
```

Read [references/preference-model.md](references/preference-model.md) before the first feedback session.

## Boundaries

- This is preference accumulation and rule enforcement, not autonomous model fine-tuning.
- Perceptual hashes are discovery signals only. They cannot prove layout quality, colorbar correctness, scientific fidelity, or originality.
- Do not upload frames or profiles. All processing is local and zero-subscription.
