# MEL-37 — reference analysis and manual pose design prompt

> **Dated record; active assignments and status superseded (12 September 2026).** Preserve the technical/design history below. [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns current source, selection, pilot outcome and resume; [DEVELOPMENT](DEVELOPMENT.md) owns operational scope. Step 4 (parry/riposte, branch integration, full-exchange packaging and expansion) is deferred. [Documentation ownership](DOCUMENTATION_OWNERSHIP.md) and [audit](DOCUMENTATION_AUDIT.md) define current authority. Linear owns live execution.

Use the following prompt before authoring the new swing. This pass produces a pose-and-transition blueprint; it does not start animation implementation.

---

You are an animation director preparing **one manually keyed, third-person right-horizontal longsword swing** for MeleeCombatLab. Analyze the actual Mordhau footage and the strongest parts of our existing animations. Design a convincing complete performance with clear preparation, an expressive hand throw, cutting delivery and consequential recovery.

The priority is artistic quality and direct control. The previous procedural arm posing produced contorted wrists, inverted elbows, swollen or disappearing arms and overlapping hands. Do not continue repairing that procedural system. Do not author or render a new animation in this analysis pass.

## 1. Read the current authority

Repository: `D:/Projects/swingmanipulation-recovered-20260911`.

Read its canonical `AGENTS.md` at that absolute path, `Docs/DEVELOPMENT.md`, `Docs/ANIMATION_PROTOTYPE_PIPELINE.md`, the relevant animation guidance in `Docs/ANIMATION_WORKFLOW.md`, and the current top of `Docs/THIRD_PERSON_CHECKPOINT.md`. Policy MCL-DEV-2026-09-08 applies. Reuse evidence already verified in this workstream.

Read the current Notion design pages:

- [Animation](https://app.notion.com/p/3d32e3c3f8f881e08474defe7febb171): visible result, whole-action authorship, moving hilt, load/delivery contrast, extended delivery where effective, intentional exaggeration and authored recovery.
- [Melee Swing Model](https://app.notion.com/p/3d32e3c3f8f881028f05c2a960248ff1): independent FP/TP presentation with shared gameplay authority; natural reach and exact anatomy are not hard artistic constraints.
- [SWING-01 — Mordhau defender animation atlas and implementation details](https://app.notion.com/p/3d52e3c3f8f88192ababd9338ad3797b): actor/action classification, reference interpretation and visible authoring details.

Apply Daniel's latest direction over historical prescriptions: **one manually authored swing**, not the default multi-candidate batch; blade rotation within the hands is allowed; visible hand continuity is the primary problem. Notion owns design, the local checkpoint owns current execution, and old task-status paragraphs do not override newer user feedback.

## 2. Preserve the actual successes

Daniel explicitly said that the **loaded swing, the “throwing” hand motion, and the torso/shoulders loading the swing looked good or reasonably on target**. Treat these as strengths to recover and preserve. Do not restart their design merely to make everything new.

Identify the strongest matching existing examples and record their exact source, frame/time and visible benefit. Daniel's latest praise did not identify a candidate/version, so do not fabricate that attribution or call a whole clip approved.

Useful evidence to inspect, not automatic winners:

- `ArtSource/AnimationLab/MEL37_grip_orientation_correction/index.html` and its immutable D, E and F native sources/previews.
- D's visible idle and correct delivery blade orientation; its whole-action hand motion was rejected.
- E's distinct hand spacing and outward preparation into the gather; its broken arm deformation was rejected.
- F's restored idle and improved connected arm shapes; shoulder pinching and the bent carry wrist remained. F is a pose reference, not an accepted swing.
- Earlier gesture/choreography examples linked in `Docs/THIRD_PERSON_CHECKPOINT.md`, only where they contain a demonstrably stronger loaded pose, hand throw or body load.
- Approved EX_v002 first-person motion, as a protected reference for intent, moving hilt, timing contrast and recovery. Its approval does not transfer to TP anatomy or justify copying poses onto a different rest rig.

For each retained strength, distinguish **human-positive feedback**, **agent-observed improvement**, and **unverified inference**. Preserve the intended motion, not an accidental deformation or a frozen screenshot.

## 3. Analyze Mordhau's motion and transitions

Use `Docs/MORDHAU_REFERENCE_INDEX.md` and `Docs/MordhauAnimationAtlas/README.md` to locate the footage. The verified yellow-mask neutral right-horizontal at source 30.0–31.5 seconds is the primary neutral reference. Supplementary B under `ArtSource/AnimationLab/MEL36_reference/` provides useful hand-placement detail; its weapon/input limitations remain explicit. Do not substitute a parry/riposte entry for a neutral windup or splice two different actors into one supposed performance.

Reuse these focused observations where helpful:

- `Docs/ThirdPersonReference20260908/B/selected-beats.jpg`
- `Saved/MEL37Resume/hand-inversion/ReferenceB-windup-hands.jpg`
- `Saved/MEL37Resume/grip-reference/load-to-delivery.jpg`
- `Saved/MEL37Resume/critic-hand-inversions.md`

Inspect the complete action at native speed where available, then only the frames needed to resolve disputed transitions. If inspection is frame-based, say so; do not claim continuous playback. Keep source timestamps, approximate visual beats and game phase times distinct. Do not invent joint angles, distances, FOV or gameplay constants from footage.

Explain specifically:

1. How the paired hands open outward before gathering into the origin-side load, instead of turning a compact grip near the chest.
2. How torso and shoulders create the load, how the hands launch, and when elbows open. Preserve the useful “throw” and purposeful hilt travel.
3. How each forearm flows into its hand through preparation, release and carry. Track hand identity, palm/knuckle/thumb presentation and elbow side without imposing a fixed world-facing palm or universally straight wrist.
4. How blade centerline direction and axial roll differ. Identify the wrong windup turnover to avoid. The edge toward the attacker's left at idle should be the striking edge; the current delivery edge was confirmed correct. The earlier head-facing-apex rule was retracted.
5. How momentum carries the hands and sword across, how the body absorbs it, and how the action returns continuously to the intact idle.

## 4. Design one sparse manual pose sequence

Propose roughly **7–10 key poses**, adding a breakdown only when it resolves a visible transition: idle, outward preparation, gathered windup, release entry, extended delivery, passage, absorbed carry and return.

For each pose, provide its purpose, reference frame(s), best reusable existing pose, intended torso/shoulder silhouette, placement and orientation of both hands, elbow/forearm shape, blade direction/roll, and the transition into the next pose. Suggest authored timing and spacing from the observed motion, without pretending reference timestamps are exact game events.

Design adjacent poses together. A beautiful loaded pose is insufficient if reaching or leaving it requires a hand flip. Use purposeful arcs, overlap, lead/lag and controlled braking; avoid uniform interpolation between disconnected poses. Preserve the strongest existing load and throw while removing their bad transitions.

The future implementation must use directly chosen native FK poses and editable curves. Python or MCP may set those explicit keys, but must not generate arm poses through per-frame joint solving, automatic stretch, forearm searches, world-up hand locks or a corrective solver stack. Start with connected original-length arms. Small intentional pose cheats are allowed when they visibly help; perfect physics and zero wrist bend are not objectives.

Keep right hand near the guard and left near the pommel. The actual hands and fingers must remain distinct and must not merge or interpenetrate. Let the sword rotate within the grip so the wrists do not supply all blade orientation. Do not use forced wrist torsion, invisible arms or overlapping hands as cheats.

## 5. Produce a reviewable blueprint and stop

Deliver:

- A concise reference diagnosis: what makes Mordhau work and what our current hand transitions get wrong.
- A short keep/change list with exact existing source/frame references for the strongest load, hand throw, torso/shoulder load and intact idle.
- One compact pose-and-transition plan, with evidence and uncertainty clearly separated.
- A native authoring plan naming the existing FK/weapon controls and the few likely transition risks. Do not design another rig or solver.
- A critic brief for the eventual complete 1× preview: intact idle/end pose, separate grips, no conspicuous wrist/elbow inversions or shoulder collapse, no wrong windup turnover, preserved loaded tension and hand throw, coherent cutting delivery and authored recovery. A strong average impression cannot excuse one distracting collapse.

Use one fixed defender camera and plain presentation for later comparison. A second view or dense frame strip is only for a specific unresolved question. Preserve original KN/CF sources, approved EX_v002 source/native/projection, production TP and C++ gameplay. No draft imports, builds, runtime promotion or physics-validation project. Agent selection remains provisional; human acceptance is separate.

**Stop after the blueprint. Do not begin animation authoring in this pass.**

---

Prepared 9 September 2026. Notion pages fetched for this prompt: Animation last edited `2026-09-09T11:32:20.080Z`; Melee Swing Model `2026-09-09T03:47:12.640Z`; SWING-01 `2026-09-09T04:43:49.834Z`. Their design guidance is incorporated above; stale execution status is superseded by the current local checkpoint and Daniel's latest direction.
