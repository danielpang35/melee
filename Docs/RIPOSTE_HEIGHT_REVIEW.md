# Riposte height revision

> Dated evidence and assignments below are superseded for current execution by [DEVELOPMENT](DEVELOPMENT.md) and the [TP checkpoint](THIRD_PERSON_CHECKPOINT.md). See [documentation ownership](DOCUMENTATION_OWNERSHIP.md). Historical timing, candidate and issue status are not live values or authorization to resume deferred work.

User direction: lower the unusually high riposte, use Mordhau as the visual reference, and retain the smooth parry-to-riposte transition. Brief deformation during the exchange is acceptable; it is not a reason to block this height pass.

The standard trajectory added 12 cm of height at both release endpoints and 18 cm at mid-release, above the selected attack's own hand arc. Its Hermite windup inherited the current parry pose/velocity but aimed at that elevated endpoint. Removed the extra vertical lift. The forward hand drive, attack plane, riposte timing and input rules remain intact. The same authoritative path drives both collision and visible weapon attachment.

`Combatant::start` retains `local`, `localVelocity` and `bodyMotion`. `AttackTrajectory::windup` interpolates from that captured pose into the release, including the endpoint tangent. No new blend or reset through idle was added. This correction changes the destination of the existing transition.

The RC_v008 exact horizontal authored pilot bypasses this standard riposte trajectory. Its recorded windup guard peaks at 165.13 cm world height, compared with 203.20 cm desired / 199.53 cm resolved for the standard 60-degree riposte. These are different attack directions, not an artistic A/B. The authored pilot and its saved/baked source files were preserved; this is a runtime trajectory revision, not a new Cascadeur bake.

Reference inspection: supplied Hatchet VS Redblue recording at 7.167–8.000 seconds and Kronk K14-03 native frames at 4:55.800–4:56.167. The examples support connected hand transport through a guard/attack exchange. They also contain high guards and viewpoint changes; they do not establish an exact height or recovered riposte clock. The design choice is to remove our unconditional lift, not to claim that Mordhau never raises the hands. Inspected sequential images, not continuous audiovisual playback.

Before-state code and module manifest: `Saved/RiposteHeight/Before`. Matched baseline engine capture: `Saved/ArmRepair/RiposteHeight_before60` (module 1018, first person, 60-degree riposte, RC_v008 enabled).

## Verified result

Module 1019 built successfully. Combat tests: 917 checks passed. Performance tests passed (authored validation/phase clocks/rigid blade/direction scope/interruptions/return and the existing 240-direction presentation checks). The previously documented unrelated SwingOnly fixture failure was not rerun or represented as passing.

Matched 60-degree first-person capture: `Saved/ArmRepair/RiposteHeight_after60_fp`. External capture: `Saved/ArmRepair/RiposteHeight_after60_side`. Both pass the scripted parry → riposte → one hit → return sequence. Maximum geometric blade error is 0.000131 cm; active projection error is zero and maximum arm stretch is 1.0. No thresholds were relaxed for the user's tolerance of brief deformation.

| First-person world-height peak | Before 1018 | After 1019 |
| --- | ---: | ---: |
| Windup desired guard | 203.20 cm | 192.64 cm |
| Windup resolved guard | 199.53 cm | 192.64 cm |
| Windup front-hand grip | 189.27 cm | 182.38 cm |
| Release front-hand grip | 187.13 cm | 178.36 cm |

Reach projection explains why removing the full source lift does not produce that same difference in the rendered peak. The paired gloves sit lower in the matched load sample and clear downward sooner through release. The diagonal still has a high load appropriate to its selected direction. The close crossed-forearm silhouette remains bulky compared with the Mordhau reference; this pass does not claim a finished hand/body performance.

Attack phase durations are unchanged. Contact with this target occurs at attack 0.520833 seconds instead of 0.550000 seconds (29.17 ms earlier) because the authoritative spatial path changed. Both runs show the same successful incoming parry at scenario 0.983333 seconds and one outgoing hit. Detailed values: `Saved/RiposteHeight/comparison.json`.

Normal-speed A/B: `Saved/RiposteHeight/before-left_after-right.mp4` (before left, lowered right). Each capture's `Review/after_normal.mp4` and `after_keyposes.jpg` are available separately. Evaluation here used synchronized frames and telemetry; continuous normal-speed artistic acceptance remains for play review.

Obstacles: no engine-source or authoring-bridge change was needed. A project header rebuild took about 136 seconds. Direct normal-speed viewing was unavailable in this session, so the packaged movies are evidence for user review rather than a claim that they were watched. Existing saved RC_v008 scenes and exports remain the source candidate for the horizontal pilot.
