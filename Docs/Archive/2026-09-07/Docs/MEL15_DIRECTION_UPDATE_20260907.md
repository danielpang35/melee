> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# MEL-15 direction revision — 7 September 2026

This reconciles the new Notion and Linear direction with the paused local implementation. **No animation source, assets, builds or tests were changed or run for this revision.** The handoff prompt was rewritten and the framework aligned. Earlier versions are preserved under `Saved/MEL15/HandoffRevisions/20260907_031752`.

**What now leads the work**

| Updated decision | Consequence for the next instance |
|---|---|
| The user likes Astra Ultra's current swing weight and feel. | Preserve timing, acceleration character, commitment, responsiveness and a reproducible A/B control. Rehaul visual arm/hilt performance without replacing the praised feel. Praise is not visual acceptance or proof of a specific accepted DLL. |
| Arms do not convey the swing; the sword “sprinklers” across the screen. | Judge coordinated camera-relative sword and especially hilt travel against Mordhau, isolating camera motion and proportion differences. A large blade arc about a nearly stationary hilt fails. |
| Grip contacts may already be correct. | First isolate actual placement, arm pose, hand model/skinning and texture/material through timestamped reference, skeleton, neutral-material and textured views. Change offsets only with evidence. |
| Stomach/upper-abdomen idle is a firm requirement. | Establish relaxed idle and continuous idle↔load/parry/recovery before accepting dependent swings. Preserve raised preparations/defenses rather than globally lowering the weapon. |
| Deliberately authored poses and phase curves, procedurally expanded, are adopted. | Author separately timed body/hand channels and full weapon transforms including roll; calibrated grips and final IK support the performance. Existing candidate key values/solver choices are infrastructure, not immutable final targets. |
| Quality/control/production efficiency take priority over literal realism. | Use believable exaggeration. Advanced physics may generate source motion, be baked, or run at runtime when quality/resource gains justify it; keep final weapon/collision authority unified. |
| One exceptional exchange comes first. | MEL-5 diagnostic/idle prerequisite → MEL-6 horizontals + MEL-15 full-body/one overhead → MEL-11 integrated playable acceptance. Preserve related owners and do not duplicate historical Notion backlog tasks. |
| Direction expansion and broad profiling remain later work. | Prove overhead interpolation after the exchange; only then consider 240 selections or retain bespoke anchors if quality fails. Resolve the observed memory blocker and narrow physics-cost questions without reinstating broad performance gates. |

The reference video `D:/Mordhau Montage VI.mp4` exists locally (76,339,804 bytes). This revision checked its presence only; it did not inspect new footage. Earlier source notes identify2:44–2:45.875 samples; those remain starting references with uncertain hidden geometry.

**Sources actually read**

- [Notion Animation](https://app.notion.com/p/3d32e3c3f8f881e08474defe7febb171), edited07:08:58 UTC.
- [Notion Melee Swing Model](https://app.notion.com/p/3d32e3c3f8f881028f05c2a960248ff1), edited07:09:02 UTC.
- [Notion Current Milestone](https://app.notion.com/p/3d32e3c3f8f8813c8883ed9e8bd1f299), edited07:09:07 UTC.
- [Notion Visual Direction](https://app.notion.com/p/3d32e3c3f8f881dabc3be8eff5b29360), edited07:09:11 UTC.
- [Notion Task / Experiment Database](https://app.notion.com/p/3d32e3c3f8f881758692e453afcdecb4), edited07:09:31 UTC.
- [MEL-5 — Diagnose hand/arm appearance against Mordhau and establish stomach-level idle](https://linear.app/meleeslasher/issue/MEL-5/diagnose-handarm-appearance-against-mordhau-and-establish-stomach), description/relations updated07:10:20 UTC; comments read.
- [MEL-6 — Rehaul authored procedural horizontal swings for a controlled playable A/B](https://linear.app/meleeslasher/issue/MEL-6/rehaul-authored-procedural-horizontal-swings-for-a-controlled-playable), updated07:10:20 UTC; no comments returned.
- [MEL-15 — Rehaul full-body swing motion and overhead hand follow-through](https://linear.app/meleeslasher/issue/MEL-15/rehaul-full-body-swing-motion-and-overhead-hand-follow-through), updated07:10:20 UTC; comments read.
- [MEL-11 — Package and play-review the current versus revised longsword exchange](https://linear.app/meleeslasher/issue/MEL-11/package-and-play-review-the-current-versus-revised-longsword-exchange), updated07:09:57 UTC.

The meaningful new decisions are in the issue **descriptions**, later than the06:47 pause comment. That comment remains a valid historical implementation status but its action order is superseded by the diagnostic/idle foundation above. Notion defines the adopted direction; Linear owns live execution state. Neither proves a new build, implemented source change or visual acceptance.

**Technical checkpoint remains separate**

The live module manifest still selected1006 and the test initializer error near PresentationTests.cpp:176 was still present when checked. The earlier1007 memory failures, unrendered combined source, frozen-core test provenance, incomplete pitched audit and capture/automation limitations remain in the handoff. This design revision does not validate or invalidate those technical results; it changes what the next implementation must accomplish.

The previous “brief exit is acceptable” preference remains valid. It is now accompanied by explicit praise for swing feel; overall visual/playable acceptance remains pending. No new comment or page was published to Linear or Notion during this prompt revision.

