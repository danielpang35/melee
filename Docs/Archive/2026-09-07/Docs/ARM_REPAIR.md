> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# Arm mesh and grip repair — 6 September 2026

> Follow-up: continuous gloves, shared hip-pivot lean, camera clearance and current evidence are documented in [HANDS_AND_LEAN.md](HANDS_AND_LEAN.md). The limitations and results below describe this earlier checkpoint.

This pass repairs the separated arm plates and the mismatched hand/forearm frames in the resumed working tree. It is a technical repair to the current procedural rig. The arms and gloves still need authored art and animation polish; the extreme-pitch camera problems described below remain open.

## What was wrong

The previous rigid-face conversion stopped triangles stretching, but left independently rotating pieces meeting at open seams. In the freshly captured baseline, coincident rest-pose seam vertices separated by as much as 24.66 cm. Those pieces could look like torn spikes even while the bone-length and triangle-edge tests passed.

There was also a grip-frame mismatch. The generated glove diagonal and the runtime source frame disagreed on the shear direction, and the left hand needed a mirrored source axis. Adjusting the target palm plane alone transferred the error between wrists and elbows. An intermediate wrist-led solver reduced wrist bending but lifted the elbows into the first-person camera; that trial was rejected during review.

## Repair

- Rebuilt upper arms, forearms, elbow cups and wrist joints as closed, overlapping rigid shells. Added closed shoulder sockets and a fitted cloth torso underlayer beneath the original armor. First person keeps complete arm sections rather than cutting through a sleeve at a height threshold.
- Matched the generated diagonal grip cavities to mirrored runtime grip axes. Palms use opposed blade-edge frames; both hand contacts remain on the existing sword handle.
- Made the elbow solver account for the glove's forearm direction, with a resting-pole preference and a bounded angular change between frames. Forearm pronation follows the glove instead of an unrelated shortest-arc rotation.
- Added up to 6 cm of additional shoulder accommodation under wrist strain. Ordinary relaxed poses retain their body-driven anchor. Existing reach accommodation and fixed arm lengths remain in place.
- Persisted skeletal-material usage for the gloves and a separate arm-steel material, with an asset reload regression check for all three slots.

The gameplay weapon path, collision, timing and combat tuning were not changed by this arm repair. The rig follows the simulation. Other uncommitted movement, swing and audio work in this shared checkout is separate from this pass.

## Evidence and repeatable review

`-ArmPoseAudit` exports actual CPU-skinned vertices at four times per motion scenario. `Tools/AnalyzeArmPoses.py` fits the rigid arm transforms, counts open arm-surface edges after welding imported UV/normal seams, and measures the angle between the forearm and the hand's reference forearm axis. This angle is a wrist-bend proxy, not a clinical joint measurement. Neither it nor a triangle-edge ratio proves that a pose looks good.

The analyzer requires NumPy and can use the existing `Saved/ArtRuntime` installation. From repository root:

```powershell
python .\Tools\AnalyzeArmPoses.py .\Saved\ArmRepair\ReleaseReview --require-closed-arms --output .\Saved\ArmRepair\ReleaseReview\wrist-analysis.json
```

Review controls added to the existing playtest:

- `-ArmReviewTag=NAME` isolates logs' companion captures/results under `Saved/ArmRepair/NAME`.
- `-MotionReviewScenario=38` through `55` selects one scenario when `-MotionReview` is enabled.
- `-AllMotionFrames` records every motion-review scenario instead of the default five selected clips.

The before/after preview uses the fresh module-1004 baseline from this resume, not the previously rejected published montage. It shows five matching first-person/external scenarios at normal speed and half speed. The contact sheets cover all seven attack directions in each view and retain the extreme-pitch problems in a separate sheet.

These are silent frame sequences captured with a fixed 30 Hz simulation step. Slow motion repeats captured frames; it does not synthesize intermediate poses. The CSV view coordinates use the combatant's view, including when the rendered camera is in external inspection mode.

## Remaining visual limitations

At +85 degrees pitch, the existing world-space weapon reach envelope can put the grip behind the camera's near plane. Portions of the sword guard and gloves clip; this is not triangle stretching. At -85 degrees, the first-person mesh exposes its capped shoulder ends because the upper torso is omitted. Correcting this needs a deliberate camera/weapon/torso composition pass with collision-readability checks.

The replacement arm shells are simple smooth surfaces, and the closed gloves remain blocky. Some extreme third-person poses still bend the wrists substantially. A rear shoulder opening in the coarse original torso remains visible in some external poses despite the added backing; the zero-boundary test covers the arm links and hands, not the original torso/pauldron surfaces. These are not final Mordhau-quality animations, and no 144-fps performance claim is made from the screenshot capture run.

## Verified results

- UE 5.8 Editor Development build succeeded. Latest fitted-mesh import completed with 0 errors and 0 warnings reported by the commandlet.
- Native presentation suite: **1,413,852 checks passed**, with MSVC `/W4 /WX` and AddressSanitizer.
- Final rendered review: **18/18 scenarios passed**, with **72 skinned-pose captures / 144 arm samples**. All six cuts, stab, first-person/external views and +/-85-degree pitch were exercised. The last asset review records five continuous clips and four pose screenshots for each remaining scenario.
- **0 open arm boundary edges** after welding imported seams, versus a worst per-arm count of **120** in the freshly captured broken baseline. The strict check was also run against the baseline and correctly rejected it.
- Matched right-horizontal samples: worst wrist-axis angle **105.712 degrees before / 38.973 degrees after**. Across the final complete sample set, the maximum is **70.025 degrees**. The baseline comparison contains four poses; do not imply it covers all eighteen scenarios.
- Maximum rendered blade discrepancy: **0.000034 cm**. Maximum arm triangle-edge ratio: **1.000128**. These are numerical correctness checks, not visual approval.
- Fresh Unreal automation: **4/4 passed**, with 0 test warnings: Citadel asset contract, state flow, frame-rate equivalence and audio asset bank. An earlier audio run failed while those independently added sound assets were missing; the fresh run passed after they became available.
- No Saved combat-tuning override is active. All review processes launched for this repair exited.

Review artifacts:

- [Before/after video](../../../Visual/Captures/ArmRepair/before-after.mp4)
- [Selected continuous motion clips](../../../Visual/Captures/ArmRepair/selected-motion.mp4)
- [First-person pose sheet](../../../Visual/Captures/ArmRepair/first-person-poses.jpg)
- [External pose sheet](../../../Visual/Captures/ArmRepair/external-poses.jpg)
- [Unresolved pitch composition](../../../Visual/Captures/ArmRepair/pitch-limitations.jpg)
- [Rendered checks](../../../Visual/Captures/ArmRepair/rendered-review.json), [surface/wrist audit](../../../Visual/Captures/ArmRepair/wrist-analysis.json), [Unreal automation](../../../Visual/Captures/ArmRepair/automation-report.json)

Raw final captures are under `Saved/ArmRepair/ReleaseReview`; the engine log is `Saved/Logs/ArmReleaseReview.log`. Earlier iterations remain under `Saved/ArmRepair` for diagnosis. The previous handoff and rejected montage are historical and have not been replaced.

## Build and launch

The code and imported assets are saved locally, uncommitted. No ZIP application is necessary. Restart any already-open game to load the repaired module and meshes. From repository root:

```powershell
.\Tools\Build.ps1 -MaxParallelActions 2 -Launch
```
