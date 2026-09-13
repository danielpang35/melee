> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# Continuous gloves and hip-pivot lean â€” 6 September 2026

**Glove appearance superseded:** the user rejected this first pass as upside down. See [the subsequent hand anatomy correction](HAND_ANATOMY_CORRECTION.md), its Mordhau reference, final evidence, and remaining animation limitations. Technical results below do not establish visual acceptance.

Implementation resumed from `HANDOFF_HANDS_AND_LEAN.md`. Work remains local and uncommitted in the existing shared checkout. This document describes this pass; previous arm-repair results remain in `ARM_REPAIR.md`.

## Behavior

Looking up bends the torso backward about the hips; looking down bends it forward. The camera, upper-body bones, arm anchors, weapon origin and upper hurt capsule follow the same body frame. The lower hurt capsule and leg roots stay grounded. Default torso pitch is 75% of view pitch, giving up to 63.75 degrees of torso bend at the existing Â±85-degree look limits. `TorsoPitchScale` is exposed in tuning and saved in CombatDefaults.

The two hurt capsules meet at the hips. Strikes now resolve against the moved torso as well as the grounded lower body. Head feedback classifies contacts in the unleaned anatomical frame. Contact normals use the closest point on the capsule union. Existing collision priorities, damage, attack clocks, turn caps and the 700 ms combo windup are retained.

The parry box and cone retain their existing rate-limited orientation and shape. Their anchor translates by the eye's lean displacement. The guard is not rotated twice by view and torso pitch. Native parry/chamber regressions cover the existing contracts.

World clearance sweeps the moving torso/head along small steps of the hip arc and returns the first safe fraction. That fraction constrains simulation, camera and renderer together. Camera position is never fed back into the upright eye height. The first-person camera uses a 2 cm perspective near plane inside its 6 cm world-clearance sphere; the default 10 cm plane sliced raised glove surfaces that remain ahead of the eye. This changes projection only, not the camera position, weapon path or hurt volumes. The engine audit puts a temporary blocking wall behind a probe combatant and checks unrestricted, blocked and crouched cases.

The character's crouched capsule half-height is now 60 cm (standing remains 88 cm). Unreal's 40 cm default put the fixed 87.35 cm hip-to-eye torso's pivot below the floor. Upright eye height is derived from capsule half-height minus 6 cm. This is an intentional crouch-clearance change and means openings between 80 and 120 cm tall no longer admit a crouched character. Crouched movement speed is unchanged.

## Glove and waist geometry

Replaced separate beveled palm/phalanx boxes with continuous tapered finger curves, an opposed thumb and a rounded palm. Each glove is a single connected, closed surface including its wrist joint. At the default 110 cm blade calibration, a fitted 24 mm radius cavity follows the measured estoc handle; source cross sections at the two grip contacts are roughly 42â€“46 mm across. Boolean numerical fragments smaller than 0.1 mm are removed, while substantial disconnected anatomy fails the DCC build. The gloves have approximately 16,850 source vertices each.

The generator accounts for the handedness change from Blender to Unreal when constructing the diagonal grip axis. The runtime hand contacts and palm-centre calibration remain fixed. The first rendered iteration exposed a cross-product sign error, which was corrected before final validation. That iteration is retained only under Saved/HandsLean and is not the delivered result.

A rounded gambeson insert backs the original open waist where hip bending exposed it. The separately deferred rear shoulder opening remains MEL-14; it was not repaired here. Three material slots (original armor, glove/joints, arm steel) and their persisted skeletal usage are retained.

## Validation

Native MSVC /W4 /WX + AddressSanitizer results:

- 605 combat checks, including 38 new lean checks: real resolving leanback/duck misses, hits on the displaced torso, lower-body coverage, crouch, head classification, blocked/intermediate lean and 30/60/144/240 fps equivalence.
- 1,413,854 presentation checks, including hip/shoulder frame agreement and the existing two-hand reach and blade contracts.
- 1,073 swing checks.
- 46 movement checks.

The neutral engine clearance audit measured full lean in open space, 0.51038 lean fraction against the test wall, and full lean in the crouched -45-degree probe. Neutral/up/down views in both perspectives were rendered and inspected. The first full motion audit passed 18/18 scenarios and all 72 skinned captures / 144 arm samples had zero open arm boundary edges. Maximum rigid-fit error was 0.000022 cm; the worst wrist-axis proxy remains 70.025 degrees. Camera projection was subsequently corrected after visual review caught the near-plane issue; final results below identify that later capture separately.

## Review and reproducibility

`Saved/HandsLean/checkpoint.json` records SHA-256 source, configuration and mesh hashes. Build/import logs are in Saved/HandsLean and Saved/Logs/HandsLean*. Skinned samples are isolated under Saved/ArmRepair/HandsLeanFinal; the final 2 cm near-plane capture is under Saved/ArmRepair/HandsLeanReleaseMotion. The camera-only projection change does not change those skinned poses. Earlier reference/repair captures have been preserved.

Repeatable commands:

```powershell
.\Tools\Build.ps1 -MaxParallelActions 2
.\Tools\TestCore.ps1 -Sanitize
.\Tools\TestCore.ps1 -Sanitize -PresentationOnly
.\Tools\TestCore.ps1 -Sanitize -SwingOnly
.\Tools\TestCore.ps1 -Sanitize -MovementOnly
```

Use `-CombatPlaytest -CombatPlaytestQuit -MotionReview -ArmSkinAudit -ArmPoseAudit -LeanClearanceAudit -ArmReviewTag=UniqueTag -UseFixedTimeStep -FPS=30` for the full rendered motion audit. Add `-NeutralPoseReview -MotionReviewScenario=38` (or 45/52/53/54/55) for stationary inspection. The wall-clearance regression runs in scenario 38 only. `-NeutralPoseReview` does not certify attack animation.

The gloves and armor remain procedural prototype art. Technical gates support visual inspection; they do not establish final AAA animation quality or packaged performance. Third-person follow-through and wrist polish are separate animation work, and the rear shoulder opening remains deferred.

## Current evidence

- [First-person pose sheet](../../../Visual/Captures/HandsLean/first-person-poses.jpg)
- [External pose sheet](../../../Visual/Captures/HandsLean/external-poses.jpg)
- [Extreme-pitch pose sheet](../../../Visual/Captures/HandsLean/pitch-poses.jpg)
- [Selected motion preview](../../../Visual/Captures/HandsLean/selected-motion.mp4)
- [Checkpoint hashes](../../../Visual/Captures/HandsLean/checkpoint.json)

Fresh engine automation after the concurrent audio import passed **4/4** tests with no test warnings: Citadel assets, state flow, frame-rate equivalence and audio asset bank. The earlier attempt failed the concurrently changing audio asset test; its original failure report remains under Saved/HandsLean/Automation. The successful report is under Saved/HandsLean/AutomationRelease.

The initial 30 Hz full tour exposed two outdated test assumptions: the crouch check required a half-height below 60 cm, and the feint-to-parry fixture scheduled its action inside a 20 ms window that a 33.3 ms frame could skip. The crouch test now checks the configured size and an above-ground hip; the parry action triggers once when its deadline is crossed. The initial 54/56 report is retained in Saved/HandsLean/full-tour-before-fixture-fix.json. Neither fix changes production combat timing.

Final projection review: **18/18 motion scenarios passed**, with 333 recorded frames across five selected continuous clips. Maximum rendered blade discrepancy is **0.000034 cm**, maximum arm reach scale **1.0**, and maximum arm triangle-edge ratio **1.000255**. The pose sheets include all six cuts, stab and extreme up/down in first-person and external views. The short selected-motion video is silent, fixed-step 30 Hz footage; it is not a performance benchmark. At extreme upward windup the close gloves still occupy much of the frame, but the cut-through surfaces from the 10 cm near plane are resolved.

The final build also updates only two playtest fixtures described above. `Saved/HandsLean/motion-checkpoint.json` records the capture binary; `checkpoint.json` records the later fixture build. Production camera, simulation and mesh hashes are unchanged between those two builds.

The fresh full in-engine gameplay tour after those fixture corrections passed **56/56** scenarios at 30 Hz, including feint-to-parry, crouch/uncrouch, chamber, riposte, input, movement and the final presentation cases. [Full tour report](../../../Visual/Captures/HandsLean/full-tour.json). All review/import/automation processes launched for this pass have exited. No user process was terminated, no ZIP was applied, and no commit or push was made.

Linear: MEL-5 records the verified previous arm repair and this resumed handoff. [MEL-14 — rear shoulder opening](https://linear.app/meleeslasher/issue/MEL-14/close-the-rear-shoulder-opening-beneath-the-knights-pauldron) remains explicitly deferred. Broader visual acceptance and third-person animation polish remain separate from this implementation checkpoint.
