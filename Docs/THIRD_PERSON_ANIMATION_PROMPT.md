# New-instance prompt — establish the process for one excellent third-person horizontal swing

> **13 September reference clarification:** Mordhau governs the animation. Baseball/golf wording below was Daniel's descriptive analogy for Mordhau, never an independent target or a reason to override observed motion. Use the current [fresh Cascadeur prompt](CASCADEUR_FRESH_RIGHT_HORIZONTAL_PROMPT.md) for execution.

> **Dated record; active assignments and status superseded (12 September 2026).** Preserve the technical/design history below. [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns current source, selection, pilot outcome and resume; [DEVELOPMENT](DEVELOPMENT.md) owns operational scope. Step 4 (parry/riposte, branch integration, full-exchange packaging and expansion) is deferred. [Documentation ownership](DOCUMENTATION_OWNERSHIP.md) and [audit](DOCUMENTATION_AUDIT.md) define current authority. Linear owns live execution.

## Objective and scope

**Reference correction, 9 September 2026:** use the [actor/action catalogue](MordhauAnimationAtlas/README.md) when consulting the courtyard tutorial. Its RH-A/RH-D demonstrations are right-parry → right-horizontal ripostes, not neutral right-horizontal performances. In particular, the high RH-A entry includes a parry. Keep the verified neutral reference separate from defensive transition evidence.


Create one convincing third-person right-horizontal sword swing: relaxed ready → load → delivery → carry → return. Mordhau is the artistic benchmark: visceral, satisfying, appealing full-body motion with weight, readable intention and responsive player control.

**Current continuation, 8 September 2026:** the user reports pullback clipping and a deformed elbow area in Block05 v002. Follow `Docs/HANDOFF_TP_PULLBACK_ELBOW.md` to locate and repair these visible defects. Preserve useful exaggeration and deliberate deformation; this feedback does not reinstate physical-realism or natural-reach gates. The candidate is not artistically accepted.

The first-person horizontal is okay for now. Preserve it as the accepted baseline. Third-person work is now authorized, but this task covers ONLY the neutral horizontal swing and the repeatable process for authoring it. Do not add parries, ripostes, combos, other attack directions, hit-reaction libraries or a complete combat exchange. Establish quality in this one action before expanding scope.

Act as a combat animation director, character animator and technical animator. Work toward a visible, editable result, not just architecture. Animation quality comes first; anatomy, physics, procedural tools and rigging serve that result. More motion, more bones and more sophisticated solvers do not establish quality.

## Authority and starting point

Deliver in `D:/Projects/swingmanipulation-recovered-20260911`. Read `C:/Users/Daniel Pang/.codex/AGENTS.md` and applicable local instructions. Preserve unrelated dirty work and recoverable versions of replaced assets. Follow the prescribed model/effort policy, prefer sequential work, reuse evidence and keep one compact checkpoint. No remote task updates or messages without authorization.

Read:
- [Animation](https://app.notion.com/p/3d32e3c3f8f881e08474defe7febb171)
- [Melee Swing Model](https://app.notion.com/p/3d32e3c3f8f881028f05c2a960248ff1)
- [REN-01](https://app.notion.com/p/3d42e3c3f8f88199b54eed401936acac) and [KRONK-01](https://app.notion.com/p/3d42e3c3f8f881d8b2e7d845679e8eb7)
- Local `Docs/MEL15_PRODUCTION_HANDOFF.md`, `Docs/CHARACTER_ANIMATION_RESET.md` and relevant current asset manifests.

This scope supersedes earlier third-person deferral and broader exchange milestones. Local receipts establish implementation state, not artistic acceptance.

Preserve EX_v002 revision `EX_v002-source-1615b76b-FBX-6a34514c-native-unreduced-v1`, including its approved source, native first-person playback, projection and timing. Source lives under `ArtSource/CharacterReset/EX_v002`; selection is `Config/EXPreview.json`. Do not compress it into legacy durations.

The old Citadel mesh, skeleton and RC_v008 presentation are retired. Never restore them. CF_v001 is an available fresh anatomical foundation; the current procedural full-body fallback is a placeholder, not accepted choreography.

## 1. Establish the reference before claiming a match

Use a clean, complete third-person Mordhau right-horizontal swing with a comparable two-handed sword and grip. We need visible feet, pelvis, torso, head, hands and weapon from ready through return, ideally at fixed aim while stationary. Watch normal speed first; then inspect the few frames that explain its construction.

Inspect existing supplied material first. Ren/Kronk first-person footage informs economy, hilt transport and manipulation, but cannot establish the player's hidden pelvis, support foot or exact body motion. The dedicated capture in `Docs/MordhauRightReference/reference.json` establishes the first-person reference, not a recovered full-body performance. Historical Hatchet VS Redblue notes describe a defensive exchange and do not by themselves supply this clean neutral reference.

If no suitable external footage is available, tell the user precisely what is missing and request it. Continue source/rig inspection and process preparation while waiting; do not invent a reference match or spend extensive effort polishing speculative choreography. An initial authored interpretation may be useful if clearly labelled as such.

Ideal capture: several separated neutral right-horizontal swings, normal speed, no movement, aim manipulation, feints or combos; entire body and blade visible; stable front three-quarter and side views of the same action; preferably 60 fps, without slow-motion edits or motion blur. A defender-distance view is useful for readability. Identify weapon, grip, source and timestamps. Do not require all angles if one clear view is already sufficient to start.

Make a compact breakdown of ready, load, delivery, carry and return. Record visible support, body silhouette, hilt travel, blade orientation and timing contrast. Distinguish observations from interpretation. Do not claim to recover hidden rig controls or exact 3D measurements from video.

## 2. Author the whole performance

Author body, hands and weapon together. Do not animate a blade guide and then force the body to follow it.

- **Ready:** relaxed stomach/upper-abdomen hands, supported stance, living asymmetry and readiness. Avoid constant raised shoulders or decorative sway.
- **Load:** deliberate hand pullback, shoulder/chest coil and a readable change in support through legs and pelvis. Head and attention remain directed toward the threat. **Latest user correction:** exaggerate the windup enough to visibly load up before release; make the right-side arm/hand preparation and timing contrast readable without changing the approved release clock. At the windup apex, bend the right/weapon-side elbow and point it downward, then open into the extended delivery.
- **Delivery:** coordinate support, pelvis/chest rotation, shoulder girdle, purposeful arm extension and wrist leverage. **User correction, 8 September 2026:** extended arms should convey power through delivery, using a golf swing as an artistic analogy. Do not default to bent elbows; use elbow bends only when necessary or when they make the animation more immersive and convincing. Offset the body's accents according to the motion; do not rotate all joints simultaneously or impose a universal mechanical sequence. The arms must visibly transport and reorient the hilt through a curved path.
- **Carry:** make the arms, torso and stance answer the weapon's momentum. Convey commitment without an uncontrolled spin, stiff elbow lock or gratuitous lunge.
- **Return:** absorb the carry and reorganize continuously into readiness. Avoid snapping to idle, mechanically reversing the outgoing path or adding an ornamental recovery loop.

Weight comes from contrast, spacing, leverage, overlap, support and momentum absorption. Ren supplies economical intention; Kronk reminds us that this foundation must eventually survive expressive manipulation. Neither justifies compulsory flourish. Find the smallest body contribution that makes the whole action convincing, rather than amplifying every joint.

**Latest explicit user direction:** animations do not need to obey physical laws. Use stylized deformation, stretch, exaggerated poses and breakdowns wherever they improve readable, convincing intent and state, as in the Mordhau benchmark. Natural arm reach, anatomical purity and physical plausibility are not artistic acceptance gates. Judge deformation by its complete normal-speed result and whether the action remains visually coherent. Preserve the source deformation faithfully in Unreal. A wide blade arc around a stationary hilt still fails the requested arm-driven swing, regardless of numeric accuracy.

**Latest readability direction:** the arms must drive the entire swing, including load, delivery, carry and return. Develop a clear continuous arc with the hands and arms carrying the weapon; reduce the forward throw followed by withdrawal. Preserve powerful extension while making the complete action read as a swing. This supersedes treating the central extended pose alone as sufficient.

## 3. Use a short authoring loop

Use the existing editable Blender foundation unless a concrete capability blocker justifies a different tool. Confirm available tooling and export capability before any migration. Provide useful pelvis/chest/head, clavicle, arm, hand, foot and weapon controls, with stable FK/IK and space switching where needed. Improve topology, weights or proportions when an observed defect requires it; do not restart an anatomical pose matrix.

Proceed in this order:

1. **Blocking:** establish key poses, support and hilt travel for the complete swing. Include head and feet in the preview. Review silhouette and intent in a stepped pass, then rhythm in continuous normal-speed playback.
2. **Early engine proof:** once the continuous block reads convincingly, import it into Unreal before expensive polish. Confirm the intended body, hand and weapon motion survives the pipeline.
3. **Polish:** refine spacing, arcs, overlap, shoulder deformation, wrist leverage, two-hand contact, foot pivots and recovery. Fix the source performance rather than layering runtime repairs over it.
4. **Matched comparison:** show reference, source and engine at normal speed with comparable views. State one visible weakness, change the relevant authoring controls, and compare again.
5. **Bounded gameplay composition:** after the neutral motion works, test the same horizontal under representative legal aim and movement. Do not generate more attacks.

Procedural curves, mocap and physics can supply editable starting material when useful. Their output still needs animation direction and cleanup. Sparse generic joint oscillations, unedited retargeting and runtime reach solving are not substitutes for authored performance. Scripts should assist the artist-controlled source and iteration loop.

Do not require a fresh permission round for every reversible revision. Show concrete progress and use the user's visual feedback to refine it. Do not declare the final artistic target achieved without human review.

## 4. Preserve one gameplay truth across two views

Use a dedicated third-person clip. Do not flatten the full-body performance to preserve first-person hand visibility, or copy first-person shoulder/arm deformation wholesale onto the external body.

The simulation remains authoritative for attack identity, phase boundaries, legal transitions, canonical blade, damage and contacts. Both views sample the same attack transaction and phase-local clock. Accels/drags remain spatial aim and footwork, not playback retiming. Animation notifies remain cosmetic.

Coauthor third-person body and weapon while consulting the canonical path. Windup/recovery allow greater visual freedom; damaging release must convey the same side, direction, reach class, active interval and contact ordering. Each view's hands attach to its own visible weapon. A cosmetic blade must not visibly miss where its canonical blade hits.

First seek a convincing performance with bounded perspective differences. If the existing canonical release prevents it, create ONE separately selectable coauthored body-and-weapon alternative and derive its proposed canonical data. Compare both perspectives and contact consequences beside the preserved baseline. Do the reversible prototype work, then obtain a decision on that concrete tradeoff before replacing the accepted first-person swing or changing combat semantics. Do not conceal the conflict with accumulating IK/stretch corrections.

Attacks remain in place relative to authoritative locomotion: local pelvis shifts and foot pivots are welcome; attack root motion must not move the capsule. Stationary contacts should look planted. Movement composition must respect locomotion support and foot phase without a hard waist seam, foot sliding or cancelling locomotion. Keep aim adaptation bounded and preserve player control.

Maintain layer order: simulation/canonical weapon → perspective clip at shared phase time → bounded skeletal stabilization → camera-only cosmetics. Runtime IK may stabilize contacts; it must not reconstruct the performance. Preserve source motion through export, compatible skinning, compression, sampling and blending. Ordinary animation edits should require export/reimport and replay, not a C++ rebuild once the consumer is established.

## 5. Review the swing, not the machinery

Use a readable plain character, grounded scene, stable lighting and complete body framing. Review without effects, camera shake or sound concealing weaknesses.

Evaluate:
- Connected body/arm leverage and a transported hilt.
- Readable preparation, decisive delivery, supported carry and purposeful return.
- Appealing changing silhouettes, coherent stylization, asymmetry and purposeful overlap; controlled anatomical exaggeration is allowed.
- Clear attack origin and threat at defender combat distance.
- Stable grips and convincing feet without large runtime reconstruction.
- Preserved responsiveness, contact truth and first-person baseline.
- Faithful source-to-Unreal choreography and deformation.

Deliver a short normal-speed reference comparison and synchronized first-person, full-body external and defender views of this SAME horizontal attack. Use extra angles, slow motion and overlays only to diagnose specific issues. If tools only permit frame inspection, state that limitation; do not claim continuous playback acceptance.

After the visual benchmark works, use one compact replay covering neutral repetition, hit/miss and representative legal aim plus movement. Run affected gameplay and source-fidelity checks only. Use one independent review for consequential implementation changes. Avoid broad pose sweeps, repeated unchanged checks and unrelated legacy-failure investigations. Geometry checks establish correctness, not Mordhau-level artistic quality.

## Deliverable and stopping point

Deliver one polished, reviewable third-person horizontal swing; editable source; its native runtime assets and any versioned weapon data; a reproducible preview/replay; and a compact process handoff. Record the reference, selected revision, what preserves the first-person baseline, known visual weaknesses, relevant verification and the exact edit → preview → export → Unreal loop.

This swing is the benchmark for deciding whether the process works. Do not expand the library or build the parry/riposte exchange in this task.

Start with reference suitability, source inspection and a brief account of the concrete authoring decisions. Then produce the complete blocking pass and iterate toward the scoped benchmark. If reference footage is the material missing input, ask for that specific footage rather than substituting engineering complexity for visual evidence.

