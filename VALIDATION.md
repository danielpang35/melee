# Combat feel validation



## Current changes



- Strike release: 560 ms, with a 5–95% damage window (504 ms active).

- Stab release: 350 ms, with 315 ms active.

- Release yaw caps: 320 / 270 / 230 degrees per second; pitch cap 220; cumulative anti-spin threshold 175 degrees.

- Combos alternate body side, including stab hilt origin. Combo attacks cannot chamber; morphing a combo does not restore chamber eligibility. Fresh attacks from idle remain eligible.

- Chamber origins are transformed into the defender view; timing remains 225 ms and tolerance 32 degrees.

- Gold parry / cyan chamber spark trails and a 650 ms success indicator.

- Saved tuning updated, with the previous values backed up to Saved/Config/CombatTuning.before-feel.json.



## Native validation



MSVC C++20 /W4 /WX with AddressSanitizer: 434 checks passed, with no reported sanitizer errors.

Contact times at 240 Hz: accel 0.720833 s, neutral 0.766667 s, drag 0.829167 s.

Neutral, accel and drag contact equivalence passed at 30, 60, 120, 144 and 240 FPS.

Includes 72 combo side/kind combinations, mirrored chamber sectors, continuous angular boundaries, expired chamber and parry windows, microdrags, stamina fallback, defense ordering, parry foot coverage, movement and lunge.



## Unreal validation

- UE 5.8.2 Editor Development build and link succeeded, including the combo-chamber restriction and final spark visibility adjustment.
- Unreal automation: 2 succeeded, 0 warnings, 0 failures (Saved/Automation/index.json).
- Rendered regression: 32/32 scenarios passed on the final build (report 2026-09-05 23:00 local, Saved/Playtests/results.json).
- The chamber scenario uses real Enhanced Input key 4 against the opposing right horizontal. The combo scenario repeats the original direction and verifies the resulting opposite origin.
- Final parry and chamber screenshots visually verified: thin gold/cyan trails and clear central success text.
- Body-contact chamber bursts are moved forward when they would spawn beside the local camera. This is presentation only; collision and chamber timing remain unchanged.

The previously locking lab process was closed with user authorization. No user action is needed to release the DLL.

## Flinch / riposte / infinite target update

Native MSVC /W4 /WX with AddressSanitizer: 461 checks passed. Includes release flinch cancelling to idle, active riposte immunity with damage retained, loss of immunity on combo/morph/recovery, raised authoritative weapon trajectory, looser turncaps, and 20 successive hits on an infinite target (700 damage recorded, health remains 100).

Flinch/riposte/infinite-target Unreal build succeeded, and its 2 automation tests passed. The subsequent build including movement changes was rejected by the user at the tool approval step. Movement changes remain source-only; the 37-scenario rendered regression is pending.

Movement tuning now includes ground friction, gravity scale, and jump speed. Rendered scenarios 35/36 compare old versus new walking acceleration and stopping distance using actual Enhanced Input and CharacterMovement. Results pending.

## Latest build / visual baseline checkpoint

Latest UE build succeeded with movement, benchmark component, isolated test tuning, and bounded riposte elbows. Native suite remains 461/461. Unreal automation passed 2/2. Prior rendered movement comparison measured 0.1625 s to 90% speed and 21.40 cm stopping at old settings, versus 0.0958 s and 10.70 cm at new settings.

The previous 37-scenario tour used user tuning (150 cm blade, 500 ms windup), which caused two low-strike floor collisions and an incorrectly timed riposte fixture. The regression now runs on its explicit default fixture and restores the exact saved user tuning on EndPlay. The corrected rendered tour remains pending; do not report it as passed.

Visual baseline launch was rejected at tool approval. Stage 1 baseline measurements and stages 2-6 are pending. No courtyard/knight visual replacement has been claimed or implemented yet. See Docs/Visual for brief, budgets, route design, style rules, asset audit and backlog.
