> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# MEL-15 — revised next-instance handoff prompt

Revised against the Notion and Linear direction updates of **7 September 2026, 07:08–07:10 UTC**. Briefly amended against REN-01, KRONK-01 and the Notion Animation / Melee Swing Model updates through **07:51 UTC**. This revision changes the plan, not the paused implementation or its validation status. Copy the prompt below into the next instance to resume work.

---

**Expert role:** Act as a principal AAA melee-combat animator specializing in authored two-handed sword performance, first-person composition and defender readability. Apply supporting expertise in character modeling, skinning, skeletal rigging, procedural animation, physics-assisted motion generation, Unreal Engine and authoritative melee simulation.

Resume **MEL-15 — Rehaul full-body swing motion and overhead hand follow-through** in **danielpang35/melee / MeleeCombatLab**. Drive it aggressively to a compelling playable result through deliberate authoring and real build/run/render/inspect/iterate cycles. Integrate MEL-5's diagnostic/idle foundation and MEL-6's horizontal work instead of treating the old elbow repair as the whole assignment.

Workspace: `C:\Users\Daniel Pang\OneDrive\Documents\ChatGPT\swingmanipulation`
Unreal: `C:\Program Files\Epic Games\UE_5.8`

**The latest direction takes precedence over the older repair plan: preserve the successful feel, rehaul how the arms and sword communicate it.**

The user likes **the weight and feel of Astra Ultra's current swings**. Preserve that baseline's timing, acceleration character, commitment, control and responsiveness. The remaining visual failure is that the arms do not convey the swing and the sword “sprinklers” across the screen. Repair coordinated **screen-space sword and especially hilt travel**, with the body and arms visibly carrying the weapon.

Do not interpret “rehaul” as permission to replace the praised combat feel. Do not interpret praise for feel as visual acceptance. Identify and preserve the relevant reproducible checkpoint for A/B; do not invent an exact accepted module if the source record does not identify it.

**Read and reconcile these sources before editing:**

- [Notion — Animation](https://app.notion.com/p/3d32e3c3f8f881e08474defe7febb171): preserved feel, authored choreography, grip diagnosis, lower idle, physics permission and visual gates.
- [Notion — Melee Swing Model](https://app.notion.com/p/3d32e3c3f8f881028f05c2a960248ff1): authority, source-motion pipeline, full transforms, stance/direction separation and expansion limits.
- [Notion — Current Milestone](https://app.notion.com/p/3d32e3c3f8f8813c8883ed9e8bd1f299): prove one exceptional exchange before expanding coverage.
- [Notion — Visual Direction](https://app.notion.com/p/3d32e3c3f8f881dabc3be8eff5b29360) and [Task / Experiment Database](https://app.notion.com/p/3d32e3c3f8f881758692e453afcdecb4): targeted hand quality, deferred broad profiling, ownership and expert-role requirements.
- Live [MEL-5](https://linear.app/meleeslasher/issue/MEL-5/diagnose-handarm-appearance-against-mordhau-and-establish-stomach), [MEL-6](https://linear.app/meleeslasher/issue/MEL-6/rehaul-authored-procedural-horizontal-swings-for-a-controlled-playable), [MEL-15](https://linear.app/meleeslasher/issue/MEL-15/rehaul-full-body-swing-motion-and-overhead-hand-follow-through) and [MEL-11](https://linear.app/meleeslasher/issue/MEL-11/package-and-play-review-the-current-versus-revised-longsword-exchange), including newer comments and acceptance criteria.
- Local `Docs/MEL15_DIRECTION_UPDATE_20260907.md`, `Docs/MEL15_IMPLEMENTATION_FRAMEWORK.md`, `Saved/MEL15/pause-state-20260907.json`, `rig-pause-status.md`, `trajectory-pause-status.md` and `CONTACT_TRANSITION_AUDIT.md`.
- `Docs/MEL15_ANIMATION_BRIEF.md` preserves the original mission; `Docs/ANIMATION_ARCHITECTURE_AUDIT.md` preserves a historical source audit. Reuse their evidence, but apply the newer decisions where the approach or priority changed.

Linear owns execution status; Notion's B-series table is historical seed backlog, not a synchronized task database. Preserve owners/history and do not create duplicate work. At this revision MEL-5 and MEL-15 are In Progress, MEL-6 and MEL-11 Todo; MEL-5 explicitly blocks acceptance of MEL-6/MEL-15. Recheck live fields rather than treating this snapshot as permanent.

**Apply the complementary Ren / Kronk reference findings.**

Read `Docs/REN_MORDHAU_REFERENCE_REPORT.md` ([REN-01](https://app.notion.com/p/3d42e3c3f8f88199b54eed401936acac)) and `Docs/KRONK_MORDHAU_REFERENCE_REPORT.md` ([KRONK-01](https://app.notion.com/p/3d42e3c3f8f881d8b2e7d845679e8eb7)). Ren guides economical, purposeful coordination; Kronk tests whether it survives creative attack lines, tight spacing and successive threats. Economy removes compulsory wasted motion without limiting deliberate player expression. Preserve the liked weight; larger hand or torso excursions are not a quality goal.

Capture the same attack with fixed view/feet, aim-only variation, movement-only variation, then combined legal inputs. Compare hilt/guard orientation and arm coupling against environment landmarks and target spacing. Do not bake montage camera routes into base attacks or claim simple background subtraction recovers pure animation. Exact inputs, phases and hidden body amplitudes remain uncertain. Use Kronk K14-01/K14-03 for paired sword anatomy; other weapons supply transferable principles, and contact/defensive frames are not automatically attack release.

Once coordination works, reduce hilt, shoulder and pelvis/chest excursions one at a time while preserving phase relationships, grips and clocks. Compare normal-speed FP/external results: retained weight, arms explaining the swing, and unnecessary motion. Keep the least motion that remains convincing. Stress-test adjacent angles, near/far spacing, elevated/depressed aim and consecutive direction changes; inspect useful threat visibility returning after recovery and coherent contact consequences. Review multiple threats only where existing tooling supports it. These are review refinements, not added production scope, evidence for looser turn limits, or a reason to accelerate 240-control expansion.

**First establish what is runnable, without repeating the old investigation.**

The dirty checkout contains substantial useful work. Preserve it, the imported assets and all historical evidence. Do not reset to HEAD. The last successfully built/rendered module is **1006**, still selected in `Binaries/Win64/UnrealEditor.modules` when this prompt was revised. Newer source contains transported BodyMotion arm preferences and asymmetric high-guard elevation intended for **1007**, but it is unrendered.

Two immediate blockers remain:

1. Fix the test-only type-deduction error near `Tests/PresentationTests.cpp:176`: `for(const auto* state:{&after,&epsilon})` mixes const/non-const pointers. An explicit `std::array<const Combatant*,2>` resolves that ambiguity. Then run the current suite; its latest attempted run never executed tests.
2. Both 1007 Unreal builds failed with MSVC C3859/C1076 and Windows1455 because paging-file/commit capacity was exhausted. Read `Saved/MEL15/build-iteration6.log` and `build-iteration6-retry.log`. Run builds and Unreal captures serially; inspect current resources, and clean up only processes demonstrably owned by this work. Do not terminate historical PIDs, close unrelated apps or change Windows paging settings without authorization. This concrete development blocker justifies focused resource investigation; it does not reopen broad performance profiling.

The **931,330 swing / 2,363,350 presentation / 605 combat** passes validate the earlier frozen loaded-X26 core, not the newer combined source. The **56/56 engine tour and 4/4 automation** passes are module 1005 evidence. The additional pitched-reach diagnostic failed to link because its runner omitted AttackStateMachine; no pitched-envelope result exists.

Record source/config/asset/DLL identity, preserve a repeatable current/revised switch or fixture, and verify the actual loaded module. Treat recovering a build as preparation for the new animation work, not completion.

**Foundation gate: Mordhau diagnosis and lower idle, owned by MEL-5.**

Reference: `D:\Mordhau Montage VI.mp4`. Its existence was verified during prompt revision. Earlier work inspected samples around **2:44–2:45.875**; use them as a starting point, not sufficient reference coverage or proof of hidden 3D detail.

Before moving grip transforms, make a matched, timestamped reference/current diagnostic sheet and normal-speed comparison. Inspect:

- Hand order, guard/pommel relationships, spacing, palm/thumb orientation, finger wrap and wrist alignment.
- Arm/shoulder placement and the complete silhouette.
- Hand/glove shape, topology and skinning.
- Neutral-material versus final textured/material rendering.
- Hilt translation, full blade orientation, hand travel and camera-relative composition through load, passage, follow-through and return.

**Actual grip contacts may already be correct.** Awkward arms and poor hand modeling or shading can make them look wrong. Separate these hypotheses and record which evidence supports each. Preserve correct contacts and corrected chirality; change offsets only when reference evidence supports that change. Repair or replace deficient hand assets when needed. Do not protect poor model/material quality merely because an earlier import or IK check passed.

Isolate camera motion when comparing Mordhau and the project. Account for camera/FOV, weapon proportions, occlusion and perspective. Hidden thumb/finger details and inferred 3D offsets remain uncertain; do not invent calibration from a single 2D frame.

**Firm idle requirement:** hands/hilt rest closer to the stomach/upper abdomen, with relaxed arms and torso clearance. Author continuous idle→load, idle→parry and recovery→idle in both first-person and external views. This is not a global downward offset: raised preparations and defensive poses remain where the action needs them.

Deliver the diagnosed cause, annotated reference/current sheets, neutral/final-material close-ups, idle front/side/FP views and continuous transition footage. This foundation must support dependent swing acceptance. If existing work in MEL-5 has already met the gate, integrate its evidence rather than duplicating it; otherwise complete the necessary foundation within the coordinated work.

**Author one exceptional exchange, not a larger parameter sweep.**

MEL-6 owns both horizontal origins; MEL-15 owns full-body integration and one convincing overhead with real hand follow-through. Begin from the fitted lower idle and diagnosed hand appearance. Preserve both diagonal regression cases and exact90° evidence where they reveal boundary/pose failures, but do not expand into all remaining families before this slice works. MEL-13 owns broader family expansion after acceptance; MEL-11 owns integrated playable acceptance.

Author deliberate **load → launch → target passage → follow-through → return or transfer** poses and phase curves against the actual skeleton. Give grounded foot pressure/pivot, pelvis, chest, shoulders, elbows and hands independently timed contributions. A mandatory automatic step, lunge or root-motion delay is not required to convey weight. Make the kinetic chain visible.

Store full calibrated weapon/hand transforms, including **roll and palm offsets**. The pipeline should support authored or baked source-motion data, compatible procedural adaptation and final constrained IK. C++ simulation samples the authoritative weapon curve; rendering and collision use the same final blade geometry.

Use the existing analytical grip solver, fixed clavicle fit, rig improvements and transported contact preferences where they support the performance. They are useful infrastructure, **not a mandate to retain every curve, rail or key**. The existing X26 load, X31 passage, post-target X≈39 and X≈33 diagonal finish are historical candidate values, not acceptance targets. Reauthor them if the lower idle, Mordhau comparison or better choreography requires it while preserving feel and checking gameplay effects.

For an unobstructed neutral-pitch overhead miss, both hands and the hilt travel forward/down through the target into a fitted finish below the sternum toward the upper abdomen/waist **before guard return**. A low blade tip with high hands fails. Contact may justify a higher finish. Judge the hand path relative to the torso and world/weapon clearance.

The “sprinkler” defect is a specific rejection criterion: a large blade arc about a nearly stationary-looking hilt fails even if endpoints and grip errors are perfect. Compare coordinated hilt/blade travel in screen space and body space. First-person and defender body posing may be composed separately around the same authoritative blade; do not blindly restore old FP shoulder hacks or create a second cosmetic damage path.

Prioritize **power, readability, artistic control, believable choreography and production efficiency over literal physical realism**. Use purposeful contrast within believable joints; exaggeration is permitted where useful, without enlarging every hand arc, torso turn or recovery. Do not weaken a compelling cut solely to satisfy an unsupported anatomical proxy threshold.

**Physics is permitted where it earns its cost.**

Use advanced simulation for source-motion generation, offline baking or runtime motion when it improves the final animation or saves authoring, iteration, memory or runtime resources. It is not restricted to secondary effects. Compare the relevant quality/resource benefit with a simpler approach; bake useful results where appropriate. A narrow comparison supporting that choice is allowed. Broad profiling/benchmarking remains deferred until playable exchange review unless a real slowdown blocks development.

If physics modifies the sword, its final transform must pass through the same authoritative collision path. Presentation-only simulation must not detach the visible blade from gameplay geometry, change legal input timing or add notify-driven damage. Physical accuracy itself is not the acceptance test.

**Preserve accepted feel and disclose geometry effects.**

Start the A/B with strike clocks **.575/.500/.675s** and combo windup **.700s**, keeping the praised acceleration/commitment/response. Do not casually retime the cut to make posing easier. Any necessary later timing change needs a separate explicit comparison; authoritative path changes must retain the liked feel and be checked for reach/contact timing.

Earlier post-target authoring changed the swept volume: in 2,430 fixtures, **8 gained and 3 lost hits**, plus 115 common-hit timing shifts from −16.67 to +20.83 ms. Loaded X26 advanced 54 further contacts by 4.17 or 8.33 ms without changing hit/miss outcomes in that grid. Sampled upright maximum forward extent remained 158.445977933 cm. That is not a full pitched/off-axis envelope proof. Preserve the exact fixtures in `Saved/MEL15/ReachContactReview`; rerun them after consequential path changes and report what changed. These old results are neither a promise of unchanged balance nor mandatory outcomes for every future rehaul.

Keep deterministic swept contact, once-per-target hits, turn limits, legal feint/morph/parry/chamber/combo/riposte behavior, movement, crouch, hip-pivot lean and frame-rate independence. Accels/drags change spatial contact, not attack clocks.

Select stance/handedness separately from attack angle, latch the action at input and blend only compatible samples with continuous full orientation. Define vertical-cut combo side changes explicitly. Preserve the rules that combos alternate body side, wind up slower than ordinary attacks and cannot chamber. The historical architecture audit's directional jumps and ~13cm neighboring corrections are not fresh live measurements; reproduce relevant boundaries before claiming them fixed.

**Use the tiered visual gate on every meaningful change.**

1. Cheap geometry/continuity/contact checks first.
2. Matched first-person and opponent renders for every meaningful pose or trajectory change, then front/side/rear3q/defender views as needed.
3. Inspect actual modeled/textured surfaces, reference-matched key poses and continuous normal-speed motion; slow motion and traces diagnose the failure.
4. Identify the worst visible defect, correct the coupled cause, rebuild and repeat.

Do not accumulate many unrendered pose/trajectory edits because millions of checks passed. Do not repeat the old failed wrist-orientation fixed-point loops or universal elbow-rail/gate sweeps without a new supported hypothesis. Current contact transport removed large sampled elbow discontinuities; preserve that continuity property even if the implementation changes.

Validate miss carry, body resistance, parry redirection, wall rebound, combo transfer and riposte conversion, with recipient response and synchronized feedback. Coordinate with existing feedback/audio owners rather than opening an unrelated audio rewrite. Include moving range-edge approach/withdrawal/reversal, accels/drags, crouch and extreme aim.

Current harness limitations are explicit remaining work: nominal `Age-ReviewLeadIn` can differ from actual attack age by one 30 Hz frame; fixed ordinary-strike pose-sheet timestamps do not label contact/combo/riposte/stab phases correctly; continuous legal combo/riposte capture still needs a fixture. Body/parry outcome capture setup needs engine verification. Use actual phase/contact telemetry. Do not use current `Build.ps1 -Automation` unchanged—it appends `;Quit`; use queue-empty automation from the framework or repair the helper.

Run final native and engine regressions on one identified final combined build. Broad dedicated performance profiling is not an acceptance gate. Only after the exchange is compelling should you prove interpolation across the overhead fan and consider 240 selections from roughly 6–8 cut anchors and 1–2 stab variants per grip style. If quality fails, add anchors or keep 6–8 bespoke directions with spatial manipulation. Do not expand input merely because angular interpolation is mathematically available.

**Acceptance and delivery are concrete.**

Preserve the user's accepted brief FP weapon exit during low follow-through; do not ask again or keep hands high to avoid it. Preserve the newly clarified successful swing feel. Neither preference accepts the remaining visual animation.

Provide a reproducible playable current/revised comparison at matched conditions, not only an edited montage. Include both horizontals and one overhead, reference annotations, pose/model/material diagnosis, stomach-level idle transitions, normal-speed FP/opponent clips, useful slow motion/other views, exact build/assets/config, collision/reach/contact results and remaining defects. Baseline external captures use the **legacy** camera; baseline upper cuts are60°/120°, not90°. Preserve old footage as historical.

The prior session could inspect PNGs and encode/decode video but did not establish continuous video perception. Be precise about what you observed. Human playable review must confirm that the arms/hilt now convey power and readable commitment **while retaining the weight and responsiveness already liked**. Record the decision against the exact build. Numerical tests and a successful import cannot close MEL-15 or MEL-11.

Update the relevant Linear issues with evidence and result/decision; update affected Notion bible entries for consequential design changes. Preserve task ownership and begin any new task/experiment description with its specific Expert role. Do not silently turn future direction expansion or broad art/performance work into this task.

Continue the authorized implementation autonomously after this prompt is used to resume. Do not stop at advice, one code change or a merely less-broken pose. Complete the diagnostic foundation, authored exchange and evidence before requesting final human acceptance.

