# Fresh Cascadeur right-horizontal production prompt

13 September 2026. Directed execution prompt; policy MCL-DEV-2026-09-08. Daniel has chosen fresh third-person choreography on the new AccuRig body. This prompt does not claim that a new performance has already been produced.

---

Create an excellent, convincing **neutral third-person right-horizontal two-handed sword attack**, authored fresh in Cascadeur for MeleeCombatLab. Mordhau is the performance benchmark: unmistakable preparation, powerful hand-led delivery, supported whole-body motion, controlled momentum and readable threat. Deliver an editable performance and a reviewable result, not merely a rig demonstration, plan or collection of attractive poses.

Work in `D:/Projects/swingmanipulation-recovered-20260911`.

## Team and ownership

Use two specialist agents with distinct responsibilities. These are assigned working roles, not claims of real professional credentials:

1. **Senior 3D combat animator — artistic lead.** Own the reference interpretation, choreography, posing, spacing, support, rhythm and visual critique. Describe actionable whole-body poses and breakdowns. Judge the complete action at normal speed wherever playback inspection is available. Challenge weak gestures even when technical checks pass. Carry the selected performance through refinement.
2. **Cascadeur expert / technical animator — native scene owner.** Own the single writable Cascadeur session, rig/control setup, two-hand weapon relationship, native animation implementation, curve/breakdown edits, save/export and Blender return. Translate the artistic lead's direction into actual editable controls. Report limitations concretely instead of substituting automatic tool output for artistic decisions.

The coordinating agent owns scope, protected baselines, provisional selection and integration decisions. Default to sequential handoffs: artistic direction → native implementation → artistic review → focused revision. Parallelize only independent work that reduces rework. Do not let both specialists edit the same scene. Reuse these specialists through acceptance; no child agents. Give each a small self-contained assignment with owned paths, relevant evidence and acceptance criteria, using `fork_turns="none"`. Follow the project's model/effort policy, including Astra High for unresolved architecture and detailed technical planning.

Before acting, each specialist reads the canonical rules at `D:/Projects/swingmanipulation-recovered-20260911/AGENTS.md`, `Docs/DEVELOPMENT.md` and `D:/Projects/swingmanipulation-recovered-20260911/Docs/ANIMATION_PROTOTYPE_PIPELINE.md`. Include those absolute rules and pipeline paths in every delegation. Read the relevant current section of `Docs/THIRD_PERSON_CHECKPOINT.md`, then `Docs/BLENDER_CASCADEUR_WORKFLOW.md` and `VALIDATION.md` once. The newer AccuRig selection supersedes the workflow's historical KN-specific starting point.

## Starting point and protected contract

- Resolve the current body from `Config/WorkingCharacter.json`. At this prompt's creation it is `ArtSource/UserMaleBody/MB_v004_Project/Male_Body_Project.blend`, scene `Rigged body - working`, armature `MB_AccuRig`, mesh `MB_Rigged_LOD0`. Native skeleton: 118 bones; the existing Unreal import adds an armature-object root. Preserve the mesh, weights, rest skeleton, LODs and original sources. Add authoring controls separately. Do not rebuild the character or reuse the KN kit as its rig.
- Begin with clean choreography on this body. Do not retarget, trace, seed from or polish the rejected KN/CF swing. Retain `MB_SwingReview_v001` and the old sources only as diagnostic evidence. The diagnostic's remaining 12.60 cm support-target reach deficit concerns that mapping/placement; it does not establish an intrinsic defect in AccuRig.
- Preserve accepted `EX_v002-source-1615b76b-FBX-6a34514c-native-unreduced-v1`, `Config/EXPreview.json`, first-person projection and the positively reviewed FP feel. Keep a reproducible baseline with actual source/config/module identity.
- C++ remains authoritative for legal inputs, attack clock, actor movement, blade contact and damage. Read current timing/configuration and the accepted weapon-motion guide before blocking. Current release duration is 500 ms; apply its source-to-runtime mapping exactly once. The existing 800 ms combo windup is preserved, but authoring combos is outside this task. Do not invent frame boundaries from these two values.
- Fresh choreography must fit the existing playable contract. Treat the damaging guide as a compatibility constraint, not an independently animated sword that hands must chase. If convincing connected body motion and authoritative reach cannot coexist, identify the exact conflicting interval and alternatives. Never silently alter gameplay or hide the conflict with compensating arm stretch.
- Keep this task to one neutral right-horizontal action, ready through complete recovery. No new parry/riposte vocabulary, other attacks, armor, environment or broad rig/solver framework.

## Reference direction and known failures

Read `Docs/MordhauAnimationAtlas/README.md` and inspect its relevant local captures. The verified neutral right-horizontal reference is the **externally visible yellow-mask opening attacker around 30.0–31.5 seconds** in the catalogued courtyard tutorial. Recovery is partly obscured; label your recovery design as interpretation. RH-A/RH-D are parry-to-riposte examples. The high pose at 156.50 seconds is not a neutral windup. Use actor-anatomical right/left, not screen direction; establish the correct right-origin horizontal action before multiplying takes.

Mordhau informs exaggeration, readable intent, force and control. Do not claim to recover its hidden rig, exact 3D trajectories or engine phase boundaries from footage. Keep neutral choreography separate from aim/footwork manipulation examples. Use current official Cascadeur documentation when a feature's behavior is uncertain; verify it in the installed application.

**Mordhau is the governing animation reference.** Daniel clarified that baseball/golf was only his attempt to describe Mordhau's motion, not an independent creative target. Where the analogy and observed Mordhau motion differ, follow Mordhau. Do not impose sports biomechanics, a mandatory low-waist backswing, or a simplified one-direction pullback that removes its observed opening and gathering. Both hands must transport the hilt and sword together through convincing preparation, delivery, passage, carry and return. Use the verified neutral reference's actual pose ordering, hand route, rhythm and body relationship; identify any interpretation required by occlusion.

Reject these recurring failures: high shrugged arm staging that reads weak; arms reaching after an independently moving sword; forward hilt shove followed by withdrawal; stationary-hilt blade rotation substituting for a swing; passive legs or synchronized decorative knee bobbing; head/torso folding unnaturally during downward aim; long telescoping arms; grip inversion; an unexplained sword stall; and a snapped or mechanically reversed recovery.

These are performance observations, not universal joint-angle rules. Powerful extension, wrist articulation, asymmetry and deliberate stylized deformation are allowed when they improve the complete result. Physical plausibility serves convincing motion; neither anatomical purity nor exaggerated movement alone establishes quality.

## Execute the work

**1. Establish a usable MB Cascadeur scene.** Check dirty state and preserve unique work. Confirm actual live access and export capability; prior connectivity is not a new rig proof. Create an isolated MB import/control setup with standard body controls, usable fingers/twist channels and editable weapon grasps. The primary right hand is guardward; the support left hand is pommelward. Calibrate them to the actual new palms and retained sword. The primary grasp owns the sword; body, shoulders, elbows and both hands remain coauthorable. Prove one native save, export, Blender return and deliberate body/hand revision. Check changed units/axes, hierarchy, rest pose, frame origin/FPS and grasp relationships. Fix a demonstrated transfer defect before creating three takes.

**2. Write one compact artistic brief and block three complete hypotheses.** Use one plain defender-distance camera, source-speed playback and the same body/weapon. Compare genuinely different strategies:

- **Rotational:** supported counterturn and coil, delayed arm opening, decisive sweep, torso braking and connected carry.
- **Grounded:** purposeful leg compression/weight transfer, supported launch and absorbed recovery.
- **Gathering:** conspicuous continuous two-hand pullback, compact preparation, curved lateral launch and economical return.

Every take includes ready → continuous load → release/passage → carry/braking → complete recovery. Establish support and pelvis intent together with hands, weapon, chest and head. Add route-defining breakdowns and intentional offsets between body regions. Do not animate the arms first and decorate them with leg motion afterward. Head and attention should remain meaningfully engaged with the opponent. Cosmetic pivots/weight shifts must not assume unimplemented actor displacement.

**3. Use Cascadeur deliberately.** The animator decides the performance. AutoPosing can assist pose construction; it does not decide choreography. Begin with ordinary interpolation and authored breakdowns for the two-handed prop action. Do not default to AI Inbetweening without verifying its relevant limitations. Consider AutoPhysics only after the gesture works, on a retained separate take, and keep its result only if it improves support/momentum without damaging grips, attack contrast or timing/contact compatibility. Do not smooth away the launch to satisfy a physics proposal.

**4. Compare complete performances and refine one winner.** Save native edits before each preview. Produce one inexpensive whole-action clip per take at its actual source speed; never normalize playback to hide differences. The artistic lead identifies each take's strongest idea and largest visible failure, then provisionally selects the best. No user approval is needed for every draft. Refine that winner for one or two focused passes, each addressing a named visible defect while preserving what won. Add a second view only to resolve a specific ambiguity. After two passes without convincing improvement, change the choreography/control premise rather than accumulating small fixes.

**5. Test the selected rough action in context before expensive polish.** Explicitly integrate only the selected source through an isolated selector, with the smallest necessary AccuRig hierarchy-aware adaptation. Existing TP code expects the older skeleton: do not bypass its checks, relabel bones or assume a mesh swap is retargeting. Compare native and runtime results at neutral and downward aim using the actual gameplay clock. Check the changed phase/reach/contact behavior, controlled aim/footwork, hit/miss and interruption/return without expanding animation vocabulary. Accels/drags must use aim and footwork at unchanged playback rate. Diagnose runtime-induced distortion separately from source choreography. Preserve default/accepted assets. Build/test only changed C++; consequential code/contact changes need one independent review.

**6. Finish in Blender after an explicit handoff.** Once the rough performance and runtime fit work, preserve the native `.casc` and transfer FBX, then retain an independent editable Blender finishing take. Correct shoulder deformation, forearm twist, finger seating, wrist continuity and remaining path/curve defects. Never regenerate over native finishing edits. Recheck only changed contracts and produce the final full-action clip plus an identified opt-in playable launch when integration is complete.

## Quality decision and deliverables

Judge readable preparation and threat, purposeful hand launch, curved blade/hilt travel, convincing support and body coordination, connected grips, acceleration contrast, controlled carry and continuous recovery. Examine intermediate motion, not just selected poses. A numeric grip score cannot excuse a weak performance; an attractive performance cannot excuse misleading damaging reach. Do not award an unobserved quality a score.

Deliver editable native sources/controls, one source-speed comparison set, the selected refined preview, a short selection rationale and the relevant integration/transfer receipt. Clearly distinguish source-speed from gameplay-clock previews. Maintain one compact entry in `Docs/THIRD_PERSON_CHECKPOINT.md` with source identity, visible change, observed evidence, remaining limitation and next useful action. Link existing records instead of duplicating them. Report continuous playback only if actually inspected; human artistic/play acceptance belongs to Daniel.

Operate the tools yourself and carry the authorized work through to a concrete reviewable result. Ask Daniel only for a material missing decision or a demonstrated blocker; do not make him operate Blender or Cascadeur. After two coherent unsuccessful batches expose a persistent specialist limitation, produce the existing one-exchange specialist handoff with assets and precise deficiencies. Do not commission outside work. Never claim Mordhau-level quality merely because exports, metrics or agent votes pass.
