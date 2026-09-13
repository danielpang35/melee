> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../../../../../DEVELOPMENT.md) for active work.

# Melee Swing Model


**Intent:** make aim, timing, and translation control a coherent moving weapon, with enough active travel for meaningful acceleration and delay of contact. [S1]

Lifecycle: **Neutral → Windup → Release → Recovery → Neutral**, with explicit legal branches for feint, morph, combo, flinch, parry, and riposte. The simulation decides legal inputs and damage windows; presentation reads them. [S1]

Six origins are upper-left/right, horizontal-left/right, and lower-left/right. Names describe where the attack begins. A right horizontal begins on the player's right and travels left. Stab is a separate family. Raw angle storage and angular matching remain compatible with eventual continuous selection. [S1]

Weapon state is a function of attack definition, phase progress, combat/view orientation, and character translation. Sweeps must cover movement between simulation steps and avoid duplicate hits on one target during one attack. Anti-spin/glancing constraints preserve a learnable manipulation envelope. Accels/drags change world-space contact time without changing elapsed phase time. [S1]

Current kinetic implementation includes a 160-degree blade arc, 132-degree grip-center arc, tunable regular-strike acceleration, linear riposte progression, Hermite boundary tangents, result-dependent carry/rebound, and movement telemetry. These are existing systems to evaluate, not features to propose as if absent. Their combined visual quality is unapproved. [D3, D4]

Combos buffer within a legal release interval and transfer to the opposite side without snapping through neutral. Combo attacks cannot initiate chamber protection. The user's cadence rule is explicit: combo windup must be slower than normal strike/stab windup. [S1, S2]

Feints cancel a legal windup and allow defensive response without waiting for the cosmetic return. Morphs transition strike↔stab during an eligible windup portion and alter commitment timing visibly. Exact eligibility and balance values remain tunable. [S1]

Open work: anatomical path design, reach-correction magnitude, family-specific posing, normal-speed defender readability, and outcome-complete feedback. Do not enlarge arcs or shorten timings simply to conceal weak hands and body motion. [S5, S6]



[Source register](../Sources.md)
