# Mordhau swing investigation — 9 September 2026

Live console testing recovered Greatsword timing, turn-cap settings, a referenced release curve and its numeric data. Five recordings cover repeated neutral swings, acceleration visualization, tracers, directional attacks, a feint, and opposite steering. This establishes a useful partial model; it does not recover the entire hidden combat implementation.

## Reproducible evidence

Steam build 16143657; executable identity in [installed-build.json](../Saved/MordhauConsoleStudy20260909/installed-build.json). Local `LiteMordhauTestLevel`, Knight/Greatsword, no deliberate footwork. Live FOV 101; mouse smoothing 0; combat headbob 1. World time dilation read back as 1. All recordings used normal game speed. Capture is 1920×1080, approximately 30 actual frames/s despite a requested 60; use decoded PTS. Review was sampled frame sequences, not uninterrupted video playback. Input sidecars contain wall-clock brackets, not exact engine input timestamps.

| Recording in Saved/MordhauConsoleStudy20260909 | Conditions / coverage |
|---|---|
| `fp-neutral-pawndebug-three.mp4` | Three right horizontals; pawn debug only |
| `fp-acceleration-three.mp4` | Three right horizontals; acceleration + pawn debug |
| `fp-tracers-three.mp4` | Three right horizontals; tracers + pawn debug |
| `fp-vocabulary-tracers.mp4` | Right horizontal, left horizontal, right upper strike, right-strike/feint input |
| `tp-neutral-leftturn-rightturn.mp4` | Three right horizontals: neutral, leftward mouse steps, rightward mouse steps; acceleration + tracers + pawn debug |

The map timed out during a property query and redirected `greatsword_c` into all chat. Input stopped, the local test map was reopened, and subsequent console text was visually checked before submission. The final two recordings are after this reload; their spawn/framing differs from the first three. Do not pool their screen-space measurements. The steering trials also start at different headings and are exploratory, not a matched target-contact experiment.

## Values actually returned by the console

Read-only commands: `ListProps BP_Greatsword_C *`, `ListProps BP_Greatsword_RightStrikeMotion_C *`, then `GetAll <class> <property>`. Full relevant values are in [live-values.txt](../Saved/MordhauConsoleStudy20260909/live-values.txt).

| Greatsword AttackInfo field | StrikeAttack | StabAttack |
|---|---:|---:|
| Windup | 0.575 | 0.675 |
| Release | 0.500 | 0.325 |
| MissRecovery | 0.700 | 0.700 |
| ComboWindupIncrease | 0.200 | 0.250 |
| MissComboExtraWindupIncrease | 0.200 | 0.200 |
| TurnCaps X / Y | 245 / 171.5 | 270 / 189 |
| TurnCapCurve | None | None |
| bStopOnHit | False | False |

Timing fields are interpreted as seconds; these are configured values, not measurements of every runtime phase. Turn-cap units, axis mapping and modifier composition remain uncalibrated. `None` in this struct does not prove the complete turn response is constant. Combo fields alone do not establish the final combo duration.

The performed right-strike motion returned `EarlyRelease=0.225`, `EarlyReleaseTimeFactor=1.4`, `WindUpCurve=None`, and `ReleaseCurve=FC_2HSwordStab`. The asset name does not make this a stab: the live object was `BP_Greatsword_RightStrikeMotion_C`.

`GetAll CurveFloat FloatCurve` exposes curve data. The referenced release curve has cubic keys at (0,0) and (1,1), with outgoing tangent 0.689186 at the first key and incoming tangent 1.336182 at the second. Under ordinary unweighted cubic Hermite interpolation, this segment is:

`f(u) = 0.025368 u³ + 0.285446 u² + 0.689186 u`, for `0 ≤ u ≤ 1`.

This mathematical reconstruction has increasing slope, from about 0.689 to 1.336. It describes the **curve segment**, not blade velocity or force. The console does not expose the call site, input normalization, early-release composition or final pose evaluation; applying this polynomial directly to a weapon would be unjustified. Raw data: [exposed-float-curves.txt](../Saved/MordhauConsoleStudy20260909/exposed-float-curves.txt).

## Visible behavior and useful distinctions

- Fixed-aim right horizontals gather the hands to the right, deliver across the view, carry past the front and return to ready. Tracers appear during delivery and persist into the return; persistence is not evidence of continuing damage.
- Three neutral acceleration readouts reported maximum total reach 190.828979–190.832443. The very small spread supports repeatability in that setup. Units and measurement origin are unresolved.
- The acceleration ribbon and its “badness” value are not calibrated quality scores. Neutral repeats already report roughly 0.98–0.99. Colors/arrows cannot yet be translated into a physical acceleration curve.
- Pawn debug identifies the motion and reports movement velocity/acceleration. Its `Accel=0` during a stationary swing concerns pawn movement, not a stationary blade.
- Directional trials visibly change the trace plane. The feint input produces a brief load and return without a new complete trace fan in the sampled evidence.
- Zero-delta `sky.scroll` at an offset coordinate moves aim without clicking or wheeling. Four ±100-pixel steps during each steering trial visibly change heading/trace placement. Actual input timing is retained. This establishes a workable control method, not a measured turn cap or confirmed earlier/later hit.

## Command coverage and remaining uncertainty

Behavior tested: `m.VisualizeAttackAcceleration`, `m.DrawTracers`, `m.ShowPawnDebug`, camera cycle P, `ListProps`, `GetAll`, and zero-wheel aim movement. Tracer persistence was read as 2 and held fixed.

Help/current values inspected: `m.DrawTracersStayTime`, `m.VisualizeBlockCollider`, `m.FOV`, `m.CameraDistance`, `m.CombatHeadbob`, `m.Headbob`, `m.CinematicCamera`, `m.MouseSmoothing`, `m.SlowLookSmoothingMultiplier`, `m.DebugNetworkParry`. These are not completed behavioral tests. `DumpConsoleCommands` and `obj dump` were unrecognized. `DisplayAll AttackMotion Stage` produced no useful visible phase readout in the sampled trial; it was cleared afterward.

Still unresolved: damage-window boundaries, exact early-release mapping, target-contact timing under steering, turn-cap enforcement, riposte/combination/morph behavior, parry geometry, FP/TP synchronization and the ribbon legend. Slow motion, network diagnostics and camera-setting comparisons were deferred; no claim of exhaustive command coverage is made.

## What to use in MeleeCombatLab

Treat phase scheduling, source motion spacing, steering, collision sampling and camera response as separate contributors. The evidence supports exploring a quieter load followed by progressively stronger delivery and continued carry; it does not establish mass simulation or justify one universal easing curve.

Next authoring experiment: three complete isolated candidates varying delivery buildup/carry while preserving the accepted attack clock and contact contract. Compare at source speed; reject a candidate if stronger launch sacrifices continuous grip or readable threat. No animation assets, gameplay code or accepted baseline were changed by this investigation.

The next measurement with highest value is a fixed defender plane with repeated neutral/into/against swings, frame-resolved motion phase and first confirmed contact. That can distinguish changing contact time from changing the underlying attack duration. Use the [console method](MORDHAU_CONSOLE_EXPERIMENTS.md) for continuation.

Restored: acceleration visualization 0, tracers 0, pawn debug 0, cleared DisplayAll, first-person camera. World time dilation verified 1. The game remains in the local experimental map; spawn and heading changed during testing. Original recordings and unique evidence remain on disk.
