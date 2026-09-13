# Kimodo combat animation workflow

13 September 2026. Technical workflow design under policy MCL-DEV-2026-09-08. Requested by Daniel as Kimodo adoption begins. This specifies future production; no Kimodo motion, retarget, runtime fit or artistic acceptance is claimed. [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns current source, selection and next action; [prototype pipeline](ANIMATION_PROTOTYPE_PIPELINE.md) and [validation](../VALIDATION.md) govern execution.

## Production strategy

Use **Mordhau reference direction → sparse authored constraints → Kimodo whole-body proposals → Blender retarget and weapon finishing → isolated Unreal comparison → Daniel's visual/play decision**.

Kimodo supplies coordinated motion and variation. The animator still decides preparation, threat, weapon route, rhythm and recovery. Blender owns the editable project-body result. Cascadeur is an optional focused intervention for a demonstrated posing/support problem, with one explicit handoff; it is not a mandatory round trip for every take. C++ continues to own movement, legal inputs, attack clock, contact and damage.

The quality target is a convincing stylized medieval fighter: clear intent from opponent distance, exaggerated but coherent preparation, powerful two-hand delivery, purposeful support and controlled carry. Preserve accepted EX first-person feel and its source/native benchmark. Naturalism must not smooth away readable attack contrast. Tool output and numerical conformity do not establish reference quality.

## 1. Establish the action brief

Start with **one neutral right-origin horizontal two-handed sword attack**, from ready through full recovery. Keep parries, ripostes, branching and additional vocabulary deferred.

- Reference: the [corrected Mordhau atlas](MordhauAnimationAtlas/README.md), externally visible yellow-mask opening attacker at approximately 30.0–31.5 seconds. Use anatomical right/left. Recovery is partly obscured and must be labelled interpretation. Do not use the 156.50-second riposte transition as neutral preparation.
- Carry forward Daniel's latest preferences as targets: original C's preparation, original B's carry, more conspicuous Mordhau gathering, earlier horizontal blade, less folded torso and a slightly lower swing where compatible. Preserve those sources as comparisons; they are not mandatory generation seeds or accepted contact solutions.
- Define six observable beats: ready, gathering, maximum load, damaging passage, carry/braking, settled recovery. Record the reference evidence and uncertainty for each. Read current configuration and phase mapping before assigning seconds; do not infer engine boundaries from footage or copy stale timing numbers.
- **Daniel's 500 ms release contract:** author new attack drafts around an actual0.500s release at source1x (15 frame intervals at30fps,30 at60fps). Preserve the accepted EX benchmark; its older native0.300s segment is not the new-draft timing template. Mark native `ReleaseStart`/`ReleaseEnd`, store `required_release_seconds=0.5`, and check the saved source and preview binding with [CheckAttackDraftTiming.py](../Tools/CheckAttackDraftTiming.py). Do not defer this correction to a slower preview or runtime remap. Current pose direction is an upright torso and conspicuous arm-led pullback with weighty delivery; the [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns the actual revision and Daniel's review.
- Fresh Kimodo attack jobs declare `purpose: "attack"`, `frame_count`, and `attack_timing` containing `fps`, zero-based `release_start_index`/`release_end_index`, and `required_release_seconds: 0.5`. [KimodoWorkflow.py](../Tools/KimodoWorkflow.py) checks500ms, source duration/count, in-range constraint indices and explicit full-body poses at both release boundaries before loading the model. The model FPS must match before generation. Legacy diagnostics remain historical; their clocks do not define new attacks.
- Fix body/weapon identity, primary and rear-quarter cameras, opponent distance, source FPS/duration and intended root behavior. Resolve the body through [WorkingCharacter.json](../Config/WorkingCharacter.json), currently MB_v005_SurfaceRepair on MB_AccuRig. Its AnimationLab adapter is absent; a legacy adapter path swap is not supported.

The brief has two parts: a short motion prompt for Kimodo, and precise pose/phase/grip instructions for the animator. A long technical prompt is not a substitute for constraints.

## 2. Prove transfer once before multiplying takes

The installed launcher at `D:/AI/Kimodo/Start-Kimodo.ps1` selects `Kimodo-SOMA-RP-v1.1`; its companion launcher sets CPU text encoding. Start with that model and default generation settings. Record the actual installed revision, model/weights identity and available controls before implementation. This design inspected the launcher and local generation code, but did not run generation or establish current server readiness.

Make one short, disposable-in-purpose but retained diagnostic motion containing a turn, bent elbows and a deliberate weight shift. Prove these boundaries on an isolated copy:

1. Save Kimodo NPZ and constraints/settings. Deliberately convert a transfer copy to standard-T-pose BVH, then import to Blender. This is a source-transfer operation, never automatic runtime export or promotion.
2. Map SOMA to the actual AccuRig hierarchy; calibrate rest rotations, limb proportions, root/pelvis separation, forward axis, scale and left/right. Preserve target rest skeleton, weights, mesh and original sources. Use an existing suitable retarget route if available; establish a bounded mapping if absent, not a new general rig framework.
3. Preserve time in seconds. Read model FPS; the local generator derives frame counts from duration and model FPS. Resample for the target scene without changing duration, record frame-origin/terminal-sample conventions, and avoid counting an extra endpoint as extra action time.
4. Fit the retained sword to real palms: right primary grasp guardward, left support grasp pommelward. Both hands and body remain editable; primary grasp owns the sword. Check wrist roll, finger closure, elbow reach and a mid-motion pose, not just rest.
5. Save an editable Blender source and verify the imported action survives one save/reopen. Inspect the exact target body from front, rear, left and right; preview the complete diagnostic motion in primary and rear-quarter views at 1x.

Keep raw NPZ immutable. SOMA exports use 77 joints while the model works internally with 30; additional output joints do not demonstrate generated finger performance. Official BVH output uses centimeters, while Kimodo constraints use meters/Y-up. Explicitly test this boundary instead of assuming Blender import defaults. [Output formats](https://research.nvidia.com/labs/sil/projects/kimodo/docs/user_guide/output_formats.html)

Exit when timing, orientation, proportions and editable transfer work. If all later candidates share an inverted grasp or collapsed shoulder, repair this common premise once before another batch.

## 3. Direct generation with sparse constraints

Author key poses in the calibrated source skeleton, using the target body and sword as a feasibility check. Do not paste AccuRig joint coordinates into SOMA constraints. Start with roughly four to six useful full-body landmarks across the action; add sparse hand/wrist targets only where they clarify the hand route. Avoid redundant or contradictory full-body and hand targets at the same frame.

| Beat | Direct explicitly | Leave room for Kimodo |
|---|---|---|
| Ready | Oblique sword, seated two-hand grasp, opponent attention, supported stance | Subtle balance |
| Gathering | Reference-led opening and two-hand transport, visible torso participation | Coordinated limb spacing |
| Loaded preparation | Clear right-origin threat, useful blade orientation, reachable hands | Support and counterbalance |
| Damaging passage | Phase anchor, feasible hilt position/orientation compatible with authoritative guide | Connected body delivery within that constraint |
| Carry | Momentum continues beyond passage; torso and arms brake coherently | Absorption details |
| Recovery | Usable ready state and continuous return | Natural settling |

Place the hands from one coherent sword/grasp relationship when authoring these landmarks. Kimodo hand targets are sparse conditioning, not a continuous two-hand prop solver. Recheck the blade reconstructed from the primary grasp between landmarks and after retargeting. If exact hand positions conflict with target proportions, revise the pose/body strategy; do not detach the hands or silently move damaging reach.

Keep neutral root travel consistent with C++ actor movement. Prefer sparse root waypoints unless a continuous path answers a real need. Do not constrain every pelvis sample flat: body weight transfer and actor locomotion are different things. Dense root paths are supported, but a constant path is not a complete foot-plant solution.

Kimodo recommends sparse constraints, fewer than 20 constrained frames per type except root paths. Keep post-processing enabled initially. Foot-contact patterns are described as trained capability but currently unavailable as direct demo/API controls; use supported foot targets and finishing when needed. Post-processing does not validate project weapon contact. [Constraints](https://research.nvidia.com/labs/sil/projects/kimodo/docs/key_concepts/constraints.html), [best practices](https://research.nvidia.com/labs/sil/projects/kimodo/docs/key_concepts/limitations.html)

## 4. Generate three distinct complete performances

Use one complete-action prompt first, for example:

> A person performs one powerful two-handed sword slash from their right to their left at chest height, gathering the sword back with a coordinated body turn, then following through and returning to a ready stance.

This is a starting hypothesis, not a verified successful prompt. Exact height, phase timing and grip belong in constraints. Describe visible movement rather than expecting the word “Mordhau” to reproduce the reference. Avoid baseball/golf prompts: they contradict the project's reference precedence, and Kimodo specifically identifies baseball as outside its training coverage.

| Candidate | Deliberate difference | Fixed across candidates |
|---|---|---|
| A — gathering | Strong continuous two-hand preparation and decisive launch | Direction, weapon, body, phase anchors, cameras |
| B — rotational | More counterturn, curved hand travel and torso braking | Same |
| C — grounded | More asymmetric support and absorbed recovery | Same |

Change a coherent pose/constraint strategy for each, not merely the random seed. Retain seed/settings for each call. Generate sequentially, keeping heavy rendering and editors from competing with inference. Reuse the loaded model where practical. Do not sweep models, guidance weights, steps and seeds simultaneously.

Start with defaults. If a promising take misses a target, correct conflicting constraints first; then change one generation parameter or one constraint hypothesis. Compare the same seed when useful, while retaining exact raw results rather than promising cross-version determinism. Use multi-prompt generation only if a complete-action prompt demonstrably fails; transitions consume time in the following segment and can soften a fast strike. [Prompt guidance](https://research.nvidia.com/labs/sil/projects/kimodo/docs/key_concepts/limitations.html), [CLI and reproducibility controls](https://research.nvidia.com/labs/sil/projects/kimodo/docs/user_guide/cli.html)

Generation saves raw motion/settings only. Transfer copies and preview assembly are deliberate separate steps; no batch auto-imports into Unreal or changes selection.

## 5. Compare, select and finish

Retarget each complete take using the proven mapping and minimal common grip setup. Produce inexpensive, identical-camera primary and rear-quarter previews on the actual body at full source timing and 1x. Include the weapon. Compare against the retained preferred source and the reference, never against only the other generated candidates.

Record each take's strongest feature, largest defect and provisional rank. Judge in this order:

1. Windup onset, attack direction and meaningful threat at defender distance.
2. Continuing preparation, launch contrast and curved hilt/blade travel.
3. Supported body motion, connected two-hand grasp and coherent attention.
4. Carry, braking and complete recovery.

Grip inversion, detachment, a sword stall, misleading damaging reach or a collapsed intermediate pose cannot be averaged away by attractive body motion. Check these as explicit defects. Missing/stale views cannot establish a new pass. Sampled frames do not establish continuous rhythm; state exactly what was inspected and leave unobserved qualities unscored.

Select a provisional winner without asking Daniel to approve every draft. In Blender, refine its native curves: grip/fingers and wrist continuity first, then preparation/launch spacing, shoulders/twist, support and recovery. Preserve the expressive body motion that won. Use existing controls and native constraints before proposing another solver. Save finishing edits before previews; never regenerate over them from an older recipe.

Allow one or two focused passes with a named defect and observable improvement. After two passes without convincing gain, change the choreography/constraint premise. After two coherent unsuccessful batches, identify whether the limit is generation, retargeting, body deformation or weapon compatibility; prepare the actionable specialist brief/assets for a persistent animator limitation. Do not commission work automatically.

## 6. Test the selected rough performance before expensive polish

Selected integration is a separate execution step. Use the existing isolated Unreal route, preserving default/runtime selections and accepted EX. Establish any required AccuRig-aware adaptation explicitly; the current body is not compatible with an older TP skeleton merely because bone names can be relabelled.

Compare native source and engine motion at matching phase times before diagnosing choreography. Apply the established source-to-runtime timing map once. Examine neutral and downward aim, controlled turning/footwork, damaging passage, hit/miss and interruption/return. Accels/drags use inputs at unchanged playback rate. Do not disguise source deficiencies with runtime correction or retime previews to hide disagreement.

Measure hilt/tip discrepancy through the damaging interval and identify its worst time and visible effect. Use actual current contract tolerances; no invented universal centimeter threshold establishes acceptance. Resolve material visual/contact disagreement explicitly. Keep mesh deformation findings separate from motion quality. Then finish only defects visible in context and rerun changed evidence.

Build and run affected contract tests only if C++ changes. Consequential code/contact changes get one independent review. Daniel's normal-speed visual and playable decision establishes acceptance; technical import success does not.

## Reusable package and first milestone

For each experiment, retain under an isolated `ArtSource/Kimodo/<experiment>/<candidate>/` directory: brief, exact prompt/settings/seed, constraints, raw NPZ, deliberate transfer copy, retarget mapping identity and editable Blender source. Put previews in the corresponding `Saved/Kimodo/<experiment>/` directory. A small receipt binds source hashes, body/weapon identity, model/revision, FPS/frame range, phase map, cameras and preview paths. Once native finishing starts, that saved source is the edit authority; raw Kimodo output remains provenance.

Use the existing TP checkpoint for one compact decision entry: candidate/source, visible change, relevant check, observation limits and next useful action. Do not create a second status ledger. Record elapsed time to the first useful batch and manual cleanup if measured; optimize for a strong reviewable result with less repair, not generation volume. Token usage is unmeasured unless cached input, uncached input and output are actually available.

**First production milestone:** one verified SOMA-to-MB transfer, three constrained complete neutral RH performances, six source-speed comparison movies, one provisionally selected editable take and at most two focused refinements. Runtime evaluation follows selection; broader vocabulary remains deferred. Daniel directs and reviews; the agent operates the tools. This document designs that milestone and does not claim it has been executed.

## Implemented local entry points

Implementation was authorized after this design. The [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns the actual results and provisional selection; these commands document the reusable tool route, not acceptance.

Use `D:/AI/Kimodo/venv/Scripts/python.exe` for `Tools/KimodoWorkflow.py` and `Tools/KimodoGraspTargets.py`; use the installed Blender executable in background mode with `--python-exit-code 1` for Blender scripts. Outputs remain under the isolated experiment, with overwrite guards.

1. `Tools/KimodoWorkflow.py generate <job.json> [<job.json> ...]` reuses one loaded model for the explicitly named jobs, retaining raw NPZ, exact inputs/effective constraints, generator copy and model/package identity. It does not convert or import.
2. `Tools/KimodoWorkflow.py convert <candidate> [...]` deliberately creates standard-T-pose BVH transfer copies.
3. `Tools/RetargetKimodo.py -- build --directory <candidate-directory>` imports into an isolated working-body copy and verifies editable transfer/persistence. Blender script arguments follow its `--` separator.
4. `Tools/KimodoGraspTargets.py <candidate-directory>` prepares an explicit native primary-grasp guide from the authored sparse poses. `Tools/FinishKimodoGrip.py -- --directory <candidate-directory> --targets <guide.json> --output <new-take.blend>` bakes both arms with the existing nonstretch posing math, preserving generated body curves. Any shared-route adjustment is separately identified; unreachable results remain failures. This is native authoring, not runtime compensation.
5. `Tools/RetargetKimodo.py -- render --directory <candidate-directory> --source <saved-take.blend> --sample-indices 12,22,26,31,43,60` renders both full1x movies, four body views and named source-index samples from saved native curves. `Tools/CompareKimodo.py -- <manifest.json>` composes already-rendered, timing-matched comparisons.

Observed integration issue: the installed postprocessor's mask builder recognizes `left-hand`/`right-hand` but skips generic `end-effector`. The wrapper expands paired hand sets into the recognized types without changing the installation; a retained-motion reprocessing experiment verified the corrected target behavior. Sparse targets still do not ensure continuous two-hand prop coupling. The native both-arm finishing route addresses that demonstrated limitation; do not diagnose every free-wrist failure as retargeting or generation quality.

`Tools/InspectKimodoBlade.py -- <saved-take.blend> <new-receipt.json>` measures a selected draft against the retained EX source guide at its native release samples. That alignment is a source-space diagnostic, not engine contact evidence. Resolve material discrepancy before treating a take as ready for gameplay; preserve the accepted source and current C++ authority.
