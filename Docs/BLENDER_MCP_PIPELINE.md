# Blender-assisted animation pipeline reassessment

> **Dated record; active assignments and status superseded (12 September 2026).** Preserve the technical/design history below. [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns current source, selection, pilot outcome and resume; [DEVELOPMENT](DEVELOPMENT.md) owns operational scope. Step 4 (parry/riposte, branch integration, full-exchange packaging and expansion) is deferred. [Documentation ownership](DOCUMENTATION_OWNERSHIP.md) and [audit](DOCUMENTATION_AUDIT.md) define current authority. Linear owns live execution.

Current procedure: [Animation creation and ideation pipeline](ANIMATION_PROTOTYPE_PIPELINE.md). Direct MCP add-on and scene-inspection calls succeeded on 9 September 2026; the unavailable-namespace statement below describes the earlier assessment. Interactive editing benefit remains unmeasured. Historical carry-problem status below is superseded by the TP checkpoint.

9 September 2026. Policy MCL-DEV-2026-09-08. Planning and read-only capability assessment; no new animation or quality acceptance. This supplements [the architecture plan](MORDHAU_ANIMATION_ARCHITECTURE_PLAN.md). [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns moving source evidence; Linear owns execution.

## Recommendation

Use Blender MCP as an optional interactive route into the existing editable Blender authoring pipeline. Keep native control curves as source, AnimationLab as the isolated batch/preview manager, and native Unreal/C++ as the selected delivery route. The expected benefit is a shorter inspect → pose/curve edit → evaluate loop, not automatic choreography or a replacement animation engine.

Blender is already central: MEL-37 has independent native curves, editable grasp/wrist controls, primary-attached sword and derived weapon samples. Its current 97-frame proof remains incomplete: carry reversals at frames 52/57/61 and 37.6 mm support separation at frame 64. Tooling checks passed; the complete motion did not. MEL-38 stays downstream.

## Verified tool boundary

The local configuration invokes uvx blender-mcp. A read-only add-on handshake at localhost:9876 succeeded: Blender 5.2.1 LTS, add-on 1.6, protocol 5; scene/object inspection, viewport screenshots and code execution are advertised. Blender MCP is not exposed as a callable tool namespace in this task; the handshake used the local add-on protocol. No edit, screenshot, save/reopen or end-to-end MCP client workflow was exercised. Record and pin the tested server/add-on/Blender versions during the experiment; current uvx configuration is unpinned.

The upstream [Blender MCP project](https://github.com/ahujasid/blender-mcp) exposes scene inspection and Python execution. Animation-specific operations should call the existing repository authoring functions through Blender Python; dedicated animation tools are not assumed. Keep one session owner and verify the open document before writes, especially while separate character art work exists. Work only in a diagnostic copy; do not open over unsaved work. Heavy previews continue through the serialized existing route.

## Proposed working loop

Reference packet and saved defender camera → native Blender controls and curves → interactive MCP inspection/edits where available → saved isolated source and scripted cheap full preview → compare three complete hypotheses → select/refine → demonstrated deformation → explicit FP/TP/contact binding → native Unreal exchange.

Use interactive operations for focused posing, evaluated grip/rotation inspection and small curve edits. Use repeatable repository scripts for creating candidate copies, recording source/rig/action identities, baking derived samples, rendering complete clips and final export. Save the actual edited native source; never regenerate it from a stale pose manifest that discards curve edits. Read back the evaluated result after an edit; a successful command is not a passed motion.

## First experiment: complete MEL-37's carry-control proof

Reuse MEL-37 rather than add a tool-installation epic. One diagnostic take, one control hypothesis, one complete preview.

1. Copy the retained native source into a new isolated diagnostic directory with selection unset. AnimationLab.refine currently requires a winner; do not select rejected A just to obtain a copy. Use a direct isolated copy or the smallest explicit investigation-copy path.
2. Inspect frames 52–65: evaluated primary-grasp orientation, hilt arc, parent rotations and support reach. Test body/world-oriented posing converted into continuous local keys, deliberate breakdowns and curve handles. Simply changing every rotation to quaternions is not a demonstrated solution.
3. Keep the sword attached to the primary grasp. Coordinate shoulder/elbow/grasp staging for reachable support; do not detach it or repair reach using automatic uniform arm scaling. Preserve earlier/later motion and the intended carry. Existing matched support-to-FK utility is available only if needed; automatic return to IK is not assumed.
4. Save and reopen the diagnostic source; render one full 97-frame 30 Hz source-speed preview in the MEL-36 camera, plus only the disputed carry interval if needed. Record exact source/preview/rig/script identities and named changes.
5. Exit: no unexplained carry reversal or distracting disconnected-looking grasp, with expressive carry and ready continuity retained. Review full motion, not only endpoint residuals. Numerical measurements locate defects; no universal gap threshold is an artistic acceptance rule. Record human/temporal evidence separately.

Measure time to reviewable edit, tool failures, rework and visible improvement against the existing script route. No fixed savings claim. If MCP is unavailable or unreliable, perform the same native-source experiment via existing Blender Python; connectivity is not a new prerequisite. If the control hypothesis fails, record the missing capability and prepare the bounded animator brief instead of restarting broad solver/pose-offset tuning.

## High-value polish ideas

| Opportunity | Concrete use | When |
|---|---|---|
| Load/launch contrast | Edit channel spacing and handles so a compact continuing load releases into decisive outward hands; offset chest and elbow arrival. | MEL-38 complete candidate hypotheses |
| Hilt arc and carry | Display evaluated hand/hilt trajectories and orientation landmarks; author a curved outward lateral cut with a consequential exit. Motion paths diagnose, never independently drive the sword. | MEL-37 control proof, then MEL-34 |
| Body overlap | Let torso initiate and later brake while shoulder/arms finish the delivery; avoid every joint easing together. | MEL-38/34 |
| Recovery | Author distinct braking, re-grasp organization and staggered settle into ready; inspect boundary velocity rather than endpoint equality alone. | MEL-34 and branch sources |
| Grip and twist | Calibrate reusable grasp poses, subtle wrist articulation, forearm twist and finger enclosure; apply local corrections only after gesture selection. | MEL-25 |
| Defender composition | Use the delivered perspective camera throughout; diagnose the known low-ready crop with the whole action. A second view answers a specific projection question. | MEL-37 onward |
| Pose/action reuse | Retain useful load, grasp and carry poses plus separate complete Actions as starting material; do not turn a pose library into seven compulsory keys or mirrored attack vocabulary. | After the control proof |

These are proposed artistic uses of Blender's [Graph Editor](https://docs.blender.org/manual/en/4.5/editors/graph_editor/introduction.html), [motion paths](https://docs.blender.org/UATEST/manual/en/dev/animation/motion_paths.html) and [pose editing/library](https://docs.blender.org/manual/en/4.5/animation/armatures/posing/editing/index.html). Documentation describes capabilities, not compatibility verification of every API on the installed version. Curve ghost snapshots and source-speed comparisons can expose whether smoothing erased launch contrast. Screenshots help inspect shape; they do not establish uninterrupted rhythm.

## Boundaries and execution

MEL-37 owns the bounded MCP-assisted native carry experiment. MEL-38 owns three distinct whole performances after proof; MEL-34 selects/refines; MEL-25 fixes demonstrated deformation. MEL-39/40 retain explicit binding and native pilot; MEL-27/15 complete branch source/integration; MEL-35/11 retain reproducibility and human exchange acceptance. No new dependency on external asset-generation services, whole-rig replacement, physics simulation or Unreal Control Rig migration.

Preserve CF_v001, accepted EX_v002 source/native/config, production TP and C++ input/clock/contact/damage. Do not modify gameplay to accommodate an exploratory motion. Deliberate exaggerated timing inside authoring remains distinct from runtime accel/drag playback rate, which stays unchanged. The specialist fallback and two-refinement limit remain in force.
