> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../../../../../DEVELOPMENT.md) for active work.

# Findings


| Finding | Evidence and status | Implication |
|---|---|---|
| Early combat and manipulation improved | User said combat felt noticeably better and manipulation closer to final in Build melee combat lab | Preserve successful spatial control while improving physical presentation |
| Movement felt floaty | Direct user observation in the original build task; cause was uncertain | Assess response, body cues and speed separately; do not assume acceleration alone explains it |
| Combo cadence was too fast | Direct complaint after 420 ms combo change; user then required 700 or 750 ms and slower-than-normal windup | 420 ms and 600 ms experiments are superseded; current value is 700 ms |
| Sword traveled farther than the hands appeared to swing | Direct user complaint in Overhaul melee combat feel | Evaluate visible grip travel and anatomy, not blade arc size alone |
| Arms deformed, clipped and contorted | User rejected recorded previews despite numerical passes | Actual surface and camera review are mandatory; repair remains unapproved |
| Bone-length metrics missed surface damage | Repair report measured worst sampled arm edge stretch at 11.47222× before rigid-section repair | Bone reach and blade alignment are incomplete visual metrics |
| Partial rigid-section repair reduced some stretch but left other issues | First-person sampled ratios about 1.00008–1.00009; external worst 1.81816; near-plane fragments remained | Do not call the final shoulder/camera combination fixed without fresh evidence |
| Reference suggests a coherent full exchange | Earlier montage frame review noted hand travel, contact, recovery and close-range tracking | Use the reference for motion relationships; exact timing/latency/audio conclusions remain unsupported |
| Local FPS did not certify target performance | Older rehaul Competitive mean 5.855 ms, p95 7.799 ms on RTX 5070/Ryzen 1600 | Target-tier packaged frame pacing remains an open measurement |

Sources: S1, S2, S5, S6, D4, D6. These are dated findings, not new playtest results from this bible pass.


## Repeatable review protocol — proposed consolidation

Record exact build/module, config, asset revision, frame rate, camera, scenario, and whether evidence is automated or human. Capture neutral/accel/drag on all six directions, stab, combos, feints, morphs, parries, chambers, ripostes, walls and range-edge movement as relevant to the change. Pair first-person footage with the defender's view. [S5, S6]

Normal-speed review asks: Does it feel powerful? Do hands carry the weapon? Can a defender identify origin and commitment? Does impact explain the outcome? Is recovery continuous? Can the player steer and defend when the state permits? Debug labels should be disabled for readability judgment.

Numerical review asks: Are blade endpoints aligned? Are sweeps robust? Do accels and drags produce meaningful contact-time differences? Are legal defense and combo rules preserved across frame rates? Does reach correction remain small enough that it is not reshaping the intended motion? Report unavailable measurements explicitly. [S6, D3, D4]

Retain failed and rejected captures with their checkpoint labels. A later green test must not silently relabel an old rejected video as final. Human acceptance and mechanical correctness are separate recorded outcomes. [D4]



[Source register](../Sources.md)
