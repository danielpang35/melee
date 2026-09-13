> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../../../../../DEVELOPMENT.md) for active work.

# Camera & Input


Mouse aim should have minimal perceptible latency, no default aim acceleration, and no excessive smoothing. No target lock, melee aim assist, magnetic view rotation, or magnetic attack redirection. [S1]

Turncaps define the permitted angular envelope by state and phase. Discard excess mouse delta rather than queueing a later snap. Keep view intent, combat orientation, body orientation, guard orientation, and weapon orientation conceptually separate. Guard geometry follows actual capped guard orientation. [S1]

Directional selection uses recent mouse intent, a configurable deadzone, and deterministic fallback. Six strike origins plus a dedicated stab are the lab scope; the internal angle representation should support later continuous selection. Do not delay the click while waiting for a gesture. [S1]

Baseline controls: WASD move; mouse look; Shift sprint; Ctrl crouch; Space jump; LMB directional strike; wheel-up stab; RMB parry; Q feint. Contextual attack input produces legal morphs, combos, and ripostes. Bindings remain configurable. [S1]

Camera motion supports bodily sensation with restrained directional impulses and locomotion cues. It must not obscure attack lines, substitute for weak weapon motion, or delay actual aim. Current FOV is a tunable implementation value. [S1, S5]



[Source register](../Sources.md)
