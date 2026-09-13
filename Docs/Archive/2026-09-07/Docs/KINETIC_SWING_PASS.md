> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# Kinetic swing revision — 6 September 2026

## Problem and reference

The blade rotated through a much larger angle than the visible hands appeared to travel. The previous anatomical reach correction compressed the hand path, and much of the first-person grip motion was below the frame. A zero-speed release ending also removed the sense of committed follow-through.

Primary visual reference: the user-supplied **Mordhau Montage VI.mp4**, particularly the exchange at approximately 2:44–2:46. The visible hands load across the view, travel together with the weapon, and reorient for the next action. The montage is used for pose and spatial relationships, not to infer exact game timing from edited footage. GregTage VII was inspected earlier and superseded as the preferred reference. The YouTube page could not be fetched; the local video copies were inspected as extracted frame sequences.

Sol's supplied diagnosis was checked against the current repository. Its quadratic front-load formula was already superseded, but the current curve still decelerated to zero at the end of release and the independent hilt/blade construction remained a problem.

## Implemented motion

- The grip centre follows a 132-degree arc. The guard is its rigid extension along the blade axis. Blade travel is reduced from 212 degrees to a tunable 160-degree arc, from +78 to −82 degrees.
- The grip plane, rest pose, stab and recovery-ready pose are raised so that hands and forearms participate visibly in first person. First-person shoulders and elbow poles remain separately posed; they need not copy the external view.
- Shoulder accommodation replaces the separate wrist-target clamp. The rig retains fixed link lengths and exact calibrated handle contacts rather than leaving the hands short of the sword.
- The first-person mesh omits upper shoulder plates and torso geometry above the waist. Third-person armor is retained. The coarse source mittens are replaced with shaped palms, four curled fingers and thumbs; the palm axis and handle-cavity offset are calibrated to the exported skeleton.
- `StrikeReleaseAcceleration` replaces `StrikeReleaseFrontLoad`. Regular progression is a tunable blend between linear travel and `0.35p + 1.45p² − 0.8p³`. At strength 0.85, initial speed is 0.4475 times average, peak speed occurs near p=0.604, and exit speed is 0.8725 times average. Riposte blade-angle progression is linear.
- Hermite endpoint tangents connect windup to release and release to recovery. Body yaw/lean/shoulder transfer also matches the release boundary tangent. Combo windup captures prior local velocity rather than restarting from a stationary pose.
- Miss and body-hit recovery use different carry distances. Parry and wall responses use different directional rebound distances and blade redirection.

## Timing and movement

Compared 650, 620, 610 and 575 ms windups at a fixed 500 ms release. Selected 575 ms: it restores useful contact speed and preserves the existing test that prohibits a stationary repeated-parry sequence. The 610 ms experiment violated that rule. No parry duration/recovery change was used to hide that result. Combo windup remains 700 ms.

Yaw caps remain 255 / 245 / 220 degrees per second. Pitch is 185 degrees per second, retaining the existing riposte scale. Mouse turning changes spatial travel, never the attack clock.

Release drive peaks before mid-release and ends at 72% of release. The default drive adds about 17.1 cm of forward travel to the controlled native movement fixture. It requires forward input, halves while crouched, stops on reversal, and does not target opponents. Excess incoming forward momentum is partially retained and decays; strafe and braking authority remain in the movement solver. Character translation feeds the authoritative weapon sweep.

The neutral guard box receives an 18 cm chest offset to meet the raised weapon plane. This offset tapers to zero at 45 degrees of pitch so that the established pitched foot-coverage contracts remain intact. Width, height, depth, parry clock and chamber rules are unchanged.

## Contact and diagnostics

Body contact uses a brief 65 ms spatial deceleration pulse while leaving elapsed attack time unchanged. Directional torso, shoulder and elbow shock receives the contact direction. Walls provide the engine impact normal; body feedback uses capsule-entry geometry. The rendered sword continues to use authoritative endpoints. Directional camera response is restrained; particles remain spatial and result-specific. Existing synthesized impact audio is retained and is not a claim of finished sound design.

Launch with `-SwingTelemetry` to write `Saved/SwingTelemetry.csv` at every 240 Hz combat step. Columns include phase, p/q, local and world motion, intrinsic angular speed, yaw/pitch rates and utilization, damage state, release rotation, inherited/drive velocity and displacement, world hilt/tip velocity, and reach correction. F3 draws sweeps from blue to red by tip speed.

Velocity decomposition is an ordered finite-difference decomposition: intrinsic/body motion, then yaw, pitch, then translation. The four world contributions sum to final tip velocity. Inherited and lunge columns describe movement-solver contributions; they are subsets of translation and must not be added to it again.

`Tools/TestCore.ps1 -SwingOnly` writes `Tests/bin/swing-timing.csv` and `swing-steps.csv`. Timing tests cover all six strike families, all four candidate windups, neutral/accel/drag, player translation and a finite grid of starting yaw and manipulation rates. Reported earliest/latest values are sampled bounds, not mathematical extrema.

F2–F5 inherited Unreal debug view-mode bindings are removed because those keys are lab controls. In particular, F4 previously also enabled detail lighting when opening the tuning panel.

Scripted engine tests ignore hardware input at the viewport while retaining their injected PlayerController/Enhanced Input events. A real mouse movement previously turned a stab fixture roughly 104 degrees and produced a false miss. The setting is restored when the test ends and is not enabled during normal play.

## Validation

- UE 5.8 Development Editor build: module 9078 succeeded.
- Native combat suite with sanitizers: 567 checks passed.
- Presentation suite: 1,412,047 checks passed; maximum sampled hilt step 1.033 cm at 240 Hz, fixed arm reach scale 1.
- Swing timing/continuity/telemetry suite: 1,073 checks passed.
- Movement suite: 46 checks passed; controlled release drive added 17.10 cm.
- Full scripted engine tour: 56/56 passed on module 9073, after the final gameplay tuning and hardware-input isolation. Subsequent changes concern glove topology/materials and visual hand calibration.
- Final rendered review on module 9078: 18/18 passed; 333 frames captured at fixed 30 Hz. Asset/state/frame-rate automation: 3/3 passed with zero warnings, including glove material persistence after disk reload. [Preview](../../../Visual/Captures/KineticSwing/revised-combat.mp4), [pose sheet](../../../Visual/Captures/KineticSwing/poses.jpg), [rendered review](../../../Visual/Captures/KineticSwing/rendered-review.json), [automation](../../../Visual/Captures/KineticSwing/engine-automation.json).

Evidence: [full tour](../../../Visual/Captures/KineticSwing/full-tour.json), [timing samples](../../../Visual/Captures/KineticSwing/swing-timing.csv), [native step samples](../../../Visual/Captures/KineticSwing/swing-steps.csv), [240 Hz engine steps, gzip](../../../Visual/Captures/KineticSwing/engine-steps.csv.gz).

The running editor was left intact; restart it to load the rebuilt module and assets.

The source rig still uses stylized bulky armor. The new closed gloves have separate finger surfaces but remain a fixed grip without finger animation. The motion remains procedurally authored; these changes do not establish Mordhau-equivalent animation quality or subjective feel approval.
