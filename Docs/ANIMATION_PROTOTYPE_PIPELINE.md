# Animation creation and ideation pipeline

9 September 2026. Policy MCL-DEV-2026-09-08. This is the current prototype procedure, supplementing [project development](DEVELOPMENT.md) and superseding historical prototype instructions in [Animation workflow](ANIMATION_WORKFLOW.md) and [MCP proposal](BLENDER_MCP_PIPELINE.md). The [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) continues to own actual candidate identity and acceptance; this document selects no animation.

## Purpose and tool split

**13 September body direction:** establish the AccuRig working body first; existing TP attack retargeting is deferred. The KN proof from the 12 September [Blender–Cascadeur workflow](BLENDER_CASCADEUR_WORKFLOW.md) is historical preparation. Its tool split remains useful: Blender prepares the character, Cascadeur owns whole-body choreography, and Blender owns finishing after an explicit handoff. Reuse Python for setup/transfer/preview work. The legacy Python adapters below remain explicit KN/CF routes, not AccuRig controls. The TP checkpoint records actual access and completion.

Produce cheap, distinct complete performances; learn which artistic idea works; refine the strongest. Blender Python and MCP share Blender's native animation capabilities. MCP supplies interactive access, not choreography intelligence.

| Work | Default route | Retained result |
|---|---|---|
| Isolate source, author initial batches, repeat operations | Existing Python / AnimationLab | Rig and authoring snapshots, hypothesis, editable native source |
| Inspect evaluated grips, poses and intermediate motion; edit a few curves | MCP into one owned Blender session, using existing Python authoring functions | New native take and brief edit description |
| Render complete comparisons, derive samples, record identity | Existing serialized Python route | Source-speed preview and compact receipt |
| Select and critique | Owner; reuse a critic when assigned | Relative ranking, concrete defects, evidence limits |
| Gameplay binding | Existing explicit Unreal/C++ route after selection | Changed-contract evidence and human play decision |

MCP scene inspection was successfully exercised in this session against Blender 5.2.1 LTS/add-on 1.6/protocol 5. Editing benefits and cost savings are unmeasured. Python remains a usable fallback if MCP fails; connectivity must not block a batch.

## 1. Write one small experiment brief

Specify the action and start/end state, intended feeling, one primary reference and its uncertainties, fixed primary and rear-quarter comparison cameras, protected baseline, and the question this batch should answer. Separate neutral strikes, riposte origins and manipulation inputs. For an attack, describe ready → load → release → passage → carry → recovery without prescribing a universal frame count.

**13 September explicit timing direction:** new attack animations must be authored around500ms of release at source1x. Frame counts follow FPS:15 intervals at30fps,30 at60fps. The accepted historical EX native benchmark stays preserved; do not copy its300ms source segment into a new draft or rely on future playback retiming. Save native release markers and verify the exact source/preview contract with [CheckAttackDraftTiming.py](../Tools/CheckAttackDraftTiming.py). See the [Kimodo workflow](KIMODO_ANIMATION_WORKFLOW.md) for the native marker names and current authoring direction.

For questions about reference acceleration, steering or contact, use the [Mordhau console experiment method](MORDHAU_CONSOLE_EXPERIMENTS.md). Calibrate diagnostic semantics and isolate input/camera effects before transferring a finding to authored timing or spacing. This is an optional targeted research route, not a new per-draft validation gate; its checkpoint distinguishes completed clip inspection from pending live tests.

Use the native body and rig in [WorkingCharacter.json](../Config/WorkingCharacter.json) for new authoring. The AccuRig working body currently has no AnimationLab control adapter; existing KN/CF adapters remain explicit historical options and cannot drive it by a path swap. Existing TP attacks require separate retargeting. Preserve accepted EX_v002 source/native playback/projection and C++ clock/contact authority. Declare exploratory timing or reach changes for later binding; never silently alter gameplay to fit a draft.

## 2. Check shared assumptions before multiplying candidates

On the seed, inspect the few reference beats needed to answer the current question: actor side, blade direction, palm/knuckle/thumb orientation, hilt seating and whole-body intent. Examine evaluated intermediate motion when endpoints could hide a reversal or path collapse. Use one focused close view only when the fixed defender view cannot answer a grip question.

This is a brief visual sanity check, not a pose matrix or mandatory full rig proof. If every candidate would inherit the same wrong grip or reference interpretation, correct that premise once first. An exact user correction may use one complete take. Do not treat repeated failures from a shared bad premise as an animator capability ceiling.

## 3. Ideate three complete performances

Default to three distinct hypotheses; expand to four–six only when additional ideas answer useful questions. Coauthor body, both hands and weapon through the whole action. Change a coherent artistic strategy, not random joints or near-identical elbow offsets.

Example right-horizontal batch, subject to the chosen reference:

| Candidate | Hypothesis | What would support it? |
|---|---|---|
| A: Gather and launch | Compact continuing load, delayed arm opening, decisive outward release | Clear load/delivery contrast with a readable projected hand launch |
| B: Counterturn and sweep | Stronger body counterturn, curved lateral hands, torso braking before arm carry | Coordinated rotational power without a stiff torso or grip turnover |
| C: Compress and drive | Lower body compression, committed extension, absorbed recovery | Visceral delivery and purposeful recovery without hand-path collapse |

Keep character, camera, plain presentation and playback at 1x consistent. Authored duration may differ deliberately; record it and never normalize playback to hide timing differences. Each take must include recovery before it competes for selection.

## 4. Author with Python; refine interactively where useful

Use [native adapter instructions](../Tools/AnimationAuthoring/README.md). Initial JSON is a blocking recipe; after authoring, the saved `.blend` and its native curves are the source. The primary grasp owns the sword; derived weapon samples do not drive regeneration.

For MCP, one owner verifies the open file, dirty state, rig/action and frame before writes. Use an isolated copy without overwriting another editor's unsaved scene. Perform a small coherent edit, read back the evaluated result, inspect the affected pose/interval, and save a new take. Reuse repository functions rather than inventing another solver. Batch related reads and edits where practical; avoid one tool call per bone.

Save actual native edits before the scripted preview. Never rebuild from stale JSON and erase curve work. Save/reopen once when first proving an MCP save route or diagnosing persistence; ordinary pose drafts do not need repeated persistence tests. Keep published previews and their source immutable.

Current executable entry points:

```powershell
python Tools/AnimationLab.py new rh_ideation_01 --adapter cf-controls-v1
python Tools/AnimationLab.py render rh_ideation_01
```

The native adapter currently creates one control proof; these commands do not automatically produce three artistic performances. Author/register the remaining distinct takes through the existing adapter/batch manifest workflow before comparison. Do not use legacy generation or assume `--count` supplies the native artistic batch. Follow the adapter README for native-source refinement. If none is selected, copy a rejected source into an isolated diagnostic take rather than falsely selecting it to unlock `refine`.

## 5. Compare the whole action cheaply

Render sequentially through the existing AnimationLab lock: plain, low-cost, complete source-speed primary and rear-quarter previews per candidate, using the same camera definitions across candidates. Reuse previews only when source/camera identities match. No engine imports, builds or broad regressions for animation drafts. Body/rig checks require front, rear, left and right views. Further diagnostic views are optional.

Rank each complete performance against its siblings and the primary reference:

1. Intent and readable threat.
2. Load/delivery contrast and hand launch.
3. Curved hand/blade path and correct direction.
4. Body/arm coordination and connected-looking grips.
5. Carry, braking and recovery.

Use a compact comparison: strongest feature, biggest visible failure, provisional rank, next change. A distracting grip inversion or intermediate collapse is a concrete defect, not something a high average score can hide. Leave unobserved qualities unscored. Intentional stretch is allowed when it helps the motion.

Continuous source-speed review establishes more about rhythm than sampled frames. If the agent only inspects frames, disclose that explicitly; retain the video for Daniel's review. A generated video is not evidence that anyone watched it continuously. Agent selection is provisional; human visual/play acceptance is separate.

## 6. Select, refine, or change direction

Select the strongest provisional candidate if its central gesture is promising. Make one or two focused refinement passes, preserving what won. Each pass states a visible defect, a proposed change and what would falsify the improvement; render the complete action again only for changed takes.

After two passes without convincing gain, return to a new batch or change choreography/controls. Before adding a solver or rig feature, demonstrate the limitation and run one bounded experiment. After two coherent batches expose a persistent specialist limitation, prepare the actionable one-exchange animator brief and editable assets. First rule out the shared-premise error described in step 2. Do not commission anyone automatically.

## 7. Keep promotion separate

Prototype generation, rendering and MCP edits never export, import or select runtime assets automatically. Only a deliberately selected source enters existing native integration. Follow [VALIDATION.md](../VALIDATION.md): check changed rig/scale/phase/contact contracts; build changed C++; use one independent review for consequential code/contact changes.

Then review the playable exchange, including hit/miss/interruption and controlled aim/footwork. FP/TP arm styling may differ, but communicated threat and authoritative contact must agree. Accels/drags remain manipulation inputs at unchanged playback speed. Complete one exchange before expanding the vocabulary.

## One compact checkpoint per experiment

Use the existing task checkpoint; do not introduce another status ledger. Copy this structure as needed:

```text
Question / action / reference uncertainties:
Protected baseline / rig / camera:
Candidates: ID — artistic hypothesis — native source — preview — duration/FPS
Comparison: ID — strongest feature — biggest failure — rank
Observation: sampled frames / continuous playback / actual user feedback
Decision: provisional winner or reject; human acceptance remains separate
Refinement: visible defect → change → observed result; pass count
Evidence: relevant source/config/module identity; changed-contract check if any
Efficiency: start → first reviewable batch; render time if measured;
            failed calls/regenerations and cause; accepted improvement if any
Next useful action:
```

At batch selection or refinement exit, correct only demonstrated waste: duplicate generation, repeated unchanged reviews, excessive screenshots, broad tests or idle polling. Measure cached input, uncached input and output separately only when available; otherwise mark usage unmeasured. Do not infer allowance charges or fixed savings from raw token totals.

First MCP trial: on the current isolated grip/direction correction, use live inspection and one native edit, save it, then produce the standard full preview. Record elapsed time and rework alongside the existing Python route. This is a proposed next experiment, not an executed edit or new selected candidate.

13 September multi-angle requirement: new character validation requires all applicable named views, bound to the exact source identity; animation views must share the full source timing and 1x playback. Missing/stale views cannot produce a new pass. Historical single-view receipts remain historical evidence, without retroactive acceptance or silent invalidation. Generated media does not establish continuous review or human acceptance.
