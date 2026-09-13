# Third-person horizontal — reference review and concrete breakdown

8 September 2026. **The new footage is sufficient to guide an initial third-person block. The main deficiency in the current implementation is the lack of a dedicated authored external performance.** The reference supports coordinated hilt transport, changing elbow shapes, shoulder/torso participation and a distinct carry/return. It does not justify reconstructing exact hidden biomechanics or combining two weapons' timings.

This work answers the current request to review and analyze the footage, third-person handoff and AGENTS.md, with subagents. The imperatives in the reviewed documents are contextual requirements for the proposed animation work; they were not executed as an additional request to replace assets. No runtime, animation, selection, gameplay tuning or remote task state was changed. Existing dirty work was preserved.

## Reference selection

| Source | User-confirmed weapon | Selected source span | Role |
|---|---|---|---|
| `01-36-39.mp4` — rear chase view | Greatsword | **5.383900–7.278233 s** | Primary weapon-specific reference: bare-back shoulder/arm coordination, curved hilt route, carry and return. Opening repetition corroborates it. Feet/pelvis are cropped. |
| `01-46-20.mp4` — opponent in player camera | Training Sword | **0.456067–2.067100 s**; excerpt includes ready through 2.206033 | Supporting defender view: compact shoulder load, forward delivery, opposite-side folded carry, stance/readability. Hit distortion, armor and player weapon obscure details. |

These are different weapons and performances, not synchronized camera angles. Right-origin lateral attack classification is visually supported; exact inputs were not confirmed. No engine attack boundaries or world-space measurements were recovered. Greatsword is the primary choice when the references differ.

Play the short [Greatsword excerpt](A/selected-source-speed.mp4) and [Training Sword excerpt](B/selected-source-speed.mp4) at 1× before studying the keys. These are source-timed, silent excerpts, with no speed adjustment or frame interpolation. Both were decoded again: source-relative timestamp error was at most 0.000001 s and frame counts matched. This verifies the files' timing, not normal-speed artistic acceptance; the model's review was **frame-sequence inspection only**.

![Greatsword reference key poses](A/selected-beats.jpg)

![Training Sword supporting key poses](B/selected-beats.jpg)

## What the footage changes about the problem

1. **The hilt path is a primary animation subject.** In the Greatsword repetition it travels down/right in the load, rises as the swing crosses, carries down/left, then returns upward/inward. The torso and arms visibly change shape along that route. A fixed grip pivot with a wide blade arc would miss this construction.
2. **The two arms do different jobs within one connected grip.** Elbow flexion and shoulder silhouettes change instead of maintaining one rigid triangle. Author weapon orientation, both hands and shoulder participation together; measure apparent grip faults before changing offsets.
3. **Carry and return contribute as much as the crossing pose.** The Greatsword maintains an extended opposite-side carry; the Training Sword folds more tightly near the opposite shoulder. Both reorganize into ready by a distinct route. Do not blend those different silhouettes into an imagined common clip.
4. **Body support remains partly interpretive.** A's feet are absent, while B offers only partly visible, moving-camera stance evidence. Begin with a modest supported stance and label the foot/pelvis decisions as authored. The new footage closes the reference gap enough to start blocking, without proving a full-body match.
5. **The present consumer cannot preserve such a performance yet.** It resets CF to reference pose, adds a generic phase coil and procedural foot targets, then fits arms to EX wrist goals. The numeric correctness of those fittings cannot demonstrate the observed choreography. A dedicated native third-person body-and-weapon clip is the relevant missing capability.

## Review of the specific third-person prompt

`Docs/THIRD_PERSON_ANIMATION_PROMPT.md` was read in full. Its one-action scope is appropriate: **neutral right-horizontal only**, ready → load → delivery → carry → return; complete blocking first, early Unreal proof, polish, then bounded aim/movement. Preserve the accepted EX_v002 first-person source, native playback, projection and shared gameplay clock. The newer prompt explicitly supersedes the older production handoff's third-person deferral; the old handoff remains useful implementation evidence.

The prompt's dedicated clip, coauthored body/hands/weapon, short source-to-engine loop and early visual review directly address the observed gap. Do not reintroduce retired Citadel/RC_v008 presentation, start a new anatomy project, or expand into other attacks. The new reference should be cited with the selections above instead of treating third-person reference as wholly missing. Its limitations should remain visible: no synchronized same-weapon front/side pair, no complete Greatsword feet, and no recovered engine phase boundaries.

## Small sequential work packages

| Package | Concrete work | Acceptance evidence |
|---|---|---|
| 1. Complete source block | Inspect existing CF controls; create a separate editable Greatsword right-horizontal action. Block body, hands, weapon and modest support together, using the selected Greatsword pose order. Overlay the preserved canonical release as a constraint. | Complete stepped and continuous normal-speed source preview with head, feet and entire blade framed; connected grips and transported hilt; explicit labels for authored lower-body choices. |
| 2. Early engine proof | Add a CF-compatible animation import and a dedicated TP selection/consumer separate from EX's canonical selector. Use the same attack transaction and phase clock; preserve source root offsets as visual only. | Source/Unreal key and subframe agreement; TP hands follow its visible weapon; capsule unaffected; approved FP/contact state preserved; new TP package can be selected/replayed without rebuilding. |
| 3. Polish the same action | Refine spacing, elbow/shoulder overlap, carry, recovery and supported feet in source. Fix observed deformation without rebuilding the performance at runtime. | Matched source/engine normal-speed review, one visible weakness per iteration, no material grip slip or persistent broken anatomy. Human review decides artistic success. |
| 4. Bounded composition | Add only needed legal aim/movement composition and one compact repetition/hit/miss replay. | Synchronized FP/external/defender views of the same transaction; cosmetic release agrees with canonical side, direction, reach class, active interval and contact order; affected checks plus one independent implementation review. |

One implementation trap matters now: **the existing EX selector also loads canonical weapon motion into simulation**. It must not be reused as a cosmetic TP slot. The export tool also treats non-EX sources as 30 fps, and the CF importer currently disables animations. The detailed, line-cited [technical review](TECHNICAL_GAPS.md) records these gaps and the smallest changes needed.

If blocking reveals a real conflict with the preserved canonical release, the prompt already supplies the appropriate conditional branch: one separately selectable coauthored alternative, with a concrete first-person/contact comparison before replacing the accepted baseline. There is no footage evidence yet that this branch is necessary.

## Compact checkpoint and receipts

- Completed: AGENTS.md and prompt review; two specialist subagents for clip B and technical gaps; parent clip A review; selected spans, timestamped keys, source-speed excerpts and timing verification; sequential packages above.
- Reviewed authority: user-supplied AGENTS instructions and `C:/Users/Daniel Pang/.codex/AGENTS.md` (same 13 rules); third-person prompt; production handoff; character reset. No ancestor AGENTS.md was found along the workspace ancestry.
- Pending for animation work: actual source/control inspection, authored block, dedicated consumer and visual acceptance. No claim of finished animation, runtime verification or continuous-playback acceptance is made by this review.
- Evidence: [Greatsword analysis](CLIP_A_ANALYSIS.md), [Training Sword analysis](CLIP_B_ANALYSIS.md), [technical gaps](TECHNICAL_GAPS.md), `review-receipt.json`, per-sequence `frames.json` and decode logs. Source hashes are pinned in the receipts.
- Reproduction: from the workspace, run `python Docs/ThirdPersonReference20260908/extract_evidence.py --help`; existing selections record exact arguments in their receipts. `python Docs/ThirdPersonReference20260908/package_review.py` rebuilds the short excerpts and key sheets from the saved selection.
- Efficiency correction: reused `Saved/VideoRuntime` and existing playback/export evidence; separate agent ownership avoided duplicate code/clip investigation; no project builds or broad gameplay tests were needed for this analysis-only change.
