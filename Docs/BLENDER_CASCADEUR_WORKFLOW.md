# Blender–Cascadeur performance workflow

12 September 2026. Policy MCL-DEV-2026-09-08. Daniel authorized implementation of this workflow after selecting **playable fit** for the first proof. This supplements [the animation pipeline](ANIMATION_PROTOTYPE_PIPELINE.md); [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns actual source, candidate, integration and human decisions. This document is a production method, not evidence that the animations have been made or accepted.

## Ownership and protected contract

- Blender owns KN_v002 mesh, skinning and rest skeleton; armor stays separate. Cascadeur owns editable choreography until the explicit finishing handoff. The final Blender take then owns finishing edits. Retain both native files and the transfer artifact; there is no assumed two-way control synchronization.
- Preserve EX_v002 source/native benchmark, positively reviewed FP feel, legal inputs, current timing and canonical contact. Author against the current source-clock-compatible damaging guide; apply the 500 ms runtime release mapping once. Label source-speed and gameplay-clock previews separately.
- Reuse the existing Cascadeur session/operation mechanisms selectively. The historical Citadel kit and CSV playback route are not KN_v002 integration. Do not execute the old kit against new selections.
- One owner controls each writable app session. Save unique takes; never regenerate a polished take from its initial blocking recipe. Use the existing explicit native Unreal route only after source selection.

## One-time KN transfer proof

Create an isolated KN import kit retaining deform bones, finger/twist channels, rest transforms and explicit sword/grasp calibration. Establish standard Cascadeur body controls and connected two-hand weapon controls without replacing the mesh or skinning. The primary grasp owns the sword; the support grasp follows its hilt placement while body, clavicles and elbows remain editable.

Check live Cascadeur access and export entitlement before authoring. Prove one save/export/Blender return and one deliberate body/hand revision. Check hierarchy, rest pose, units/axes, frame origin/FPS, both grips and bone motion. A Blender-only reimport proves the Blender FBX route, not Cascadeur rigging or control fidelity. Stop at a demonstrated transfer defect before multiplying candidates.

Use binary FBX, preserve Model Pose and disable Automatic Bone Orientation on Blender import. Keep editable Cascadeur controls in `.casc`; transferred baked animation is downstream evidence. [Official Blender transfer guidance](https://cascadeur.com/help/category/300).

## Choreography before finishing

Use the corrected neutral yellow-mask Mordhau reference, with uncertainties from [the reference catalogue](MordhauAnimationAtlas/README.md). **13 September clarification: Mordhau governs the choreography; baseball/golf was only Daniel's descriptive analogy.** Follow observed Mordhau pose ordering, opening/gathering, hand route and rhythm wherever a sports analogy differs. Hands and sword travel together through the load; do not impose a separate sports backswing or inherit rejected arm/weapon staging as protected choreography.

Block three complete actions from ready through recovery:

| Candidate | Whole-body hypothesis |
|---|---|
| Rotational | Pelvis/chest counterturn, delayed arm opening, coordinated rotational carry |
| Grounded | Leg compression, weight transfer, supported drive and absorbed recovery |
| Gathering | Compact continuous pullback, clear lateral launch, longer coordinated carry |

Each must communicate gathering load, coil, delivery, passage, absorption and return. Establish foot support and pelvis intent, coauthor body/both hands/weapon at key poses, then add route-defining breakdowns. Deliberately stagger acceleration and braking through pelvis, chest, shoulders and hands. Foot pivots and weight transfer are cosmetic; actor displacement remains gameplay-owned. Do not add synchronized knee bobbing to an unchanged arm-only swing and call it full-body coordination.

Use ordinary interpolation for the two-handed attack. AutoPosing assists whole-body poses; it does not decide choreography. AI Inbetweening is not the default for this proof because its documentation lists prop-action and relative-controller limitations. [AutoPosing](https://cascadeur.com/help/tools/animation_tools/autoposing), [two-handed setup](https://cascadeur.com/tutor/workingwithweapons), [Inbetweening limitations](https://cascadeur.com/help/category/278).

Compare three cheap whole-action previews from one fixed defender camera. Select one provisional winner. Add a side/grip view only for a concrete ambiguity. Refine readability, body coordination, acceleration contrast and continuity in that order. Preserve deliberate preparation and decisive delivery; uniform smoothing is not the objective.

Use AutoPhysics only after the gesture works, comparing its proposal against the retained authored take. Test the actual two-hand constraints; retain only coordinated improvements compatible with timing/contact. Reject an assistant result that needs weapon snapping or added arm stretch to restore the contract. [AutoPhysics](https://cascadeur.com/help/tools/physics_tools/autophysics), [current point-constraint support](https://cascadeur.com/blog/view/cascadeur-2026-1-new-renderer-ue-live-link).

## Selected runtime check and Blender finishing

Before expensive polish, integrate only the selected rough take with an isolated selector. Compare native and runtime neutral/downward-aim behavior at the actual gameplay clock. Diagnose any distortion introduced by aim/contact fitting. An attractive source with incompatible contact, or exact contact with an implausible body, is not a successful proof. Surface unresolved incompatibility explicitly; do not change FP/gameplay or add a compensation stack silently.

Once choreography and rough runtime fit work, hand off to Blender. Correct shoulder deformation, forearm twist, wrist/finger seating and remaining curve defects. Inspect hilt/tip/wrist/pelvis motion paths for accidental corners, stalls and jitter; preserve attack acceleration contrast. Keep the imported base and editable finishing action separate from the baked export. Never rerun the authoring recipe over native finishing changes.

Final changed-contract verification covers damaging alignment, hit/miss, interruption/return, controlled aim/footwork and the positively reviewed FP feel. Changed C++ requires a build, affected tests and one independent review for consequential changes; source drafts do not. Follow [VALIDATION](../VALIDATION.md).

## Acceptance and efficiency

The visible target is supported full-body launch and absorption, continuous coordinated preparation, strong rhythm, connected grips without conspicuous telescoping, readable gaze/direction including looking down, and a performance that survives runtime composition.

Continuous human playback reviews the promising rough performance and final playable result. Sampled frames establish narrower pose/path findings and cannot certify fluidity or human acceptance. An agent's provisional choice permits refinement, not an acceptance claim.

One owner carries the selected take through refinement; reuse one critic when needed. After two refinement passes without convincing gain, change choreography or a demonstrated control limitation. After two coherent unsuccessful batches, prepare the existing specialist brief and editable assets; do not commission automatically. Serialize expensive work. Record setup time, first reviewable result, revision effort, transfer cleanup and actual human outcome in the existing checkpoint. Do not extrapolate old Citadel technical-cycle times into KN production savings.

No vocabulary, parry/riposte, armor or environment expansion is part of this proof.
