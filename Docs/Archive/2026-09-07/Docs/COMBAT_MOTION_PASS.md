> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

> Follow-up: [Arm deformation and motion revision](COMBAT_MOTION_REVISION.md) supersedes this pass's visual conclusions.

# Combat motion pass � 6 September 2026

## Audit and design decision

This is an implemented motion foundation, not an assertion of AAA animation quality or a substitute for hands-on feel approval. Audit sources: AttackTrajectory, AttackStateMachine, CombatSimulation, WeaponPresentationComponent, MeleePresentationPose, KnightPresentation, CombatRigMesh, training/playtest code and asset import scripts.

The existing system was already more than a rotating stick: translating hands, spherical blade interpolation, procedural torso rotation, two-hand IK, fixed 240 Hz simulation, swept collision and calibrated skinned knight/arms assets were present. No authored attack clips, animation curve assets, Control Rig graph or FBIK integration were found in the active presentation path. KnightPresentation builds component-space poses from the reference skeleton every frame; the first-person mesh receives the same pose as the full body. This makes motion coherent but does not supply artist-authored gesture or good skin deformation automatically.

Specific weaknesses:

- The old release map p*(1+f*(1-p)) began at maximum speed after a zero-speed windup and then decelerated throughout. At f > 1 it reached a clamped plateau before release ended. The result was a mechanical velocity step, not early acceleration from tension.
- Cut families mainly rotated the same arc, with only small hilt offsets. Underhand leverage and overhead hand descent needed stronger differentiation.
- The old stab extended and retracted during the damage-active phase. Its body did not extend with the weapon.
- A 700 ms combo load was slower than a fresh 650 ms windup; it captured the prior hilt but still performed another anticipation movement. The body did not capture the previous action pose.
- Feints, chamber resets and successful parries could lose body pose continuity. Successful parry changed state during resolution without resetting the return origin, allowing a stale idle return.
- The visual parry used camera orientation while the guard volume used rate-limited orientation.
- World-space hands inherited full camera pitch; the arm solver stretched to satisfy unreachable targets. The rendered skeleton independently solved different shoulder targets.
- The blade frame transported camera-right even for diagonal cuts; wrist preparation did not sufficiently establish the cutting plane.
- Existing impacts were generic synthesized sound and scalar camera/body kicks. Empty-air swings have no polished velocity-shaped audio, cloth/armor secondary motion or authored weight transfer. Mathematics cannot establish that swinging is deeply pleasurable.

## Architectures considered

Scores are engineering judgments, 1 (weak) to 5 (strong), for this repository and an eventual production implementation. They are not measured quality scores. The authored alternatives assume suitable artist-made assets exist.

| Architecture | Plausibility | Authority | FP quality | Manipulation | Readability | Response | Combos | Animation | Maintainability | AAA ceiling |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fully procedural joint/physics solving | 3 | 4 | 3 | 5 | 3 | 4 | 4 | 3 | 2 | 3 |
| Authored skeletal bases + weapon correction | 5 | 3 | 5 | 3 | 5 | 4 | 5 | 5 | 4 | 5 |
| Control Rig/FBIK around weapon targets | 4 | 5 | 4 | 5 | 4 | 4 | 4 | 4 | 3 | 4 |
| Pose-space families with dynamic hand/elbow IK | 4 | 5 | 4 | 5 | 5 | 5 | 4 | 4 | 4 | 4 |
| Co-authored trajectory/body action + IK adapter | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 5 |

Chosen: the final hybrid. The implementation here uses code-defined action curves and the existing skeletal adapter. It does **not** pretend that numeric curves are equivalent to AAA authored animation. The production extension is offline co-authoring of blade/hilt curves and skeletal poses, then baking those into deterministic evaluators. Control Rig/FBIK can consume the same targets, but engine support alone is not a reason to introduce a second source of weapon truth.

The seven-part framework maps onto a single action: family establishes hilt path and blade plane; windup loads body/wrists from the captured prior action; one release travel coordinate drives leverage and acceleration; shoulder/hand targets feed elbow solving; family recovery unloads the same pose. Pelvis/spine contribution remains distributed by KnightPresentation and its existing foot solver. Camera rotation spatially changes the authoritative world trajectory under existing turn caps. It does not change phase speed.

## Implemented behavior and timing

| Setting / behavior | Before | After |
|---|---|---|
| Fresh strike windup/release/recovery | 650 / 500 / 675 ms | unchanged |
| Stab windup/release/recovery | 565 / 350 / 675 ms | unchanged |
| Combo windup | 700 ms | 700 ms, direct transfer from exit; deliberately slower than normal windup |
| Riposte windup | 320 ms | unchanged, captured guard origin |
| Release front-load | .45, quadratic map | .90, blend of integrated smooth velocity lobes |
| Strike damage interval | 5�95% of release (450 ms) | unchanged |
| Missed parry recovery | 550 ms | 600 ms |
| Chamber opposition return | 100 ms neutral blend | 180 ms compression/disengage; no new input lock |
| Successful parry return | possible stale neutral origin | captured contact pose, 60 ms hold + 160 ms return |

Release uses a blend of smoothstep and Beta(2,4) CDF, normalized over the existing [0,1.25] tuning range. Both end with zero travel speed; no legal setting plateaus before the endpoint. Default travel exceeds 85% in the first two-thirds and its speed peaks between 15% and 40% of release. This is a spatial curve, not playback scaling. Release ends braked; recovery carries the pose through a family-dependent disengagement rather than preserving ballistic angular velocity.

Stabs extend through 78% of release and hold the established line until recovery. Overheads increase shoulder-side height before descending; underhands deepen the scoop and increase the transverse hand path. Diagonal wrists rotate toward their cutting plane. Riposte retains its raised authoritative path and existing turn/immunity rules.

Before collision, the world hilt is projected into intersecting 43 cm hand-reach spheres at both body-driven shoulders, with calibrated grip spacing. Blade direction and length remain exact. This changes reachable strike position at extreme pitch; it intentionally trades camera-relative reach for embodiment. The presentation uses those same shoulders. Shoulder anchors are calibrated to the Citadel reference mesh (Y �27.592 cm, Z 147.470 cm above the sole). The adapter uses 26.1/21.22 cm links and the rendered rig reads exact reference-bone lengths, replacing the old hard-coded 32/28 cm solver. A 4 cm palm-to-wrist offset leaves a small bend margin. The low-level solver retains an explicit stretch fallback for imported/unvalidated poses; rendered tests record actual skeletal stretch rather than assuming adapter validity proves mesh validity.

Measured native contact against the stationary target at 135 cm: accel 783.3 ms, neutral 800.0 ms, drag 820.8 ms. That contact shift made the old missed-parry timing allow stationary double-parry; 600 ms recovery restores a 15 ms punish gap (second threat 950 ms, second guard ready 965 ms). Geometry dimensions and chamber eligibility remain unchanged. Broader balance requires playtesting.

## Debugging and feedback hooks

Use F3 for the existing debug HUD and `mcl.MotionDebug 1` for targets. Green is simulation blade; magenta is the actual sword component's transformed asset endpoints; cyan is shoulder/elbow/hand targets; yellow is tip velocity (scaled). HUD shows phase, direction/family, speed, angular speed, acceleration, chest contribution, authoritative reach correction and measured render endpoint error. These are target overlays, not measurements of the final skinned elbow surface.

Combatant exposes world-space tipVelocity and tipAcceleration (cm/s and cm/s�), bodyMotion and reachCorrection. CombatEvent now captures incomingVelocity and normalized energy at contact for sound, particles, haptics and camera consumers. The rig also exposes MaxArmStretch using actual reference-bone lengths. Energy is speed/1800 clamped to [0,1], not joules. Velocity direction is not a surface normal. Existing event point/result/time remain available. Feedback should consume these read-only signals and never displace the authoritative sword or drive collision from sockets. Existing camera feedback stays cosmetic. No new automatic swing-camera shake is imposed.

Persisted Saved/Config/CombatTuning.json values override defaults: remove/update the relevant saved values or use the tuning panel to evaluate these defaults. Automated playtests temporarily use defaults and restore saved tuning.

## Validation

Validation results and limitations are recorded below after the final build/render pass. Native contracts include every six-direction combo pairing, both kinds, pitch extremes, finite IK, grip calibration, orthonormal blade frame, release monotonicity at the full tuning range, early velocity peak, zero endpoint travel speed, non-retracting active stab, and guard orientation. Standing neutral-release samples additionally assert full blade clearance above the floor. Existing combat tests cover frame-rate contact equivalence, drag/accel, defense priority, chambers, ripostes, feints, morphs and once-per-target damage. The rendered tour now includes 18 empty-air scenarios (six directions plus stab in first/external views and four extreme-pitch views), with four phase captures each. It measures transformed mesh blade error and actual skeletal arm stretch, and rejects unintended floor stops in neutral-pitch empty-air swings. Scripted �80 deg/s turns are injected at the simulation step so render timing does not dilute the fixture; native tests separately retain externally supplied, frame-rate-varied input coverage. Two obsolete rendered fixture expectations were corrected: feint reattack waits for its existing lockout and release hits expect Flinch. Grounded movement has its own suite; stale momentum/lunge checks referencing removed settings were removed from CombatTests while direction-input checks were retained.

## What still prevents AAA quality

1. Artist-authored biomechanical poses, hand/finger grip shapes, shoulder/scapula deformation, joint limits and offline reach validation against the actual skeleton. BuildCitadelArt.py creates hand bones but no finger joints, retaining the source finger silhouettes. Rendered review confirms an open, rigid gauntlet shape around the grip; wrist IK cannot close those fingers. The arm target envelope is a robust prototype constraint, not a full musculoskeletal model.
2. Authored combo and defensive transition families. Current transfers are position-continuous and deliberately brake at release end, rather than preserving unrestricted angular momentum. Chamber still resolves by attack matching/body contact, not actual blade-on-blade intersection. Parry still uses a forgiving box/cone, so guard-facing agreement does not imply every block is on the rendered steel.
3. First-person shoulder/torso mesh coverage and clipping evaluation throughout motion, especially at extreme pitch. The supplied FP mesh remains a separate visibility mesh sharing the body pose; no new torso mesh was authored.
4. Authored locomotion/weight transfer, foot planting on uneven ground, inertia and armor/cloth secondary motion. Existing lower-body movement is procedural and was not replaced.
5. Designed empty-air whooshes, directional contact audio, differentiated impact responses and user-led camera tuning. Hooks now carry useful motion data; production feedback assets are still needed.
6. Human A/B playtests at competitive latency, with different FOVs, target ranges, weapons and skill levels. Automated passes cannot prove pleasure, readability, or AAA feel. No network replication/rollback validation was performed.


## Final verification record

- UE 5.8 Development Editor build succeeded with module suffix 9062. The normal link was blocked by the user's open editor holding the original DLL; the existing session was left open. Binaries/Win64/UnrealEditor.modules now resolves the newly built suffixed module for the next launch. Restart the editor to use it.
- Unreal automation: 3 passed, 0 failed, 0 not run (2026-09-06 12:43:01 UTC).
- Native combat: 561 checks passed; grounded movement: 46 checks passed.
- Native presentation/motion: 1,412,017 checks passed. Maximum adapter stretch 1.0; maximum hilt displacement 1.45152 cm per 240 Hz step across the sampled combo/pitch matrix. Counts include repeated frame assertions, not independent test cases.
- Rendered engine tour: 56/56 scenarios passed (completed 12:45:36 UTC). Includes 18 empty-air scenarios, four snapshots each, first/external views, extreme pitches, actual geometry, input, defense and movement.
- Maximum actual rendered blade endpoint error: 0.000293 cm. Maximum actual skeletal arm scale: 1.003691 (0.3691% stretch). This verifies calibrated component endpoints and link reach, not per-pixel skin agreement.
- Inspected textured first-person release plus external release/extreme-pitch captures. The hand silhouette remains rigid/open; shoulder deformation remains rough. Late tour captures also have washed-out material appearance, so those captures support pose inspection rather than finished material/lighting approval. No claim of comprehensive visual or subjective feel acceptance is made.
- Native frame-rate coverage includes 30, 60, 120, 144 and 240 Hz collision/input checks; presentation covers 30, 60, 144 and 240 Hz. Rendered tour ran at variable desktop frame rate, not separate locked-rate render tours.
- No ZIP was produced; changes are already in this repository. No commits, pushes or asset reimports were made.

Reports: [rendered scenarios](../../../Visual/Captures/Motion/rendered-results.json), [engine automation](../../../Visual/Captures/Motion/automation-results.json). Captures: [first-person release](../../../Visual/Captures/Motion/first-person-release.png), [external release](../../../Visual/Captures/Motion/external-release.png), [extreme pitch](../../../Visual/Captures/Motion/external-extreme-pitch.png). All four phase snapshots for each air scenario remain in Saved/Playtests.

Reproduce from the repository in PowerShell:

```powershell
.\Tools\TestCore.ps1
.\Tools\TestCore.ps1 -PresentationOnly
.\Tools\TestCore.ps1 -MovementOnly
.\Tools\Build.ps1 -MaxParallelActions 3 -Automation
.\Tools\Playtest.ps1
```

If an editor holds the regular DLL, use `-ModuleSuffix 9063` (or another unused positive suffix) on Build.ps1. The running editor keeps its existing code; newly launched instances use the built module. Run only one rendered playtest at a time because its report/tuning fixture uses shared paths. Inspect Saved/Playtests/results.json after process completion; launching the script alone does not establish a pass.


