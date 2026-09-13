> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# Paused handoff — fingers and hip-pivot lean

Resumed at the user's request on 6 September 2026. See [the lean implementation](HANDS_AND_LEAN.md) and [the subsequent hand anatomy correction](HAND_ANATOMY_CORRECTION.md). The user rejected the first glove pass as upside down; the new pass corrects mirrored handedness, thumb placement and finger geometry using `D:/Mordhau Montage VI.mp4`. Remaining swing wrist/forearm-clearance defects are documented for MEL-15. Earlier automated results do not establish visual acceptance. MEL-5 has been updated and the deferred rear shoulder issue exists as MEL-14. The pause-state details below are historical.

## Requested work

1. Update Linear with the previous arm repair and create a separate issue for the **rear shoulder opening**. Defer repairing that opening.
2. Fix the blocky, disconnected-looking fingers shown in the user's screenshot.
3. Make looking up/down bend the torso about the hips, enabling leanbacks/ducks and improving first-person clipping.

Screenshot: `C:/Users/DANIEL~1/AppData/Local/Temp/codex-clipboard-698b064f-b7f2-454f-b41a-5275194fefda.png`.

## Actual state at pause

- **Linear: no writes performed.** No Linear tools or plugin-search tools were exposed in this task. A question about connection/team/project was pending when the user requested this pause. Recheck available integrations when resuming; do not claim an issue exists.
- **Fingers: diagnosis only; no mesh changes in this pass.** `Tools/BuildCitadelArt.py` generates each phalanx as a separate beveled cube and the palm as a rectangular block, then shears the hand diagonally. These produce the visible broken knuckles/palm slabs. Replace with continuous curved, tapered glove geometry fitted to the actual estoc handle. Keep four fingers and a thumb readable and preserve the runtime grip calibration, or update both together.
- **Lean: partial source edits only**, listed below. Camera, renderer, simulation implementation, collision call sites, and tests still use the old interfaces. **Expect compilation failures until the integration is completed or these specific edits are reversed.** Existing built binaries/assets predate this partial pass.
- No commit, push, ZIP, or new runtime capture was made.

## Partial edits made in this pass

- Added `Source/MeleeCombatLab/Combat/CombatBodyPose.h`: pure `BodyFrame`, with a fixed hip pivot 87.35 cm below the upright eye, forward/inverse transforms, and an eye position following the lean arc.
- `Combat/CombatTuning.h`: added `TorsoPitchScale`, default **0.75** (provisional and untested), range 0–1.
- `Combat/Attacks/AttackTrajectory.h`: `shoulder()` now requires a torso-pitch argument; `world()` accepts an optional lean fraction, moves the eye and shoulders about the hips, and rotates the 18 cm weapon-origin offset with the torso.
- `Combat/CombatSimulation.h`: added `torsoPitchScale`, `leanFraction`, `uprightEye()`, `bodyFrame()`, `eye()`, `hurtAxes()` (two capsules joined at the hips), `region()` (contact classification in unleaned coordinates), and an optional `constrainLean` callback. Removed the old single `hurtAxis()` method.

These edits are an initial implementation direction, **not a validated design**. In particular, the new scale/fraction fields are not yet synchronized with tuning/reset/advance, and the obstruction callback is not called or implemented.

## Resume checklist

1. Read current source and preserve the dirty working tree; other work, including audio, was already present. Previous completed repair and evidence are in `Docs/ARM_REPAIR.md`.
2. Wire the shared body frame through `CombatSimulation.cpp`: reset/advance, weapon-origin inverse capture, motion decomposition, collision against both hurt axes, nearest-axis contact normals, and head/body classification. Update `MeleePresentationPose.h` for the new shoulder signature and torso-relative elbow poles.
3. Update `KnightPresentation.cpp`: rotate upper-body bones about the actual pelvis pivot while keeping legs grounded; use the same frame for arm anchors and audit eye. Apply any first-person shoulder composition offset in the leaned torso frame. Current code still bends only for attack motion and keeps aim shoulders in yaw space.
4. Update `MeleeCharacter.cpp` camera position from the shared eye. In `CombatLabGameMode.cpp`, stop reading the camera's resulting Z back into `Simulation.eyeHeight` (that would feed lean back into itself). Derive the upright crouch eye height from capsule dimensions, update debug hurt volumes and eye-dependent feedback, and add world clearance that constrains the **shared lean**, rather than only moving the camera. Decide guard anchoring explicitly and preserve defense correctness.
5. Rebuild continuous fingers/palm/thumb in `Tools/BuildCitadelArt.py`; inspect the handle's cross section before setting the grip cavity. Current runtime calibration in `KnightPresentation.cpp`: rest finger direction, rest palm normal, diagonal grip axis `mirroredAcross + finger * .8`, and palm offset `finger * 4.5 cm + palm * 2 cm`. Avoid changing one side of that contract alone.
6. Replace the old presentation test that demands identical shoulder positions at ±85°: the new requirement is a fixed hip pivot with shoulders/eyes following it. Add meaningful collision regressions for lean/duck misses, hits on the moved torso, lower-body coverage, crouch, head classification, obstruction, and frame-rate equivalence. Retain blade/renderer agreement and existing parry/chamber tests.
7. Build, import, and visually inspect focused neutral/down/up views before full motion validation. Verify fingers, wrist alignment, camera clearance, torso attachment, and actual dodge behavior. Then update Linear with verified results and the deferred shoulder issue.

## Useful existing commands / evidence

From repository root, after completing integration:

```powershell
.\Tools\Build.ps1 -MaxParallelActions 2
.\Tools\TestCore.ps1 -Sanitize
.\Tools\TestCore.ps1 -Sanitize -PresentationOnly
```

Rig-only DCC rebuild helper: `python Saved/MotionRevision/build_rig.py`; Unreal importer: `Tools/ImportCombatRig.py`. Both were used in the previous completed repair. Do not rebuild/import until geometry is ready.

Existing motion-review scenarios: 38–44 first-person attacks, 45–51 external attacks, 52/53 first-person up/down at ±85°, 54/55 external up/down. `-MotionReviewScenario=N` isolates a case; `-ArmReviewTag=UniqueName -ArmSkinAudit -ArmPoseAudit` isolates evidence. Preserve user-owned Unreal processes; the build script supports a fresh numbered module when the default DLL is locked.

Previous completed evidence: `Saved/ArmRepair/ReleaseReview`, `Saved/ArmRepair/ReleaseAutomation`, and `Docs/Visual/Captures/ArmRepair/`. Previous results were 18 motion checks, 4 Unreal automation tests, and 1,413,852 native presentation checks passing; **none validate this unfinished pass**. The prior matched swing wrist proxy improved from 106° to 39°, but rear shoulder opening and extreme-pitch clipping remained visible.
