> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../../../../../DEVELOPMENT.md) for active work.

# Rejected Experiments


Separate direct user rejection from superseded implementation and proposed alternatives. Nothing in this table means a technique is universally forbidden; it records why that version failed or ceased to govern this project.

| ID | Experiment / prior position | Disposition | Reason / replacement | Source |
|---|---|---|---|---|
| R-001 | 420 ms combo windup | User rejected cadence | Too fast; subsequent user instruction requires slower-than-normal windup | S2; S5 earlier delivery |
| R-002 | 600 ms combo adjustment | Superseded by explicit correction | Still below then-normal 650 ms; current combo is 700 ms | S2; D1 |
| R-003 | Severe clipping/contortion preview | User rejected | Numeric pose checks failed to reveal unacceptable surfaces; combined repair pending | S5; D4 |
| R-004 | Fixed bone length as proof of acceptable arms | Rejected validation assumption | Surface stretch, intersections, gaps and camera clipping require separate review | D4 |
| R-005 | Large blade sweep with compressed/offscreen hand travel | User-identified failure | Rework grip/body path; current kinetic pass couples visible hands and blade more closely | S5; D3 |
| R-006 | Abrupt front-loaded release followed by floating deceleration | Superseded motion approach | Continuous acquisition of speed and follow-through replace snap-then-float behavior | S5 kinetic brief; D3 |
| R-007 | 610 ms windup in kinetic comparison | Failed existing balance fixture | Violated stationary double-parry assertion; 575 ms chosen. Rule itself remains reviewable | D3; S6 |
| R-009 | Toy-like primitive/lathed knights as final quality | Rejected quality ceiling; backend superseded | Citadel introduced skeletal/imported presentation; final deformation still unfinished | S4; D5 |
| R-010 | Exact same first/third-person pose required | Superseded assumption | Explicit user correction permits camera-specific posing | S5 |
| R-011 | Original 0.7–1.1 m lunge as a fixed requirement | Superseded starting suggestion | Later input-dependent drive is evaluated through spacing and controlled fixtures | S1; D2; D3 |

Authored pose/curve hybrid motion, a multiplayer latency slice, and a final strategic mode are **not rejected experiments**. They remain proposed or open and should acquire results before any acceptance/rejection entry is made.



[Source register](../Sources.md)
