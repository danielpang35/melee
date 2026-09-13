> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../../DEVELOPMENT.md) for active work.

# MeleeCombatLab

Project bible · Version 1 · 6 September 2026

**A competitive first-person melee slasher with the immediacy and clarity of a competitive FPS, the bodily satisfaction of Mordhau, and deep skill expression through aim, timing, footwork, and readable deception.**

This bible consolidates seven available earlier project conversations, their relevant supplied briefs, and the project's design and development records. It preserves the requested hierarchy. ChatGPT history was unavailable through the task listing; no archived Codex tasks were returned. It is therefore a synthesis of accessible history, not a claim to have reviewed inaccessible chats. Notion publication remains pending because no Notion tools are exposed in this session.

## How to read this bible

**Established** means explicit user direction or a retained foundational design rule. **Current implementation** describes code, configuration, or a dated implementation report; it does not imply player acceptance. **Proposed** means a recommendation or newly organized experiment awaiting evaluation. **Open** means the reviewed sources do not settle the question. **Superseded** means a later correction replaced an earlier instruction or result.

Later explicit user corrections govern conflicts. Implementation reports establish what was attempted and measured, not what the project must permanently become. Numeric tuning belongs in Balance / Tuning; principles describe the experience those numbers must serve. Source IDs below refer to the source register at the end of this page.

## 00 — Project Vision

### The promise

“Medieval CS:GO” is the project's identity: precise first-person control, a very high mechanical ceiling, readable engagements, individual expression, and an eventual structure that creates teamwork and strategy. Mordhau is the reference for physical immersion and satisfying melee, while CS2 is a long-term reference for visual sharpness. These references identify desired qualities; they do not prescribe copied assets, exact combat timings, or a replica game mode. [S1, S6]

The player should feel that their body generated the swing, their aim and footwork determined contact, and the opponent's response followed intelligible rules. A miss, hit, parry, and riposte should each produce a different physical consequence. Even an empty-air swing should be satisfying. [S5, S6]

### Priority order — established

1. Exceptional combat and game feel.
2. Exceptional swing animation and weapon motion.
3. Movement and combat footwork supporting that feel.
4. Competitive readability.
5. AAA visual refinement and great performance, targeting 144 fps on mid-tier PCs.

This order comes from the latest user summary. Readability, simulation correctness, and low input latency still constrain how improvements are achieved; the priority list does not authorize unreadable or misleading combat. [S6]

### Product scope

**Speed of development is key.** Favor short iteration loops, playable progress, and direct decisions. Keep routine process documentation lean where that improves efficiency. **The project bible is an exception: its rigor, accuracy, and upkeep must not be sacrificed for speed.** Keep established principles, system descriptions, current direction, and consequential decisions coherent and current as the project evolves. [Current user direction]

The immediate product is a single-player combat laboratory centered on one longsword, programmable opponents, repeatable encounters, and rapid tuning. It should be compelling enough to keep dueling before adding breadth. The long-term product is a competitive multiplayer melee game with meaningful team strategy. Team size, objectives, round structure, economy, matchmaking, and progression are open. [S1, S6]

The current quality frontier is one complete, exceptional longsword exchange. More weapons, broad team-mode production, elaborate environments, and secondary progression do not answer the present problem of weak bodily motion. The one-exchange milestone is the latest recommendation being triaged, not a claim that its implementation or acceptance is complete. [S6, S7]

### What success feels like

The player loads the weapon; torso and hands transmit force; the blade gains speed through a useful cutting region; aim and movement change when it arrives; contact produces resistance and a visible recipient response; recovery carries the history of the exchange. Controls remain immediate throughout the legal input windows. A defender can understand and learn from the result. [S5, S6]

## 01 — Design Principles

### Combat

**Iterate quickly and maintain the bible.** Choose the shortest useful path to a playable improvement. Minimize unnecessary process paperwork while keeping this bible accurate, consistent, and updated when design direction or consequential decisions change. [Current user direction]

**Combat feel is the authority.** Existing trajectories, timing, movement assumptions, rigs, and presentation can change when evidence supports a better result. Co-design simulation and animation until the motion itself is excellent. [S3–S6]

**Skill emerges from spatial rules.** Accels and drags result from rotating and translating a timed weapon trajectory through space. Aiming around someone, deliberately missing, choosing contact timing, and changing range are legitimate expressions of mastery. Mouse direction must not secretly accelerate or slow the attack clock. [S1, S5]

**Reliable authority makes skill learnable.** C++ combat simulation owns phase, blade pose, defense, contact, and damage. Rendering, audio, camera, and animation express the resolved state. Root motion and animation notifies must not independently decide damage. The visible blade should agree with authoritative geometry. [S1, S4, S5]

**Defense has intentional asymmetry.** A parry provides a generous aimed catch; a chamber is an ordinary matching attack with brief defensive protection. Their differences create decisions around timing, deception, and commitment. A delayed attack can outlast chamber protection naturally. [S1]

**Initiative must have visible consequences.** Flinch cancels a non-riposte swing; a riposte is a recognizable exception with distinct motion and looser turning. Combos alternate sides, cannot themselves chamber, and wind up more slowly than ordinary strikes or stabs. [S1, S2]

Acceptance lens: Did the player cause the outcome? Can the defender explain it? Does repetition reveal learnable control? Did an improvement survive actual play as well as regression checks?

### Movement

**Immediate intent, physical velocity.** The player communicates direction now; body velocity can accelerate, brake, and redirect over time. Weight should come from velocity response, foot placement, body motion, and sound rather than delayed input. [S5, S6, D2]

**Footwork is an attack and defense system.** Approaching, withdrawing, circling, sprint transitions, and recovery movement must change reach and contact timing through collision-resolved translation. Movement cannot be a cosmetic layer under a stationary tracer. [S1, S5]

**Commitment must preserve steering.** Attack drive may use forward intent and inherited momentum, but must not pull toward targets, grant an uncontrolled shove, or make a stationary attack automatically dash. Reversal and braking remain meaningful. The original speculative lunge distance is not a permanent requirement. [S5, D2, D3]

Acceptance lens: Test entry to range, withdrawal against drags, lateral evasion, whiff punishment, sprint-to-attack, and reversal during recovery. Weight is successful only when these remain predictable and controllable. [S6]

### Animation

**The body must appear to generate the sword.** Feet, pelvis, torso, shoulders, elbows, wrists, hilt, and blade form one kinetic chain. Visible hand travel is central to power; a broad blade arc with nearly stationary hands fails this principle. [S5]

Use the seven-part design framework as one action: hilt translation, blade orientation, anticipation, elbow/hand path, release acceleration, follow-through, and recovery. Horizontal, overhead, underhand, and stab families need distinct anatomical solutions. [S4, S5]

Load should feed release continuously. Strong acceleration does not mean starting at maximum velocity and floating through the remainder. The later kinetic brief favors a smooth exit, rapid acquisition of speed, useful contact-sector energy, and continued travel. Position continuity alone is insufficient when velocity visibly jumps. [S5, D3]

Recovery remembers the outcome: a miss carries, a body hit loses energy, a parry redirects or arrests, a wall rebounds, a combo transfers into the opposite side, and a riposte converts defense into offense. Cosmetic emphasis cannot postpone a legal input or pause the combat clock. [S5, S6]

**First-person and third-person poses may differ.** Camera-specific shoulders, elbow paths, mesh visibility, and composition are permitted by explicit user correction. Both views must support the same gameplay blade and preserve external telegraphs. Identical poses are not a quality requirement. [S5]

Current architecture uses shared simulation state, procedural posing, and grip constraints. A small authored pose/phase-curve set with procedural adaptation and final IK is a proposed next experiment. Control Rig is an option, not a committed implementation requirement. [D3, D4, S6]

Acceptance lens: inspect moving surfaces, wrists, grips, shoulder seams, intersections, and near-plane clearance at normal speed and extreme pitch. Fixed bone lengths, exact blade endpoints, and passing pose tests cannot certify good anatomy. The user rejected a numerically passing preview. [S5, D4]

### Camera & Input

Mouse aim should have minimal perceptible latency, no default aim acceleration, and no excessive smoothing. No target lock, melee aim assist, magnetic view rotation, or magnetic attack redirection. [S1]

Turncaps define the permitted angular envelope by state and phase. Discard excess mouse delta rather than queueing a later snap. Keep view intent, combat orientation, body orientation, guard orientation, and weapon orientation conceptually separate. Guard geometry follows actual capped guard orientation. [S1]

Directional selection uses recent mouse intent, a configurable deadzone, and deterministic fallback. Six strike origins plus a dedicated stab are the lab scope; the internal angle representation should support later continuous selection. Do not delay the click while waiting for a gesture. [S1]

Baseline controls: WASD move; mouse look; Shift sprint; Ctrl crouch; Space jump; LMB directional strike; wheel-up stab; RMB parry; Q feint. Contextual attack input produces legal morphs, combos, and ripostes. Bindings remain configurable. [S1]

Camera motion supports bodily sensation with restrained directional impulses and locomotion cues. It must not obscure attack lines, substitute for weak weapon motion, or delay actual aim. Current FOV is a tunable implementation value. [S1, S5]

### Visual Direction

**Bright, crisp, grounded medieval competition.** The established setting is a sunlit low-fantasy tournament in a maintained stone courtyard. The latest direction emphasizes clean silhouettes, strong player/background separation, restrained heraldry, and competitive clarity. High fidelity should strengthen these qualities. [S1, S3–S6]

| Element | Direction | Practical review criterion |
|---|---|---|
| Architecture | Pale limestone/sandstone; arcades, gates, readable roofline and landmarks | Architecture frames bodies without hiding lower attacks or movement |
| Composition | Open duel space, broad circulation, simple fountain obstacle | Range, escape paths, and collision are understandable during combat |
| Light | Clear sunlight, cool filled shadows, stable exposure | Weapons and armor remain legible in sun and shade |
| Knights | Functional medieval proportions; steel, mail, padded cloth, leather | Clear shoulders, elbows, hands, legs, and attack origin in motion |
| Weapon | Hero-quality blade, guard, handle and steel response | Grip is believable and visible reach agrees with damage geometry |
| Identity | Muted blue and red heraldry; sparing gold | Identity reads without ornamental noise dominating the fighter |
| Materials | Believable roughness, modest wear, useful silhouette/detail | Steel avoids chrome; stone avoids noisy or stretched texture scale |
| Combat effects | Brief directional gold parry and cyan chamber cues | Contact is readable in sunlight and the next attack remains visible |
| Audio | Clear swing/contact/footwork cues above ambience | Fountain and environmental sound do not mask combat information |

Working palette from the style record: warm limestone **#C9B892**, shadow blue-grey **#667785**, heraldic blue **#294A68**, muted red **#813D36**, leather **#3C2B20**, and cool neutral steel. The Citadel pass adds charcoal slate and sparing gold. These are working art values, not immutable color specifications. [D5, D6]

Avoid muddy grimdark grading, heavy fog, noisy fantasy effects, excessive bloom, busy backgrounds, dense debris or foliage in attack lines, oversized fantasy armor, and ornate animation flourishes that hide commitment. The player should read the fighter before the decoration. [S6]

The fountain is the original courtyard anchor and a readable movement obstacle; the later presentation mandate permits rebuilding the courtyard if that improves the result. Preserve the purpose—orientation, open footwork, intelligible collision—rather than treating the exact fountain layout as sacred. [S1, S4]

**Quality target:** premium armored duelists, convincing hands and deformation, powerful readable motion, and an attractive tournament space. Procedural fallback assets, successful imports, and sharper materials alone do not establish AAA quality. Broad art expansion follows a convincing exchange. [S4–S6]

**Performance direction:** Competitive targets 144 fps at 1080p, approximately 6.94 ms/frame, on a modern six-core CPU, 16 GB RAM, and RTX 3060/4060 or RX 6600/7600-class GPU. High targets 90 fps; Showcase prioritizes appearance. Competitive must retain the art direction with expensive features disabled. Profile representative combat and frame-time distributions; local editor averages are not target certification. [S1, S6, D6]

## 02 — Systems

### Melee Swing Model

**Intent:** make aim, timing, and translation control a coherent moving weapon, with enough active travel for meaningful acceleration and delay of contact. [S1]

Lifecycle: **Neutral → Windup → Release → Recovery → Neutral**, with explicit legal branches for feint, morph, combo, flinch, parry, and riposte. The simulation decides legal inputs and damage windows; presentation reads them. [S1]

Six origins are upper-left/right, horizontal-left/right, and lower-left/right. Names describe where the attack begins. A right horizontal begins on the player's right and travels left. Stab is a separate family. Raw angle storage and angular matching remain compatible with eventual continuous selection. [S1]

Weapon state is a function of attack definition, phase progress, combat/view orientation, and character translation. Sweeps must cover movement between simulation steps and avoid duplicate hits on one target during one attack. Anti-spin/glancing constraints preserve a learnable manipulation envelope. Accels/drags change world-space contact time without changing elapsed phase time. [S1]

Current kinetic implementation includes a 160-degree blade arc, 132-degree grip-center arc, tunable regular-strike acceleration, linear riposte progression, Hermite boundary tangents, result-dependent carry/rebound, and movement telemetry. These are existing systems to evaluate, not features to propose as if absent. Their combined visual quality is unapproved. [D3, D4]

Combos buffer within a legal release interval and transfer to the opposite side without snapping through neutral. Combo attacks cannot initiate chamber protection. The user's cadence rule is explicit: combo windup must be slower than normal strike/stab windup. [S1, S2]

Feints cancel a legal windup and allow defensive response without waiting for the cosmetic return. Morphs transition strike↔stab during an eligible windup portion and alter commitment timing visibly. Exact eligibility and balance values remain tunable. [S1]

Open work: anatomical path design, reach-correction magnitude, family-specific posing, normal-speed defender readability, and outcome-complete feedback. Do not enlarge arcs or shorten timings simply to conceal weak hands and body motion. [S5, S6]

### Blocking & Parrying

The established defense is a timed aimed parry, not an assumed indefinite held block. A body-covering box plus extended forward catch region gives ordinary parry generous coverage. Both follow actual guard orientation under guard turn limits. The catch region is intentionally more forgiving against manipulation than a chamber. [S1]

A chamber is a matching ordinary attack with a short defensive window, angular/facing requirements, and no extended cone. It does not require literal blade-on-blade intersection as its central criterion. A stab chambers a stab primarily through timing. If the opponent feints, the chamber attempt remains an attack; if the incoming drag arrives too late, chamber protection has expired. A generic feint back to neutral then parry supplies the defensive escape without a bespoke chamber-feint-to-parry state. [S1]

A successful parry opens a riposte window. Riposte direction remains selectable; its distinct arm/swing motion and looser turncap make the exception readable. The user's flinch rule preserves a riposte while canceling other swings. [S1]

Preserve defense ordering, cone orientation, angular matching, early/late timing, and once-per-target resolution coverage when changing trajectories. Current box/cone numbers are a baseline, not immutable geometry. A stationary double-parry fixture expresses a balance choice that merits explicit review if future timing work conflicts with it. [S6, D3]

Open: future shields or held-block systems, final stamina economics, and the eventual multiplayer defense/prediction contract. No rule is invented here for those systems.

### Movement

Current movement uses an engine-independent locomotion law applied through a custom CharacterMovement component. Input intent is immediate; acceleration, braking, redirect, and reversal resolve planar velocity. Unreal handles collision, floors, stepping, slopes, jumping, and actual translation. Combat consumes that translation. [D2]

Forward, lateral, and backward targets differ; mixed directions use an elliptical envelope to avoid a diagonal speed bonus. Sprint is a request gated by forward intent, grounded state, crouch, and neutral combat. Entering combat lowers the target without an instantaneous velocity reset or animation lock. Phase modifiers scale travel targets while retaining steering. [D2]

The later kinetic pass expands the earlier modest forward-bias model: forward-input-dependent drive peaks early and ends partway through release; inherited forward momentum partially carries and decays; reversal stops drive. One controlled fixture recorded about 17.1 cm extra displacement. That is a fixture result, not every attack's travel distance. [D3]

The movement contract's earlier release-bias prose and the original 0.7–1.1 m speculative lunge should not override the later implementation. Review source/config and actual exchanges before selecting a new distance. [S1, D2, D3]

Open: crouch acceleration, high-skill reversal balance, air-control exploits, sprint stopping feel, and networking saved-move/prediction support. These are playtest and future implementation questions, not verified deficiencies. [D2]

### Game Structure

**Established now:** a single-player combat lab; one developed longsword; a passive damage dummy with infinite health by user request; deterministic attacking patterns; reset, diagnostics, live tuning, and reproducible tests. Programmable opponents take priority over sophisticated dueling AI. [S1]

**Established ambition:** a competitive multiplayer melee slasher where individual mastery and teamwork/strategy both matter. [S6]

**Open product decisions:** team count/size, match and round rules, win conditions, objective design, economy, equipment selection, map roster, skill/rank system, progression, and presentation of team identity beyond the working color variants. “Medieval CS:GO” does not by itself accept bomb planting, five-player teams, or a buy phase.

**Proposed sequence:** prove the local exchange, test a narrow multiplayer latency/prediction slice, then expand weapon and team-mode production. The networking slice is a recommendation from reference analysis, not completed work or a commitment to a particular network design. [S6]

## 03 — Current Development

### Current Milestone

**Working milestone: one exceptional longsword exchange — load, swing, contact, reaction, recovery.** Latest recommendation carried into project triage. Status: foundation repair requires fresh combined visual validation; milestone implementation and human acceptance are not established. [S6, S7, D4]

| Gate | Concrete deliverable | Exit evidence |
|---|---|---|
| 1. Trustworthy baseline | Exact source/config/assets/module checkpoint and current arm review | Fresh first-person and external captures; inspect surfaces, grips, seams, clipping and all relevant poses |
| 2. Horizontal pair | Revised right/left load, hand transfer, blade passage and recovery | Same-timing A/B at normal speed; visible hand/body causality and blade agreement |
| 3. Complete outcomes | Miss, body hit, parry and riposte branches | Contact-synchronized attacker/recipient motion and distinct feedback |
| 4. Footwork | One moving range-edge exchange plus approach, withdrawal and reversal cases | Contact timing/displacement telemetry paired with human control/readability assessment |
| 5. Acceptance | Playable comparison, first-person/opponent videos and relevant tests | User play confirms power, clarity and earned outcomes; no unreviewed visual defects |

These gates are a proposed organization of the latest next-step assessment. Chamber and wall branches are required follow-on coverage before extending to all six origins and stab. Performance and competitive regression checks run alongside relevant changes. [S6]

Current recorded state: module 1004 built successfully and the latest shoulder assets imported; their combined arm result has not been rendered/tested in the handoff. Earlier native and rendered suites passed on earlier checkpoints, but the user rejected the visuals. The old editor may still have old code/assets loaded. The working tree contains substantial uncommitted work. This bible performs no build or fresh gameplay certification. [D4; local configuration/status inspection]

### Task / Experiment Database

The companion CSV is a proposed seed backlog, not a live Notion database or a synchronized copy of Linear. No owner or due date has been invented. The concurrent Linear triage task was in progress when reviewed; reconcile IDs/status with that project before importing duplicates. [S7]

Recommended properties: Name (title), ID, Type (task/experiment), Area, Priority, Status, Hypothesis / Problem, Next Action, Acceptance Evidence, Depends On, Source, Owner, Result / Decision. Proposed views: Current Milestone, Experiments Awaiting Review, Visual / Animation, and Deferred Product Questions. These database conventions are editorial proposals.

| ID | Priority | Task / experiment | Status | Acceptance evidence |
|---|---|---|---|---|
| B-001 | P0 | Validate newest combined arm repair | Needs validation | Fresh checkpoint and normal-speed first/external views; surface/clip/grip inspection |
| B-002 | P0 | Compare authored horizontal pose/curve approach | Proposed | Same-timing A/B; coherent hands, body and authoritative blade |
| B-003 | P0 | Complete hit/miss/parry/riposte outcome chain | Proposed | Distinct synchronized motion and recipient consequence |
| B-004 | P1 | Replace placeholder combat audio | Proposed | Authored swing/metal/body/exertion/footstep set; cues remain clear |
| B-005 | P1 | A/B release drive and momentum carry | Proposed | Range-edge timing, stop/reversal, displacement and subjective control |
| B-006 | P0 | Defender-readability gate | Proposed | Origin, commitment, feint/morph and outcome readable without debug labels |
| B-007 | P1 | Review timing and double-parry contract | Open design question | Explicit balance decision and corresponding regression expectations |
| B-008 | P1 | Packaged target-tier performance measurement | Proposed | Hardware/settings/checkpoint plus mean, p95/p99 combat frame times |
| B-009 | P1 | Extend approved motion to remaining families | Deferred until horizontal acceptance | Distinct overhead/underhand/stab anatomy and transition coverage |
| B-010 | P2 | Refine knight/weapon/environment art | Deferred behind exchange | Premium grips/materials/silhouettes with measured cost |
| B-011 | P2 | Narrow multiplayer prediction/latency prototype | Proposed future work | Document contact/defense consistency under specified latency conditions |
| B-012 | P2 | Define strategic match structure | Open | Accepted objectives, round/team rules and prototype success criteria |

## 04 — Playtesting

### Findings

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

### Repeatable review protocol — proposed consolidation

Record exact build/module, config, asset revision, frame rate, camera, scenario, and whether evidence is automated or human. Capture neutral/accel/drag on all six directions, stab, combos, feints, morphs, parries, chambers, ripostes, walls and range-edge movement as relevant to the change. Pair first-person footage with the defender's view. [S5, S6]

Normal-speed review asks: Does it feel powerful? Do hands carry the weapon? Can a defender identify origin and commitment? Does impact explain the outcome? Is recovery continuous? Can the player steer and defend when the state permits? Debug labels should be disabled for readability judgment.

Numerical review asks: Are blade endpoints aligned? Are sweeps robust? Do accels and drags produce meaningful contact-time differences? Are legal defense and combo rules preserved across frame rates? Does reach correction remain small enough that it is not reshaping the intended motion? Report unavailable measurements explicitly. [S6, D3, D4]

Retain failed and rejected captures with their checkpoint labels. A later green test must not silently relabel an old rejected video as final. Human acceptance and mechanical correctness are separate recorded outcomes. [D4]

### Balance / Tuning

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

## 05 — Decision Log

### Accepted Decisions

“Accepted” here describes established design intent. It does not certify implementation quality. Entries with a source document rather than an explicit later user correction retain the foundational rule unless a future decision changes it.

| ID | Decision | Rationale / consequence | Source |
|---|---|---|---|
| A-001 | Combat feel takes priority; existing implementation may change | Improve actual play instead of protecting weak mechanics | S4 correction; S5; S6 |
| A-002 | Competitive first-person melee identity: Medieval CS:GO | Precise input, high skill ceiling, clarity, eventual strategic teamwork | S5; S6 |
| A-003 | Simulation owns blade, phase, contact and damage | Visuals and collision must tell the same story | S1; S5 |
| A-004 | Accels/drags emerge spatially | Aim and footwork change contact without playback-speed tricks | S1; S5 |
| A-005 | Parry and chamber remain asymmetric | Generous aimed catch versus brief matching-attack protection | S1 |
| A-006 | Combos alternate sides and cannot chamber | Readable continuity and explicit defensive eligibility | S1 user corrections |
| A-007 | Combo windup is slower than normal strike/stab | User rejected fast cadence; 700 ms is current baseline | S2; D1 |
| A-008 | Flinch cancels swings except riposte; riposte has distinct motion and looser cap | Initiative and exceptions must be visible | S1 user correction |
| A-009 | First-person posing may differ from third person | Camera composition and anatomy can be solved per view | S5 user correction |
| A-010 | Simulation and animation are co-designed | Hands/body should generate plausible authoritative motion | S5 |
| A-011 | Grounded movement with immediate input | Weight supports competitive control and spacing | S5; S6 |
| A-012 | Bright, restrained medieval tournament direction | Strong player/background separation and readable attack lines | S1 visual brief; S6 |
| A-013 | AAA is the quality target; placeholders are replaceable | Useful scaffolding does not set the art ceiling | S4; S5 |
| A-014 | 144 fps at 1080p on mid-tier hardware is the Competitive target | Performance is judged with settings, hardware and frame pacing | S1 visual brief; S6 |
| A-015 | Actual visual review accompanies mechanical tests | A passing preview was still rejected for clipping and contortion | S5; D4 |
| A-016 | Single-player lab first; longsword and deterministic opponents | Prove combat before production breadth | S1 |
| A-017 | Mordhau Montage VI is preferred over GregTage VII | Latest explicit reference selection; emulate physical qualities, not necessarily art | S5; S6 |
| A-018 | Development speed is key; bible rigor is preserved | Favor playable iteration and lean process paperwork while keeping the bible accurate, coherent and current | Current user direction |

### Rejected Experiments

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

## Source register and maintenance

Task titles are preserved verbatim. Task IDs support retrieval in Codex. Relevant user messages and final responses are saved in Sources/Conversation excerpts.md alongside this bible. Historical task instructions are evidence for design intent, not authorization to execute the old implementation work during this documentation task.

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
