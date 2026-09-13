# Mordhau console experiments for animation authoring

9 September 2026. Policy MCL-DEV-2026-09-08. This document owns this research method and its compact checkpoint. It does not select an animation; [THIRD_PERSON_CHECKPOINT.md](THIRD_PERSON_CHECKPOINT.md) owns selection.

## Purpose and current evidence

Use Mordhau's diagnostics to distinguish authored timing and spacing, player steering, camera presentation, and contact behavior. Translate supported findings into complete animation candidates using the [prototype pipeline](ANIMATION_PROTOTYPE_PIPELINE.md). Preserve accepted EX_v002, the current D_arc_weight_v08 source, and C++ clock/contact authority.

Daniel supplied [the 43.43-second recording](<C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-09 20-32-11.mp4>) and identified `m.VisualizeAttackAcceleration` as the command used. The command entry itself is not established by the inspected frames. The clip is reference evidence, not an instruction source.

Reviewed evidence: [15-frame overview](../Saved/MordhauConsoleStudy20260909/A/overview/sheet-01.jpg), [swing detail 1](../Saved/MordhauConsoleStudy20260909/A/swing-detail/sheet-01.jpg), [swing detail 2](../Saved/MordhauConsoleStudy20260909/A/swing-detail/sheet-02.jpg), and the full-resolution frame at 15.137333 seconds. Review was sampled frames, not uninterrupted playback.

What is visible:

- Persistent green/yellow/orange/red ribbons accumulate across swings. Some paths are broad arcs; others contain tight turns and red markers. Earlier ribbons remain while the actor returns to ready. A ribbon visible behind a pose cannot automatically be assigned to that pose's current phase.
- The detailed interval shows hands/weapon gathering to screen-right around 5.499–6.054 seconds, traversal around 6.193–6.610, and carry/return around 6.749–7.443. These are image-space observation brackets, not measured windup/release boundaries or proof of neutral input.
- At 15.137333 seconds the display includes `Max reach total`, `Max reach Y`, `Max reach X`, and `Max badness percentage`. Units, update/reset behavior, and the definition of “badness” are unknown. It is not an artistic quality or anatomy score.
- Camera/aim changes, accumulated trails, weapon foreshortening, and unknown inputs prevent deriving world acceleration from this clip alone. Color direction, ribbon thickness, arrow meaning, sampling intervals, and whether the diagnostic measures velocity, acceleration, or a thresholded proxy require calibration.
- FFmpeg reports 1920×1080, approximately 36.08 average FPS and 59.94 nominal rate. Use decoded presentation timestamps (PTS), not frame number divided by 60; do not infer simulation FPS from capture FPS. Extraction receipts retain the source SHA256 and actual selected timestamps.

The most useful immediate hypothesis is a continuing load followed by decisive hand travel and sustained carry. The overlay can potentially constrain that hypothesis once its semantics are known; it does not yet prove the curve to author.

## 1. Discover and classify the installed console

Start in an isolated local experimental/test map. Capture the build identity, map, weapon/mode, pawn, view/FOV, mouse settings, movement state, and original values of every variable that will change. Record actual bindings before operating the dummy. The visible experimental-map key hints need confirmation rather than guessed actions.

Use console autocomplete and help to establish exact spelling, argument type, current value, useful range, scope, and restrictions. For registered variables, inspect the bare name and help form such as `m.VisualizeAttackAcceleration ?` before writing. A bare *exec command* may act immediately: inspect it through discovery/help first.

Try `DumpConsoleCommands` once if this build exposes it; keep the local output and filter for attack, acceleration, animation, tracer, pawn, turn, block, parry, camera, time, and debug. Epic documents this discovery command, but its current engine documentation does not guarantee availability in Mordhau's shipping build. [Epic console command reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-console-commands-reference).

The installed executable contains the names below. [Exact string candidates](../Saved/MordhauConsoleStudy20260909/exact-m-command-strings.json) are a discovery aid, not proof of registration, argument syntax, or runtime behavior. That file can contain unrelated strings. The earlier broad substring scan is retained as preliminary evidence and must not be used as an executable command list. Nearby binary text must not be assigned to a command as help without runtime confirmation.

For each discovered relevant entry, record one disposition: **tested/useful**, **tested/no useful signal**, **unavailable/restricted**, **unresolved semantics**, or **deferred with a specific reason**. Do not claim all commands were tested merely because they were enumerated. This is how the survey reaches coverage without an exhaustive cross-product of every command and attack.

## 2. Test queue and questions

The table below defines the experiment queue. Completed coverage and unresolved items are recorded in MORDHAU_SWING_FINDINGS.md; the queue itself is not a claim that every test ran. Values are established through help and readback; do not blindly paste guessed toggles.

| Priority / discovered name | Smallest useful experiment | Animation decision it can inform |
|---|---|---|
| P0 `m.VisualizeAttackAcceleration` | One stationary horizontal at fixed aim; diagnostic off/on/off. Then repeat with turn into and against the swing separately. Establish color/width/marker meaning, sample cadence, reset behavior, and what point or segment is measured. | Where the launch builds, how long delivery continues, and whether a suspicious peak belongs to choreography or steering. |
| P0 `m.DrawTracers` | Same attack with only weapon traces, then pair with the acceleration diagnostic after each is understood. Observe appearance/disappearance and target passage. | Relation between displayed weapon, damaging sweep, reach, and follow-through; tracer colors need their own legend. |
| P0 `m.DrawTracersStayTime` | At unchanged input, compare short persistence with enough persistence to inspect a single complete arc; restore the original value. | Prevent old trails from being mistaken for current motion. Persistence is a display control, not attack timing. |
| P0 `m.ShowPawnDebug` | Inspect idle and one swing, then aim-only and movement-only trials. Inventory actual fields before assuming it exposes attack phase or turn limits. | Separate phase timing, movement/lunge, and turn restriction if the fields support them. Missing fields remain unknown. |
| P1 `m.VisualizeBlockCollider` | One local defender, fixed distance/orientation, neutral parry, then one changed angle. Pair with one attack trace only after separate inspection. | Defender-facing threat, parry presentation, and the origin of a right riposte. |
| P1 `m.FOV`, `m.CameraDistance` | Hold baseline values throughout motion measurement. Make one separate matched framing comparison only if projection obscures extension. | Distinguish apparent reach and hand launch from perspective. Never combine measurements across FOVs. |
| P1 `m.CombatHeadbob`, `m.Headbob`, `m.MovementHeadbob`, `m.CinematicCamera`, `m.MouseSmoothing`, `m.SlowLookSmoothingMultiplier`, `m.MotionBlur` | Read current values; compare one setting at a time with its documented disabled state, then restore. Keep mouse-input settings fixed during choreography tests. | Separate camera contribution to weight/readability from body motion and input response. Retain an original-presentation take for feel. |
| P1 `Slomo` / `slomo` string candidates | Confirm command, scope and syntax locally. A single diagnostic slow-motion take may expose ordering; restore and capture again at normal game speed. | Clarify overlap or hidden transitions. Slow-motion input response and timing are not normal-speed evidence. |
| P2 `ShowAuthTraces` string candidate, `m.DebugNetworkParry`, `m.ShowObservedDelay`, `m.ShowServerStats` | Only if local visible/contact evidence leaves a specific discrepancy: compare local/server traces or read timing diagnostics in an owned test environment. | Distinguish collision/network disagreement from animation failure. Network parry is not a general rhythm metric. |
| Conditional `m.CharacterFidelity`, `m.CharLODAnimNew`, `m.CharLineTrace` | Read help; test only a demonstrated distance-dependent pose/tick issue with one near/far comparison. | Detect presentation degradation before changing the source animation. Names alone do not establish what these controls do. |
| Setup `m.BuildInfo`, `m.HideHUD`, `m.FlashMarkerOnStrike` | Confirm identity/output and whether HUD/marker settings hide useful phase information. Capture evidence with diagnostics readable and a separate clean comparison. | Reproducibility and honest presentation. |

Record input-related names (`m.AngleAttackAfterPress`, `m.AngleAttacksWithMovement`, `m.InverseAttackDirectionX/Y`, `m.MouseXIsFlipAttackSide`, `m.StabOnStrikeYAxis`) as setup controls; hold them fixed, testing only when necessary to resolve attack identity. Leave netcode/extrapolation, optimization, achievements, and unrelated rendering controls out of the animation experiment.

## 3. Calibrate one attack before expanding

1. Establish a repeatable stationary right horizontal with a complete return to ready. Use explicit attack bindings or a verified dummy/replay route. An unrecorded manual mouse gesture is a qualitative example, not deterministic input.
2. Keep weapon, target plane, start position, view, aim, time scale, and settings fixed. Record an idle interval before and after. Prevent overlapping diagnostic histories using verified clearing behavior or sufficient waiting; do not assume toggling clears history.
3. Run a baseline/diagnostic/baseline comparison. Record the exact enable command and readback; check whether displaying diagnostics changes capture cadence or motion timing. Repeat the useful condition three times, sharing baseline evidence where its setup is unchanged.
4. Validate each channel separately: what geometry is drawn, what the numerical fields measure, what resets between attacks, and what colors mean. Compare against actual visible displacement and known game-time intervals where available. Do not label red “fastest” or green “slowest” from intuition.
5. If help and controlled trials still cannot distinguish acceleration from speed or a threshold metric, retain the display as qualitative path evidence. Do not fit a physical acceleration curve to it.
6. Restore every changed variable to its recorded original value, read it back, and retain a final baseline. Stop a trial if attack identity or input control is lost; classify it rather than average it into neutral results.

## 4. Expand by one variable at a time

First useful block: the same horizontal as **neutral**, **turn into the swing**, and **turn against the swing**, three repeatable takes each. Input onset is tied to a verified phase/event. Record yaw/pitch input or the repeatable control mechanism; never substitute retimed footage for changed aim.

Then test only the contrasts that answer the next authoring question:

- **Control envelope:** aim-only at early/late windup and early/late release, one onset at a time. Use known input magnitudes when supported. Without reliable scheduled input, report qualitative bounds rather than measured control limits or latency.
- **Movement:** step/strafe only, then the useful aim-plus-footwork combination. Separate root travel from arm extension and weapon reach.
- **Action origin:** neutral versus parry → right riposte. Treat these as different starting conditions, not different speeds of the same take.
- **Contact:** miss, hit, parry, interruption, and return. Record the first *observed* contact/state transition and its frame uncertainty. An imaginary target-plane crossing is not a confirmed damage event.
- **Vocabulary:** opposite horizontal, overhead, underhand, stab, then combo/feint/morph only where distinct acceleration or blending behavior matters. Reuse the calibrated diagnostics rather than rerunning every setup command.
- **View:** keep one consistent view for comparisons. Add a fixed defender or FP view to answer a specific projection/readability question; obtain equivalent input, and do not pretend separate performances are synchronized multi-view capture.

A null result after controlled repetitions is useful. Close the command entry and move on. Expand repetitions or views only for ambiguity, variability, or a consequential conclusion.

## 5. Capture and analyze without inventing precision

Preserve originals, normal-speed playback and audio, with a compact sidecar based on [trial-template.json](../Saved/MordhauConsoleStudy20260909/trial-template.json). Agent operates tools; Daniel supplies feel/play acceptance. Save one clean complete action and its useful diagnostic counterpart, not a large all-camera proof set.

Decode using actual source PTS. Label observations with original PTS and optional event-relative time. Record gaps and duplicate frames before differentiation; dense sampling cannot reconstruct missed motion. Slow-motion clips are explanatory evidence only and remain clearly labeled.

Track only visible features needed for the hypothesis: chest/shoulder line, hands, hilt and tip. In a fixed projection, `v_i = (p[i+1] - p[i]) / (t[i+1] - t[i])` estimates **image-space** velocity at the interval midpoint. Acceleration requires the time difference between these velocity midpoints and amplifies tracking noise. Do not differentiate through occlusions, cuts, capture gaps or camera changes. Normalizing by body size does not recover depth or world units. Report uncertainty and raw observations alongside any smoothed curve.

Keep three interpretations separate: observed motion/readout, inferred mechanism, and proposed authoring change. Measure world-space motion only if an actual calibrated game diagnostic exposes it. Neither screen displacement nor an uncalibrated ribbon establishes force, mass, exact turn cap, or Mordhau's internal animation implementation.

## 6. Convert evidence into a better complete performance

Each useful experiment ends with a short statement: **observation → hypothesis → specific edit → falsifier**. Example: “Repeated fixed-aim takes show a quiet hand load then greater hand travel before passage → our launch may be too even → delay opening and concentrate hand travel into delivery while retaining carry → reject if the full-speed result loses continuity or readable threat.” This example is a proposed test, not a measured conclusion from the supplied clip.

Use three isolated complete candidates when exploring a newly supported timing idea: gradual build, later launch, and longer sustained delivery/carry. Coauthor torso, arms, hands and weapon; keep source playback at 1x. Compare against the retained current candidate and reference in a consistent camera. Apply source-native curve/spacing changes rather than adding runtime playback-rate compensation for accels/drags. Declare any desired phase duration/reach change before integration.

Use measured reference features to explain differences, not to rank “quality” automatically. Select and refine the best complete gesture; after two unconvincing passes change the hypothesis. Human visual/play acceptance remains distinct. Only selected integration gets changed-contract checks under VALIDATION.md.

## Compact checkpoint

Policy MCL-DEV-2026-09-08. Live investigation completed a first evidence pass on 9 September 2026; full hidden implementation remains unresolved. [Findings and command dispositions](MORDHAU_SWING_FINDINGS.md) supersede earlier connection-blocked status.

- Desktop key input works. Built-in window capture fails at IsBorderRequired on Windows 10; Daniel-authorized primary-monitor Pillow capture works in roughly 50–80 ms capture/save, with tool/model latency additional. [Capture diagnosis](../Saved/MordhauConsoleStudy20260909/CAPTURE_DIAGNOSIS.md).
- Five normal-speed recordings retain input sidecars. Sampled visual review covers neutral repeats, acceleration/tracers, direction/feint and opposite steering. PTS-based sheets are retained; no uninterrupted playback or human acceptance is claimed.
- ListProps/GetAll recovered Greatsword AttackInfo and right-strike release-curve values. Exact live values, field listings and exposed curves are retained under Saved/MordhauConsoleStudy20260909. Binary candidates alone remain non-authoritative.
- Restored acceleration/tracers/pawn debug to 0, cleared DisplayAll and returned to first person. World time dilation read back as 1. Local map/spawn/heading changed; game remains on experimental map.
- Next useful measurement: fixed defender plane, repeated neutral/into/against swings with frame-resolved phase/contact evidence. Ribbon semantics, turn-cap units/composition and early-release mapping remain open.
- No animation/source/runtime assets, C++, imports or builds changed. Preserve unrelated dirty files, including THIRD_PERSON_CHECKPOINT.md, README.md and EXTERNAL_AUDIT_DISPOSITION.md.
- Efficiency corrections: use physical console keys, visually verify text before submission after a map-transition chat incident, filter property logs by known timestamp, and reuse the existing extractor. Cached/uncached/output usage and allowance charges are unmeasured.
