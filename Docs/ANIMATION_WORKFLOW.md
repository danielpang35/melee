# Rapid animation production

Current prototype procedure: [Animation creation and ideation pipeline](ANIMATION_PROTOTYPE_PIPELINE.md). Use its Python/MCP tool split, shared-assumption check, complete candidate comparison and bounded refinement loop. Historical examples below remain reference material; the current native adapter README governs commands and source editing.

## Current character — Knight KN_v002

New `AnimationLab.py new NAME` batches use the Knight body through the existing
native control adapter. The source is
`ArtSource/UserKnight/KN_v002/Knight_Animation.blend`: animate `KN01_Body` through
`KN01_Rig`; `Knight Armor (Deferred)` retains the supplied shell and is hidden in
editing/rendering. The body is CF-derived anatomy fitted to the Knight, because
the supplied FBXs contain no complete underlying body. The new rest skeleton is
independent; matching bone names do not authorize binding old CF/EX/TP clips.

The default produces one technical control proof, not four artistic candidates.
Its `CF_*` control names and `cf-controls-v1` adapter ID remain compatibility
identifiers; the snapshotted character is KN_v002. Create and edit complete new
performances on this body. `--adapter legacy` explicitly reproduces the historical
CF batch route described below. Existing snapshots stay immutable and retain
their own character. See [Knight checkpoint](USER_KNIGHT_CHECKPOINT.md).

`Tools/PrepareKnightBody.py` rebuilds the fitted rest body and separate hidden
armor from preserved sources; `Tools/ImportKnightBody.py` is the explicit body
import. Neither runs automatically during candidate generation. The [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns the current test-scene motion binding; `-KnightArmor` restores
the archived full Knight and `-FoundationBody` the historical foundation route.

## Historical direction — 9 September 2026 architecture reassessment

Daniel rejects the current complete motion as stiff and weak and requests a comprehensive audit and plan. The active [architecture plan](MORDHAU_ANIMATION_ARCHITECTURE_PLAN.md) supersedes earlier local-refinement assignments and universal zero-wrist, low-elbow or clear-face prescriptions. Target a powerful reference-directed hand launch, exaggerated but continuous body/arm/grasp motion, and a convincing complete performance. Subtle wrist articulation and useful nonphysical deformation are allowed; the sword follows the authored grasp. Current local refinement is stopped. Earlier wrist-direction feedback is not whole-animation acceptance. Preserve EX/runtime/gameplay; this audit does not itself implement or promote the new architecture.

Policy MCL-DEV-2026-09-08 in [AGENTS.md](../AGENTS.md) applies to every agent. One owner takes a batch through selection and brief refinement. No per-draft engine proof.

The [Mordhau polish process](MORDHAU_POLISH_PROCESS.md) specifies repeated animation-critic diagnosis, implementation and verification through source and playable acceptance. For current neutral RH comparison, corrected yellow-mask N-RH is primary; older A/B examples mentioned below are supplementary. Selection and human acceptance remain in THIRD_PERSON_CHECKPOINT.md.

The [confirmed visual direction](MEL17_REFERENCE_ROUTE.md) and [quality rubric](ART_CRITIC_REVIEW.md) guide comparisons. The inventory below distinguishes finished-slice requirements from current clip support; it does not expand the game into the traversal, facial or vehicle systems present in other references.

## Generate and review

Select references by actor and action using the [corrected Mordhau catalogue](MordhauAnimationAtlas/README.md): neutral initiation, preceding parry side, riposte origin/family and manipulation are separate fields. The tutorial's high horizontal entry includes a parry; do not copy it as a neutral load. Six riposte directions are documented, while neutral overhead/underhand examples remain unverified in that tutorial.

```powershell
python Tools/AnimationLab.py new right_horizontal_batch01 --adapter legacy
python Tools/AnimationLab.py render right_horizontal_batch01
```
The explicit legacy adapter in this historical example snapshots the TP generator/helper, character foundation and canonical reference data into ArtSource/AnimationLab/right_horizontal_batch01/source. It creates a control plus deeper-load, rounder-sweep and longer-carry variations. These are named starting hypotheses, not automatically good animation or a claim of complete-library support. Edit each draft's pose-controls.json before rendering to author more distinct approaches. Default is four; --count 3 makes a smaller batch.

Open ArtSource/AnimationLab/right_horizontal_batch01/index.html. Play all from the start at 1x. One camera is fixed per batch; --camera Defender may be chosen on its first render. Resolution is 512×416, 30 fps from every second 60 Hz source frame; time is preserved. This adapter previews attack-start frame 19 through the ready return. It is specific to the current 154-frame neutral-right source; new actions need a suitable authoring adapter, not a rotated horizontal or a mandatory 154-frame production format.

The renderer runs sequentially with a shared AnimationLab lock, no C++ build/import, and no permanent per-frame matrix. It keeps one temporary raster, editable source, compact receipts and preview per candidate. Existing previews are reused only with matching inputs/camera. Do not edit snapshot author code/data after creation; create a new batch for such changes. A stale lock after an interrupted process needs owner inspection before removal, not automatic process killing.

## Select and refine

Wrist/arm finding,9 September: Daniel rejected K's hand orientations despite its small palm/forearm direction error. Judge both complete closed grips and the arms that carry their rotation. Do not use endpoint-equivalent unwrapped turns as fractional forearm twist: they can leave different ready skin orientations. Projected transverse-normal pronation fixed that specific winding failure in an isolated experiment, but its hand-derived elbow plane and digit transfer remained unacceptable. Do not promote that solver or the EX finger pose as a proven TP fix. The current checkpoint and critic own the observed limitations; change to coauthored bilateral arm/grasp motion after these failed passes.

```powershell
python Tools/AnimationLab.py select right_horizontal_batch01 B_deeper_load --reason "Stronger visible load with a coherent carry" --observation frames
python Tools/AnimationLab.py refine right_horizontal_batch01 E_refine_load --reason "Keep the load; soften the release opening"
# Edit the new candidate's pose-controls.json, then:
python Tools/AnimationLab.py render right_horizontal_batch01 --candidate E_refine_load
```
The selection reason above is an example, not a preselected winner. Use observation frames unless continuous playback was actually reviewed; user_feedback records an existing user decision. Selection always remains provisional and does not write runtime selectors or claim human acceptance. A refinement copies only the selected score into a new take. Select the refined take after review.

Rank whole intent, load/delivery contrast, curved hilt/blade travel, coordinated body/arms and recovery. Do not choose by smallest elbow error. After two weak refinements, generate a different batch or change the relevant authoring controls. Limit secondary views and dense inspection to a specific disputed interval.

## Integrate the winner
The candidate's editable TP_v001_RightHorizontal.blend is inside source/Candidates/<id>/TP_v001. Export it with the existing tool's explicit --source and --out arguments, keeping the current production selection intact until the integration owner deliberately selects the winner. Import through the existing native TP route; read its current arguments instead of hardcoding a stale package name.

Check changed scale/phase/contact behavior and the affected engine view, then use Tools/PlayBenchmark.ps1 -ThirdPerson for an actual playable decision. The launcher records selection/module/tuning identity. Basic source fidelity is already proven; do not repeat a full sweep for every candidate. Significant TP/canonical disagreement remains a gameplay decision.

Preserve EX_v002 FP/source/projection and one authoritative C++ transaction. Review hit/miss/parry/riposte/interruption, legal input response, controlled aim/footwork, camera/reactions/audio together. Accels/drags remain input recipes at unchanged clip speed.

Daniel clarified on 9 September 2026: first-person animation serves attacker feel; third-person animation must look convincing and communicate the attack clearly to the viewer. Arm poses and extension need not match between perspectives. The shared authoritative sword path governs the attack, not resemblance between the arms. Author TP body motion for that readable path. For the current neutral right-horizontal revision, bring the sword closer to the shoulder, use a subtle moving apex reversal, and retain elbow bend longer so opening develops through delivery. The latest direction also requires visceral power/style: stage body compression, hip/shoulder sequencing, committed delivery and absorbed carry with clear speed contrast, avoiding a rigid torso simply presenting the blade path. Daniel subsequently liked the body drive and asked for the load to ease slightly into the apex, a more upright torso beneath crossing hands, and heavy arm-led delivery with restrained wrist articulation. Preserve hip/chest drive and delayed elbow opening; avoid independent grip revolutions or extreme cant that make the hands appear to power the blade. Latest support-arm refinement should reduce the high, reaching upper-arm silhouette and fold into carry, guided by the catalogued lateral motion; a connected support hand still follows the shared hilt. Riposte animations, including the wristy-twisty RH-A/RH-D atlas examples, are excluded from this neutral-motion reference match. Use the selected ordinary lateral examples in Docs/ThirdPersonReference20260908 with their weapon/input limitations. Obtain animation-critic feedback; the current checkpoint records the requested iteration count and delivery scope.

## Expand and hand off
Once one exchange works, generate candidates for opposite horizontal and overhead, select/refine those, then expand the vocabulary. Separate choreography/clip metadata from rig solving, preview generation, export and combat binding. Add a new adapter only when an action requires it; do not rewrite the functioning combat pipeline.

Keep one candidate checkpoint: policy; reference/assumptions; batch/winner; reason; human decision if any; changed contract check; next issue. Preserve source and unique approved evidence. Record batch latency and rework rather than test counts. If two coherent batches expose a persistent animation-specialist gap, use [the scoped brief](ANIMATION_SPECIALIST_BRIEF.md) without automatically commissioning anyone.

## Finished-slice movement inventory

Audited 8 September 2026 against PROJECT_SPEC, current FP/TP checkpoints, movement source and Notion [Game Structure](https://app.notion.com/p/3d32e3c3f8f88147bcaeffd4e1764989), [Swing Model](https://app.notion.com/p/3d32e3c3f8f881028f05c2a960248ff1), [Defense](https://app.notion.com/p/3d32e3c3f8f881149047ee9c11b8ea7a), [Movement](https://app.notion.com/p/3d32e3c3f8f88121bb01f4d381024731). Product loop: choose a practice pattern, approach/space, read an attack, strike or defend/manipulate, understand hit/miss/parry/interruption, recover/repeat, reset when downed. Current scope has six strike origins and stab; prove the right exchange first, then expand. A timed aimed parry is not an indefinite held block. Chamber semantics follow legal timing/direction rather than requiring a literal blade collision. Do not invent shields, vehicles, gliders, facial dialogue or RPG interaction animations from the reference set.

**Shared contract for every row:** Unreal 5.8 on mid-tier PCs, user target **100–144 FPS**; exact minimum CPU/GPU/RAM remain unspecified. Near combat is reviewed in the actual first-person/defender camera at source speed and target resolution, normally with one cheap draft camera beforehand. Each movement consumes authoritative simulation state and actual world velocity; no root-motion capsule ownership, animation-notify damage or playback-rate manipulation. FP and TP may exaggerate/differ but must communicate compatible phase, direction, reach and contact. Materials must survive pose/light change. Controller feedback is optional pending supported input devices; any future haptic is cosmetic, cancellable and mirrors an authoritative event. No category currently earns a controller-support claim.

Budget classes (allocation proposals, **not measured**): **A** critical hands/weapon/near combat pose sampled for every displayed frame from the shared clock; no distance throttle for an immediate threat. **L** near-body locomotion target 60 pose updates/s with interpolation if it proves visually equivalent; otherwise full render rate; distant non-threatening bodies may be tested at 30. **S** secondary cloth/gear target 30–60 cosmetic updates/s with interpolation; can fall back to authored bones. **E** event reactions trigger immediately from resolution, with short effect/audio budgets. Total initial animation/IK/secondary CPU allocation is at most 1ms for two nearby combatants plus FP presentation, to be measured inside the total game-thread budget; this is not a guaranteed cost. No sampling reduction changes attack time, collision, input or reaction event identity.

| ID / category and gameplay purpose | Required rig/assets; authored + procedural layers | Important states/transitions and contacts | Synchronized systems; target/read at gameplay distance; budget |
|---|---|---|---|
| M1 Ready/idle: recognizable armed readiness | Existing CF/EX/TP rig family; ready poses and restrained breathing; camera aim applied from input | Spawn/reset → ready → action; both grips, blade/guard and stance remain connected | Breathing/gear quiet; no misleading attack movement. Recognize threat orientation without face animation. A for hands, L body; current ready evidence partial |
| M2 Directional walk/strafe/backpedal, starts/stops/reversals: communicates actual velocity | Full-body lower-body cycles, start/stop/redirect poses; blend from local velocity, acceleration and braking signals; foot contacts | Idle ↔ forward/lateral/backward/diagonal; hard reverse; foot planting and swing clearance | Footsteps at planted contacts, surface audio; small optional camera response. Feet do not skate or hop on velocity changes. L; current locomotion artistry NE |
| M3 Sprint and crouch: distinguish mobility/height/commitment | Gait clips and transitions, crouched stance, pelvis/spine control; procedural gait gates from C++ | Sprint legal only under movement contract; entering combat lowers speed; crouch ↔ stand, blocked stand, sprint → walk/stop | Camera height follows actual capsule/stance; gear/step cadence matches gait; no cosmetic delay on input. L/A upper body; full transitions NE |
| M4 Turning and aim/footwork manipulation: direction and deception | Turn/step pivots, torso/head/shoulder aim ranges; coauthored weapon performance plus current view/world transform | Stationary turn, moving arc, up/down aim, accel/drag recipes through windup/release/recovery; planted feet and connected hands | Camera/input remain responsive; avoid excessive body twist or camera-obscuring arms. Preserve source speed. A/L; clips alone cannot prove manipulation system |
| M5 Jump, fall, land and terrain response: grounded weight | Takeoff/air/landing poses; pelvis/leg IK and limited foot orientation only where required by terrain | Ground → jump/fall → land; step/slope ascent/descent; feet/floor and capsule support | Landing audio/VFX on real contact; restrained camera impulse, optional haptic; no delay of capsule/input for landing animation. L/E; not reviewed |
| M6 Six strike origins + stab: load, threat direction, delivery and carry | Per-family authored body/hands/weapon clips, FP/TP bindings, source blade track, explicit phase metadata | Ready → windup → release → carry/recovery → ready; right, left, overhead/underhand directions and thrust remain distinct | Air at committed release; hit only on resolved contact; poses give clear intent and power. A/E; approved EX right source preserved, other finished authored families unproven |
| M7 Parry, chamber, riposte: communicates defense and answer | Guard entry/expiry/return, defensive contact response, riposte variants; matching attack chamber window consumed from C++ | Early/late/missed parry, valid contact, riposte window open/expire/commit, chamber outcome; both grips and defensible facing | Distinct compact contact sound/spark, brief UI confirmation and legal opportunity cue; feedback never implies a held shield. A/E; branch artistry partly provisional |
| M8 Feint/morph/combo/interruption transitions: readable deception without locks | Branch/return and compatible transition poses; shared state-driven blending, source phase bindings | Legal feint may defend before cosmetic return; morph changes family; combo alternates/slower windup and no chamber; riposte flinch exception preserved | No committed-air cue on canceled windup; audio/VFX cancel/continue per actual rule. No duplicate event. A/E; full branch library remains required |
| M9 Hit, miss, wall contact, flinch, downed/reset: clear consequence | Authored upper-body/full-body response poses and controlled downed state; optional limited physics after gameplay resolution | Once-per-target contact; hit vs miss vs wall; ordinary attack canceled by flinch; downed → explicit reset. Body/weapon wall contacts visually plausible | Contact-position audio/spark, distinguish danger and outcome, camera response bounded and optional haptic. A/E; ragdoll optional, not established. Downed appearance NE |
| M10 Cloth, mail, straps, armor and weapon secondary motion: connected weight and material identity | Rigid armor bound to suitable bones; deforming padding/mail; a few cloth/strap controls or optional cloth sim | Lames slide/read as connected through shoulder, elbow, hip and knee travel; cloth settles after carry, no grip occlusion | Gear rustle follows movement intensity; no clipping through face/hands; shade/reflection follows real pose. S; full armored deformation not evaluated |
| M11 Contact/environment VFX and shader motion: clarify force and place | Small spark/dust/air effects; controlled mesh ribbons only where approved; simple environmental water/cloth if present | Start/end at relevant events; no always-on sword trail; calm environment ↔ combat priority | Effects, lighting impulse if used, audio and UI share event identity. Effect fades do not obscure next threat. E/S; no need for moving lights as default |
| M12 Training/menu/reset state: coherent transition between play and configuration | Ready/downed reset pose; UI transitions; no new interaction rig required | Open/close settings or choose actual training pattern; resume restores correct combat/input state | UI sound/focus/input lock has one owner; no buffered accidental strike; clear return state. E; F4 is currently developer tooling, not full player menu |

### Clip requirements versus runtime-system requirements

The approved EX source has its own 154-frame/60Hz sampling and exact revision; keep its format intact. New actions use suitable native timing, not a forced 154-frame template. Each selected clip package must retain editable source, rig/skeleton identity, action/perspective, duration/sample rate, phase markers, hand/weapon controls, blend entry/exit intent, contact markers for cosmetic use, export axes/units and an unretimed preview. Existing importers/selectors own actual package formats; do not create a second parser or rename working assets simply to satisfy a naming example.

The complete runtime system additionally requires direction/gait selection, start/stop blending, phase-authoritative action selection, branch interruption, upper/lower-body composition, aim application, actual floor support, event routing, visibility/LOD, and reset/load lifecycle. A finished right-cut clip does not establish these systems or a locomotion library. Maintain one attack clock; sample both views from it and retain once-per-target contact. Verify authored deformation survives existing exports. Imported skeleton node counts may include root/eyes beyond the source rig; compare actual manifests rather than declaring a raw bone-number mismatch.

Prefer the smallest lower-body blend and foot-placement solution that fixes a visible problem; no new Control Rig/IK compensation stack without a demonstrated bottleneck. Use ground-contact markers and velocity signals for stride/steps. Secondary physics never changes the authoritative capsule or blade. Deliberate stretch is allowed if it preserves connected-looking motion and useful threat. Review isolated plate/cloth collisions only after the whole action is convincing.

### Event synchronization and review evidence

Attack serial + event kind + resolved contact identity should deduplicate presentation events. At the selected integration, verify release/air onset, contact/impact sound, spark, body response, health/UI and any camera/haptic change in the same recording. Proposed target: visible response on the first available rendered frame following the resolved event, without an extra animation wait; sound onset aligned within the capture's timing resolution. Do not claim a sub-frame latency from a 30/60fps recording. Cosmetic footsteps use planted contacts; damage never does. A miss has air passage and carry, with no fabricated impact. Lighting impulses are optional and must not swamp steel highlights.

Actual current audio route must be inspected before selecting a bank: the PrecisionSteel_v5 master bank is a source/audition asset, not proof it is the loaded gameplay bank. Its instructions differ from older tail-damping policy. Confirm the chosen event/mix policy in one actual exchange and document it explicitly; avoid stacking both old and new cue routing. Audio has not been independently auditioned in this visual audit.

Review set after selected integration: ready → parry → right riposte → carry → ready; deliberate miss; interruption; moving aim; then M2–M5 in a short movement sequence. Use native gameplay distance, sun/shade where materially relevant, and source speed. Dense multi-opponent pressure is deferred until the approved gameplay supports it, but stays a coverage gap for any broader readiness claim. Existing proof matrices remain historical evidence; this inventory does not reinstate them as routine gates.
