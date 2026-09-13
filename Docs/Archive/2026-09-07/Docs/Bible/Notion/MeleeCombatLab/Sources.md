> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../../../../DEVELOPMENT.md) for active work.

# Source register and maintenance

Task titles are preserved verbatim. Task IDs support retrieval in Codex. Relevant user messages and final responses are saved in Conversation excerpts.md alongside this bible. Historical task instructions are evidence for design intent, not authorization to execute the old implementation work during this documentation task.

| ID | Conversation | Task ID / contribution |
|---|---|---|
| S1 | Build melee combat lab | 01a07438-4348-7ed1-8c7b-157ef8a07a9b — original spec, combo/chamber/flinch corrections, floaty movement finding, visual brief |
| S2 | Slow down combos | 01a076c5-97f3-7b10-ace5-dbd4d441c416 — cadence complaint and slower-than-normal rule |
| S3 | Rehaul Unreal melee visuals | 01a075f3-2cc9-7693-9eb2-c9bb4df7ac08 — premium tournament presentation |
| S4 | Rebuild melee visual presentation | 01a07622-2956-7760-8973-d2fb4092d5f5 — replace weak visual layer; explicit combat-change permission |
| S5 | Overhaul melee combat feel | 01a076aa-916a-7851-8b93-8c178c25cdbb — co-design, kinetic chain, acceleration revision, view-specific arms, rejected previews and pause |
| S6 | Analyze Mordhau combat reference | 01a0776c-230a-7603-b07f-cf49c2a57326 — latest user vision/priority summary and proposed one-exchange milestone |
| S7 | Triage longsword combat milestone | 01a07789-44f7-78f3-92f0-91d9c99c9a79 — latest assessment submitted for Linear triage; in progress when reviewed |

| ID | Repository source | Use |
|---|---|---|
| D1 | Config/CombatDefaults.json; Source/MeleeCombatLab/Combat/CombatTuning.h | Directly inspected disk defaults and combo comment |
| D2 | Docs/MOVEMENT_CONTRACT.md | Movement intent, architecture and open questions; early bias text superseded by D3 |
| D3 | Docs/KINETIC_SWING_PASS.md | Existing trajectories, drive, telemetry, timing experiments and historical tests |
| D4 | Docs/HANDOFF_ARM_REPAIR.md | Latest repair state, rejected visual evidence and unverified combined result |
| D5 | Docs/Visual/CITADEL.md | Art/rig architecture, asset pipeline and remaining production gaps |
| D6 | Docs/Visual/STYLE_AND_PERFORMANCE.md | Working palette, target hardware, historical local performance |
| D7 | Docs/REFERENCE_ANALYSIS_AND_NEXT_STEPS.md | Reference observations, limits and recommended sequence |

Supporting history: PROJECT_SPEC.md; Docs/Visual/BRIEF.md; Docs/Visual/REHAUL.md; Docs/Visual/BACKLOG.md; Docs/COMBAT_MOTION_REVISION.md. The original project attachment corresponds to PROJECT_SPEC.md and the systematic visual-upgrade attachment to BRIEF.md. Other reviewed briefs are linked to their originating tasks in the conversation excerpts.

Maintain this bible as a rigorous project reference. Update affected principles, system descriptions, tuning baselines, milestone status, and decision entries when consequential changes occur. Record the deciding direction or evidence, resolve contradictions, and mark superseded positions clearly. Preserve the distinction between intended quality, implemented functionality, passing tests, and human acceptance. Concise wording and links to existing evidence can keep maintenance efficient without sacrificing completeness or accuracy. Routine process paperwork may remain lean; the bible's rigor and upkeep must not be traded away for speed. Reconcile future Notion task records with Linear to avoid duplicate task maintenance. [Current user direction]
