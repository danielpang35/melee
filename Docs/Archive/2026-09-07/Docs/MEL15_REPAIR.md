> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# MEL-15 repair — progress evidence, 7 September 2026

> **Paused at user request, 7 September 2026.** This historical report is superseded for current state by [MEL15_IMPLEMENTATION_FRAMEWORK.md](MEL15_IMPLEMENTATION_FRAMEWORK.md) and [HANDOFF_MEL15_NEXT_INSTANCE.md](HANDOFF_MEL15_NEXT_INSTANCE.md). Last rendered module is1006; newer source intended for1007 remains unrendered after paging-file build failures. Human acceptance is pending.


**Status: implementation and visual iteration are ongoing. This repair is not accepted. Human visual acceptance is pending, and MEL-15 must remain open.** This snapshot covers rendered module **1004** and subsequent source work intended for **1005**. At the snapshot, the 1005 engine build is in progress; no completed 1005 module or footage has been verified. Passing scripted checks has already failed to identify visibly bad wrists and arm silhouettes.

This document records what has been measured and rendered so far. It does not claim final animation quality, complete first-person regression coverage, or a finished before/after comparison. `README.md` and `VALIDATION.md` have not been rewritten as a final result.

**Starting state and preserved evidence**

The task began with substantial local changes. The checkout was inspected and retained; useful hand anatomy, continuous glove geometry, hip-pivot lean, movement, and earlier presentation work were not discarded by resetting to HEAD. The baseline is that existing local state, rather than the repository's last committed revision. Its source hashes are recorded in [baseline-hashes.json](../../../../Saved/MEL15/baseline-hashes.json), with source and asset snapshots under [BaselineSource](../../../../Saved/MEL15/BaselineSource) and [BaselineAssets](../../../../Saved/MEL15/BaselineAssets).

The fresh rendered baseline contains **1,200 PNG frames across all 18 air-review scenarios**, captured with the logged `-UseFixedTimeStep -FPS=30` command. It loaded the unsuffixed `UnrealEditor-MeleeCombatLab.dll`. The originals remain in [MEL15_Baseline](../../../../Saved/ArmRepair/MEL15_Baseline); [the engine log](../../../../Saved/Logs/MEL15BaselineRetry.log) records the actual scenario and screenshot sequence.

[BaselineClips/README.md](../../../../Saved/MEL15/BaselineClips/README.md) links the eight requested horizontal/upper-cut baseline packages. The [baseline manifest](../../../../Saved/MEL15/BaselineClips/baseline-manifest.json) accounts for each source PNG exactly once and records SHA256 hashes, source filenames, log lines, engine-frame indices, and wall timestamps. The original external camera was the legacy inspection offset `(210,260,80)`; those clips are labelled accordingly. Their upper cuts are 60° and 120°, while the first two new overhead candidates below explicitly requested 90°. They are useful iteration evidence, but not a final comparison with identical attack and camera settings.

Baseline phase telemetry was not recorded. Its per-frame simulation time is reconstructed from logged engine-frame differences and the logged fixed FPS; `phase=UNRECORDED` is deliberate. The first frame is about 33 ms into the attack, rather than an exact zero-time guard freeze. A screenshot logged on the next scenario's BEGIN frame belongs to the outgoing capture request and is flagged as a transition frame.

**Measured causes of the arm-chain failure**

The original problem was not explained by an elbow sign alone. [The baseline rig diagnosis](../../../../Saved/MEL15/BASELINE_RIG_DIAGNOSIS.md) reconstructed rigid bone transforms from imported, CPU-skinned surfaces and preserved the old reference skeleton for subsequent comparisons.

| Imported reference measurement | Original rig | Rebuilt rig |
|---|---:|---:|
| Shoulder → elbow | 26.093865 cm | 30.413807 cm |
| Elbow → wrist | 21.216316 cm | 25.387002 cm |
| Shoulder-pivot span | 55.184984 cm | 44.000000 cm |
| Clavicle length | 22.605897 cm | 17.013405 cm |

These dimensions come from the actual source/import pipeline, not an assumed mannequin. [The reference plot](../../../../Saved/MEL15/rest-rig-front-side.png) shows old rest vertices and bone locations; [the rebuilt reference measurements](../../../../Saved/MEL15/proportioned-rig-expected.json) agree with candidate 2's runtime `CITADEL RIG` log positions. New link lengths and narrower shoulder centers were authored and imported. They are not runtime bone stretching used to hide the original pose.

The glove's corrected handedness signs agreed across the Blender-to-Unreal conversion. However, its reference hand/forearm orientation and the desired grip frame conflicted with the arm pose. In the old neutral target, both transformed reference forearms pointed steeply downward. A wrist-led elbow solve therefore raised the elbows to satisfy the hand orientation. In the archived rendered neutral pose, the right elbow was **23.669 cm above** its shoulder and the left **13.212 cm above**. Low wrist-axis scores in those poses did not make the resulting anatomy acceptable. Merely pushing those elbows down would transfer the defect to the wrists.

Shoulder accommodation also broke the visible chain's joint attachment. The archived surface audit measured clavicle-end/upper-arm-pivot gaps up to **6.323 cm**. Candidate 2's external surface reconstruction reduced the maximum measured gap to **0.0000292 cm**, with an arm rigid-fit residual of about **0.000022 cm**. That establishes joint attachment in the measured poses. It does not prove complete shoulder-armor coverage or a convincing scapular silhouette; irregular rear shoulder armor still requires rendered review. See [candidate 2's independent review](../../../../Saved/MEL15/CANDIDATE2_RIG_REVIEW.md).

The authored hand path was another cause. The old upper cuts finished with grip center around **139.1/139.4 cm above the floor** even while the tip pointed down. The shared 43 cm hand-reach projection shortened and biased some paths, but the raw hand path itself was too high. [The trajectory audit](../../../../Saved/MEL15/trajectory-audit.md) separates raw, projected, and final-path observations instead of attributing the whole defect to projection.

**Architecture rendered in module 1004**

- [AttackTrajectory.h](../../../../Source/MeleeCombatLab/Combat/Attacks/AttackTrajectory.h) authors load, passage, and completed-cut grip poses, distinct horizontal origins, and a low overhead recovery turn. Shared shoulder centers now include chest pitch and independent shoulder elevation/depression.
- [MeleePresentationPose.h](../../../../Source/MeleeCombatLab/Visual/MeleePresentationPose.h) contains the shared actual `solveGripArm` implementation used by both native checks and the rendered arm solve. Its body-authored guide arm chooses hand pronation before the palm offset places the wrist; the final arm then uses that fixed orientation with bounded wrist assistance. This removes the former circular glove/wrist feedback loop. "Single pass" refers to this orientation decision: the helper still performs bounded shoulder fitting and guide/final two-link solves.
- [KnightPresentation.cpp](../../../../Source/MeleeCombatLab/Visual/KnightPresentation.cpp) passes the imported clavicle anchors, arm lengths, reference hand axes, palm offset, and chest-frame rail into that shared helper, then applies the returned shoulder, elbow, wrist, and hand frame to the actual bones. Native tests approximate the clavicle anchors; imported-mesh and rendered traces remain necessary. Per-frame traces record raw and projected hilt, shoulders, elbows, wrists, grips, wrist-axis proxy, and reach scale.
- [BuildCitadelArt.py](../../../../Tools/BuildCitadelArt.py) rebuilds the anatomical shoulder centers and arm proportions while retaining the established glove construction. [Topology checks](../../../../Saved/MEL15/proportioned-arm-topology.json) found no open or nonmanifold edges in the rebuilt arm/hand parts; [surface comparisons](../../../../Saved/MEL15/proportioned-glove-surface-verification.json) document the small glove changes rather than asserting byte-identical geometry.

The legacy FP shoulder shift of **+10 cm forward / −8 cm down** is removed (`ViewShift=ZeroVector`) in the module 1004 captures. The new shared solve and the lower carry/turn recovery are therefore rendered changes, but their remaining defects are recorded below. The source links above also contain later 1005 edits; they are not immutable copies of 1004.

The present `solveArm` still exposes a fallback reach scale for out-of-range targets. All 20 reviewed I3 scenario results report scale 1.0; full motion/pitch/stance coverage on the final module must establish that runtime stretching is not being used elsewhere. This remains a validation obligation.

**Rendered iterations and why they were rejected**

The values below are **wrist reference-axis angles**, a diagnostic proxy computed from the solved forearm and transformed hand reference. They are not clinical wrist-flexion measurements or a substitute for inspecting the rendered surface.

| Captured candidate | Verified loaded module | Measured worst external / FP wrist proxy | Status |
|---|---|---|---|
| I1, exact 90° overhead, side view, original proportions | `UnrealEditor-MeleeCombatLab-1002.dll` | 87.5200° / 93.5869° | Rejected; recovery lifted the hands before turning the downward blade. |
| I2, exact 90° overhead, side and first-person views, rebuilt rig | `UnrealEditor-MeleeCombatLab-1003.dll` | 55.1752° / 93.0225° | Rejected; late release and recovery still fold the chain, particularly in first person. |

Module identity is recorded in [the I1 log](../../../../Saved/Logs/MEL15_I1_OverheadSide.log), [the I2 side log](../../../../Saved/Logs/MEL15_I2_OverheadSide.log), and [the I2 first-person log](../../../../Saved/Logs/MEL15_I2_OverheadFP.log). [The I1 module hash](../../../../Saved/MEL15/iteration1-module.json) identifies module 1002. [The successful second build log](../../../../Saved/MEL15/build-iteration2.log) identifies the linked module 1003.

I1's 93.5869° FP value comes from the FP chain telemetry emitted during its side capture; it is not evidence of a separate I1 first-person recording. I2 has both rendered views. Each trace contains both solved views, so analyses must filter `view` before reporting a maximum.

| Evidence | Normal speed | Half speed | Frozen poses | Raw trace |
|---|---|---|---|---|
| I1 side | [MP4](../../../../Saved/ArmRepair/MEL15_I1_OverheadSide/Review/after_normal.mp4) | [MP4](../../../../Saved/ArmRepair/MEL15_I1_OverheadSide/Review/after_half_speed.mp4) | [Sheet](../../../../Saved/ArmRepair/MEL15_I1_OverheadSide/Review/after_keyposes.jpg) | [CSV](../../../../Saved/ArmRepair/MEL15_I1_OverheadSide/arm-traces.csv) |
| I2 side | [MP4](../../../../Saved/ArmRepair/MEL15_I2_OverheadSide/Review/after_normal.mp4) | [MP4](../../../../Saved/ArmRepair/MEL15_I2_OverheadSide/Review/after_half_speed.mp4) | [Sheet](../../../../Saved/ArmRepair/MEL15_I2_OverheadSide/Review/after_keyposes.jpg) | [CSV](../../../../Saved/ArmRepair/MEL15_I2_OverheadSide/arm-traces.csv) |
| I2 first person | [MP4](../../../../Saved/ArmRepair/MEL15_I2_OverheadFP/Review/after_normal.mp4) | [MP4](../../../../Saved/ArmRepair/MEL15_I2_OverheadFP/Review/after_half_speed.mp4) | [Sheet](../../../../Saved/ArmRepair/MEL15_I2_OverheadFP/Review/after_keyposes.jpg) | [CSV](../../../../Saved/ArmRepair/MEL15_I2_OverheadFP/arm-traces.csv) |

I2's worst FP sample occurs at **t=0.966667 s**, release progress **0.716667**, in [frame 34](../../../../Saved/ArmRepair/MEL15_I2_OverheadFP/Frames/frame_00034.png). The right elbow is ahead of and below the hand; the forearm runs backward and upward while the blade points down and forward. The hands and blade leave the screen during low carry, while the cuff remains prominent. At **t=1.400 s** the FP right-wrist proxy reaches another **80.2605°** peak during recovery. The scripted scenario still reports PASS, demonstrating that its present numerical gates are insufficient.

**Module 1004: five cameras rendered, remaining defects visible**

The [successful I3 build log](../../../../Saved/MEL15/build-iteration3.log) links `UnrealEditor-MeleeCombatLab-1004.dll`. Each capture log below independently records loading that module. Each set contains the four core origins **0°, 60°, 120°, 180°**, with standing stance and neutral pitch: **20 cut cases and 1,455 original PNG frames**, verified by counting the files and four results in each `results.json`. These are not exact-90° overhead captures.

| Camera | Captures and per-cut packages | Module log | Frames / cuts |
|---|---|---|---:|
| Side | [CoreSide](../../../../Saved/ArmRepair/MEL15_I3_CoreSide) | [Log](../../../../Saved/Logs/MEL15_I3_CoreSide.log) | 291 / 4 |
| First person | [CoreFP](../../../../Saved/ArmRepair/MEL15_I3_CoreFP) | [Log](../../../../Saved/Logs/MEL15_I3_CoreFP.log) | 291 / 4 |
| Front | [Views_front](../../../../Saved/ArmRepair/MEL15_I3_Views_front) | [Log](../../../../Saved/Logs/MEL15_I3_Views_front.log) | 291 / 4 |
| Rear three-quarter | [Views_rear3q](../../../../Saved/ArmRepair/MEL15_I3_Views_rear3q) | [Log](../../../../Saved/Logs/MEL15_I3_Views_rear3q.log) | 291 / 4 |
| Defender | [Views_defender](../../../../Saved/ArmRepair/MEL15_I3_Views_defender) | [Log](../../../../Saved/Logs/MEL15_I3_Views_defender.log) | 291 / 4 |

Each `Split/<scenario>/Review` contains normal-speed and half-speed MP4s and a nine-pose sheet. The [FP review](../../../../Saved/MEL15/I3_CoreFP_VISUAL_REVIEW.md) and [front/rear/defender review](../../../../Saved/MEL15/I3_EXTERNAL_VIEWS_REVIEW.md) link the inspected sheets and original problem frames. [Video validation](../../../../Saved/MEL15/I3_external-views-validation.json) confirms decoding, frame counts, and hashes for those three external cameras. Encoding a normal-speed video and inspecting static frames do not establish continuous normal-speed viewing or human acceptance.

The upper-cut hands now descend from above the helmet to the abdomen/waist region; the 60° hilt is about **104.60 cm above the floor** at recovery frame 114. The sampled external poses demonstrate actual low hand carry. However, front and defender recovery show nearly vertical upper arms and a tight forearm shelf across the abdomen, with sharply turned hands around the downward handle.

| I3 core origin | Worst external / FP wrist proxy | Recorded time / frame |
|---|---:|---|
| 0° right | 54.2374° / 50.3940° | 1.266667 s / 43 |
| 60° upper right | 75.8532° / 76.5188° | 1.233333 s / 114 |
| 120° upper left | 59.7709° / 59.5684° | 1.266667 s / 188 |
| 180° left | 54.4036° / 47.8818° | 0.566667 s / 240 |

These maxima come from all recorded per-frame samples, joining four ordered trace rows per image to the scenario/time metadata; they are not maxima inferred from nine selected poses. [The joined FP trace analysis](../../../../Saved/MEL15/I3_CoreFP-trace-review.json) retains both solved views and flags the four attack-start frames whose presentation trace still says idle while scenario metadata says windup. These boundary labels do not affect the maxima above. The [I3 rig diagnosis](../../../../Saved/MEL15/I3_RIG_RECOVERY_DIAGNOSIS.md) records a side-view clavicle-end gap of at most **0.0000336 cm** across its sampled exports, yet rear shoulder plates still show jagged dark flaps and irregular coverage. Numerical joint attachment does not certify the shoulder surface. Loaded forearms also crowd the helmet silhouette; projected overlap alone is not proof of mesh penetration.

**User decision on first-person framing:** the weapon briefly leaving the first-person viewport during the low carry is acceptable. This supersedes the earlier FP review's treatment of that exit as a framing objection. It does not approve the remaining wrist articulation, hidden arm clearance, shoulder coverage, or the full animation; human animation acceptance is still pending.

**Source changes intended for module 1005 — engine build and rendering pending**

The next source iteration adds arm-role-dependent recovery rails: the trailing arm receives more forward support on diagonal overheads, with both arms supported near 90°. The [I3 feasibility diagnosis](../../../../Saved/MEL15/I3_RIG_RECOVERY_DIAGNOSIS.md) explains why applying the same rail to both diagonal arms can improve one and spoil the other. Exact-vertical finish authoring also keeps the grip moving forward and sets a floor-safe endpoint before constructing the hand arc, avoiding the old sample-wise floor correction's dip and rebound. These changes have native geometric evidence but no verified 1005 rendered evidence in this snapshot. [The in-progress engine build log](../../../../Saved/MEL15/build-iteration4.log) must show a completed module, followed by fresh identified captures, before they can replace 1004 observations.

The older [recovery-authoring note](../../../../Saved/MEL15/recovery-authoring.md) and [recovery audit](../../../../Saved/MEL15/recovery-audit-summary.txt) remain historical records. Later [endpoint recovery samples](../../../../Saved/MEL15/recovery-endpoint-summary.txt) test the current path; none of these native outputs substitute for inspecting the final rendered exact overhead.

**Gameplay evidence and remaining acceptance work**

The original 43 cm authoritative hand envelope and the starting strike timings remain part of the current design. The collision sweep still uses the authoritative weapon path. Trajectory edits nevertheless change per-family geometry; they must not be described as having no gameplay effect. [Contact-timing comparisons](../../../../Saved/MEL15/contact-timing-comparison.json) record unchanged neutral horizontal/upper-cut contact at the 240 Hz sampling resolution, with some accel/drag samples shifting by one tick. [Reach comparisons](../../../../Saved/MEL15/reach-comparison.json) record per-family reach changes. The dense native sweep reports **158.446 cm** maximum forward extent, within the prior theoretical **158.451 cm** global envelope.

Test counts below are tied to their saved provenance. This document update did not run tests or overwrite any test log. Some generic `trajectory-*-tests.txt` filenames have been reused by later native runs; the older counts remain historical observations, not claims about those files' present contents.

| Recorded source/test stage | Checks reported | Provenance and limit |
|---|---|---|
| Earlier trajectory/recovery work | 74,153 swing; 605 combat; 1,413,494 presentation | Preserved in [trajectory audit](../../../../Saved/MEL15/trajectory-audit.md) and [recovery-authoring note](../../../../Saved/MEL15/recovery-authoring.md); predates the shared actual grip solver. |
| I3 shared actual grip solver | 1,983,430 presentation | [Saved I3 result](../../../../Saved/MEL15/grip-iteration3-results.txt); worst native wrist proxy 86.0783° at 90°/pitch +85°. Native approximate anchors, not the exact imported UE chain. |
| I3 regression logs | 605 combat; 46 movement; 322 audio | [Combat](../../../../Saved/MEL15/combat-iteration3.log), [movement](../../../../Saved/MEL15/movement-iteration3.log), [audio](../../../../Saved/MEL15/audio-iteration3.log). These precede the later endpoint edits. |
| Intermediate next-source rail pass | 1,983,430 presentation | [Rail iteration log](../../../../Saved/MEL15/grip-iteration4.log); worst native wrist proxy 72.6392°. This is an intermediate source result, not module 1005 footage. |
| Latest native source outputs at this snapshot | 918,139 swing; 2,363,350 presentation; 605 combat | [Swing](../../../../Saved/MEL15/trajectory-swing-tests.txt), [presentation](../../../../Saved/MEL15/trajectory-presentation-tests.txt), [combat](../../../../Saved/MEL15/trajectory-combat-tests.txt), recorded about 01:38–01:40 EDT. Presentation reports 65.0002° worst wrist proxy, 4.32822° maximum transported hand-roll step at 240 Hz, and reach scale 1. These results do not certify the pending UE build or visual acceptance. |

The five-camera standing/neutral matrix exists for module 1004. Moving, crouched, and high/low-pitch rendered coverage, exact 90° review, and refreshed relevant cameras remain necessary for the final compiled candidate. [The core-set harness](../../../../Source/MeleeCombatLab/Tests/CombatPlaytest.cpp) and [matrix runner](../../../../Tools/MEL15CaptureMatrix.ps1) allow four cuts per process while retaining global and per-scenario frame metadata. [The packaging helper](../../../../Tools/MEL15SplitReviewSet.py) preserves original PNGs and recorded timing. [The validation run plan](../../../../Saved/MEL15/validation-plan.md) separates final native checks, engine automation, and the complete 56-scenario combat tour; this snapshot does not claim those final-module runs have finished.

Remaining acceptance requires normal-speed visual review, exact overhead hilt follow-through review, FP wrist/clearance checks with the new recovery rails, shoulder-armor inspection, and gameplay/contact regressions on the final compiled module. **No current evidence supports closing MEL-15 or claiming the requested animation quality has been reached.**
