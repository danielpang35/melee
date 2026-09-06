# MeleeCombatLab



A single-player first-person melee laboratory for studying spacing, spatial swing manipulation, timed defense and attack commitment. C++ combat simulation owns the sword; rendering follows its blade endpoints. No animation notifies, root-motion damage, aim assistance, lock-on or multiplayer.



## Build and launch



Requires **Unreal Engine 5.8**, Visual Studio 2022 C++ x64 tools, a Windows SDK, and the **.NET Framework 4.8 SDK/targeting pack**. Engine installation must finish before building.



From PowerShell in this project:



```powershell

.\Tools\Build.ps1 -Launch

```



The script discovers `C:\Program Files\Epic Games\UE_5.8` or `C:\Epic Games\UE_5.8`. For another location, pass `-EngineRoot 'X:\path\UE_5.8'`. Unreal needs normal access to its engine installation and user caches.



Alternatively open `MeleeCombatLab.uproject`, allow the module build, and press Play. The configured engine Entry map runs `ACombatLabGameMode`, which constructs the arena, lighting and targets at runtime. No external art or generated binary content is required.



## Controls



| Input | Action |

|---|---|

| WASD / mouse | Move / look |

| Shift / Ctrl / Space | Sprint / crouch / jump |

| LMB | Strike selected from recent mouse intent |

| Wheel up or E | Stab |

| RMB | Timed parry |

| Q | Feint during legal windup; immediately permits parry |

| 1 / 2 / 3 | Right horizontal / upper right / upper left |

| 4 / 5 / 6 | Left horizontal / lower left / lower right |

| F2 | Cycle deterministic training patterns |

| F3 | Actual weapon, sweep, hurt, parry and chamber geometry plus diagnostics |

| F4 | Open tuning; use CLOSE to return to mouse capture |

| F5 | Toggle external inspection camera for guard/foot coverage |

| F6 | Toggle infinite stamina |

| R | Reset health, positions and attacks |



Strike and stab inputs during early opposite-type windup morph. Inputs during the latter release window queue combos. An attack immediately following a successful parry becomes a faster riposte.



Directions name the **origin** of the strike. Right horizontal travels right-to-left. The input resolver keeps the raw continuous angle and quantizes to six 60-degree sectors. With insufficient recent mouse movement it retains the last sector.



## Mechanics and tuning



The attack lifecycle is idle → windup → release → recovery. Strike defaults are 525 / 560 / 675 ms; stab defaults are 565 / 350 / 675 ms. Only 7–93% of release damages bodies. All points along the blade have identical gameplay rules.



Turning changes the world-space weapon path. Accels and drags never change attack playback rate. Release yaw limits decrease from 260 to 190 to 135 degrees/sec. Cumulative release rotation beyond 135 degrees disables body damage. Excess mouse input is discarded.



Parry lasts 365 ms with 550 ms punish recovery on a miss. Its oriented frontal box and extended cone follow a separately limited guard. Looking up lowers and tilts the box to protect the feet; looking down raises its lower edge. The cone applies a tunable pitch influence of 0.35 so it does not accidentally erase that foot exposure. Chambers require body contact, the incoming origin projected into the defender's view, within 32 degrees, and a 225 ms window at the start of an ordinary attack. Stabs chamber stabs. Chambers have no extended region. A legal drag can outlast a chamber while a normal parry catches it farther forward.



Momentum compares actual locomotion intent and velocity, never camera yaw alone. Lunge adds a short forward velocity contribution through collision-safe CharacterMovement. It requires forward commitment and is capped at 85 cm of commanded extra displacement.



F4 exposes the shared tuning registry. Durations use seconds, distances centimeters, and angular rates degrees/sec. SAVE/LOAD use `Saved/Config/CombatTuning.json`. RESET restores built-in defaults. PROMOTE TO PROJECT DEFAULTS writes `Config/CombatDefaults.json`; commit this file to share tuned defaults. Invalid JSON is rejected and numeric values are clamped to supported ranges. Attack definitions snapshot timing at attack start; changes affect subsequent attacks.



Start human tuning with `ReleaseMidCap`, `StrikeRelease`, `ParryDuration`, `ChamberDuration`, and `LungeStrength`.



## Architecture



| Location | Responsibility |

|---|---|

| `Combat/Attacks` | Intent, sector selection, attack definitions, explicit state machine, procedural trajectory |

| `Combat/Defense` | Transformed box/cone geometry and continuous chamber-angle comparison |

| `Combat/Collision` | Equal-rule blade samples and continuous sweeps |

| `Combat/CombatSimulation.*` | 240 Hz shared simulation, all-combatant advancement, deterministic defense-first contact resolution |

| `Combat/CombatTuning.h` | Single timing, defense, weapon, movement and presentation tuning registry |

| `Combat/CombatComponent.*` | Unreal ownership and combat input boundary |

| `Movement` / `Character` | Momentum, lunge, custom CharacterMovement and Enhanced Input |

| `Camera` | Sword and two-link procedural arm presentation |

| `Training` | Runtime arena, targets, repeatable patterns and synthesized impact audio |

| `Debug` | Canvas HUD, actual geometry and Slate tuning |

| `Tests` | Unreal Automation Tests and an opt-in in-engine regression tour |



`Combat`, `Movement` and `TrainingPattern.h` contain engine-independent simulation logic. The same code is compiled into the native tests and Unreal module. The simulator retains fixed-step catch-up debt, caps work at 64 steps per frame and reports overload rather than silently dropping time. Blade sweeps subdivide further for large translation or rotation, up to 64 subdivisions, using spherical interpolation rather than cutting across the curved path. World collision delegates to Unreal sphere sweeps; hurt capsules and defenses use the shared mathematical geometry. Contacts are gathered before chamber → parry → world → body resolution.



To move toward continuous/240 input, replace the resolver's quantization with the raw angle. Trajectory, chamber matching, contact detection and attack intent already use continuous angles. Future networking should serialize timestamped intents and authoritative events, then add server-side scheduling/reconciliation; no replication or prediction is implemented here.



## Verification



```powershell

.\Tools\TestCore.ps1 -Sanitize

.\Tools\Build.ps1 -Automation

```



The native suite compiles with MSVC `/W4 /WX`, and optionally AddressSanitizer. Its 461 checks cover state transitions, all 36 strike chamber pairings, continuous tolerance edges, complete pitch-dependent parry coverage, swept cone contact, curved blade sweeps, registration-order independence, exhausted defenses, once-per-target damage, spatial accel/drag contact, multiple frame rates, momentum and lunge.



To run the scripted **in-engine** tour after building:



```powershell

& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' `

  "$PWD\MeleeCombatLab.uproject" /Engine/Maps/Entry -game -windowed `

  -ResX=1600 -ResY=900 -CombatPlaytest -CombatPlaytestQuit

```



This uses actual actors, movement, world queries, rendering and feedback. It writes images and `results.json` to `Saved/Playtests`. It is a scripted regression tour, **not a replacement for human combat-feel testing**. See `VALIDATION.md` for recorded results and unfinished checks.



## Current scope and limitations



- Original primitive art and procedural arms; no skeletal mannequin, authored animation or advanced IK rig.

- Synthesized placeholder audio. No proprietary assets or external packs.

- Simple health/stamina and flinch. No armor, dismemberment, weapon zones, optional clashes or NavMesh dueling AI.

- Single local player. No networking, rollback, prediction or replication.

- Very long hitches can create catch-up debt; the HUD marks overload. This is a development lab, not a shipping performance claim.

- Human testing is required to judge responsiveness, swing readability, arm appearance and balance. Automated contact-time tests establish mechanics, not subjective feel.



Combos always alternate left/right body side, preserving the requested strike height. Stab combos use visibly different left/right hilt origins. Chamber the side you see the attack coming from: an opponent's right horizontal requires your left horizontal (key 4). The HUD shows the matching key during incoming attacks. The 225 ms early-attack chamber window remains short; start just before impact. Successful defenses show gold parry or cyan chamber sparks and a central success indicator.



Combo attacks cannot chamber, including when a combo is morphed to the other attack type. A fresh attack from idle can chamber normally.


Hits reset ordinary attacks directly to idle, including release and queued combos. The visual weapon eases back to rest over 120 ms and an interrupted lunge stops. Active riposte windup/release resists flinch but still takes damage; lethal damage still kills. Riposte recovery, follow-up combos, and morphs are vulnerable normally.

Ripostes use a raised counter-cut and lifted elbow pose, with a RIPOSTE HUD indicator. Their yaw/pitch caps and cumulative rotation allowance are multiplied by the tunable RiposteTurnScale (default 1.25). The raised blade path is shared by rendering and collision.

The passive DAMAGE TARGET has infinite health and reports hit count and accumulated damage. R resets its counters. The attacking dummy retains normal health.

Movement responsiveness defaults: forward 450, lateral 380, backward 300, sprint 640 cm/s; acceleration 4200 and braking deceleration 5000 cm/s²; ground friction 10. Sprint momentum builds at 1.0/s. Gravity scale 1.4 and jump impulse 500 cm/s give approximately 0.73 s airborne on level ground, before capsule/landing details. All are exposed in F4 tuning. Previous saved movement settings are backed up in Saved/Config/CombatTuning.before-movement.json.
