> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../../../../../DEVELOPMENT.md) for active work.

# Balance / Tuning


Disk baseline inspected 6 September 2026 from Config/CombatDefaults.json. No Saved/Config/CombatTuning.json override file was present. These values do not establish what an already-running editor has loaded. They are tuning, not universal design laws. [D1]

| Parameter | Current value | Meaning / constraint |
|---|---|---|
| Strike windup / release / recovery | 575 / 500 / 675 ms | 650 ms windup is historical; judge actual contact timing |
| Stab windup / release / recovery | 565 / 350 / 675 ms | Dedicated family |
| Combo windup | 700 ms | Must remain slower than normal strike/stab windup |
| Combo input interval | 50–96% release | Reliable buffering with continuous opposite-side transfer |
| Damage interval | 5–95% release | Visual release is longer than damaging interval |
| Riposte windup / input window | 320 / 300 ms | Distinct transition; turn scale 1.5 |
| Release yaw caps | 255 / 245 / 220 degrees/s | Early / mid / late |
| Pitch cap | 185 degrees/s | Separate from yaw |
| Parry duration / recovery | 365 / 600 ms | Current timing; catch geometry is distinct from chamber |
| Parry box width × height × depth | 80 × 110 × 32 cm | Current dimensions, not a rendered sword-only block |
| Cone length / half-angle | 100 cm / 18 degrees | Forward / vertical offsets 30 / 20 cm |
| Neutral guard chest offset | 18 cm | Tapers with pitch in current implementation |
| Chamber duration / angle tolerance | 225 ms / 32 degrees | No extended parry cone |
| Forward / lateral / backward / sprint | 360 / 315 / 255 / 560 cm/s | Current directional envelope |
| Release drive speed / end | 95 cm/s / 72% release | Forward-input-dependent drive |
| Attack momentum carry | 0.60 | Evaluate with drive before increasing |
| Strike release acceleration | 0.85 | Curve strength; does not change the attack clock |
| Blade length / damage | 110 cm / 35 | Simple lab baseline |
| FOV | 120 | Current configurable camera value |

Tuning sequence for the current milestone: establish acceptable arms; compare motion with fixed clocks; measure neutral/accel/drag contact; assess defense outcomes and footwork; then adjust timings with explicit rationale. Recheck combo cadence when normal timings change. [S2, S6]

Unresolved balance questions include the stationary double-parry rule, final acceleration curve, release drive strength, reversal/stop authority, chamber tolerance, and stamina economics. Preserve intentional competitive tests; revise tests that encode an explicitly changed balance choice only alongside a recorded decision. [S5, S6]



[Source register](../Sources.md)
