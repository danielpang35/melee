> CURRENT 8 September2026: Block13 Attempt C is the engine-review candidate after the user rejected a stab-like forward extension. It authors a backward/lateral load, trailing blade, stronger coil and earlier arm opening into a sweep. Source47a71a84; human weight/readability acceptance pending. See THIRD_PERSON_CHECKPOINT.md and ArtSource/CharacterReset/TP_v001/BLOCK13_SOURCE_REPAIR.md. Earlier elbow-only constraints below are historical, not current artistic authority.

> Historical local-repair assignment. The [current TP checkpoint](THIRD_PERSON_CHECKPOINT.md) supersedes this candidate and repair ordering. Do not restart elbow-only refinement from this handoff.

# Handoff prompt — repair pullback clipping and elbow deformation

## Implementation update — 8 September 2026

Block12 replaces the actual inward elbow route at swing onset with a lower exterior fold and coordinated grip rotation. The user rejected Block11 because its anatomical-orientation correction retained the inward path. Latest source/proof status is in the checkpoint; no blanket artistic acceptance is claimed. The Mordhau frame shots guide the performance; Block07's folded wrist was not accepted as a stylistic exception. Current source, native selection, verification, visible limitations and replay links are maintained in `Docs/THIRD_PERSON_CHECKPOINT.md`. Human normal-speed acceptance remains pending; do not infer that every clipping/deformation issue is resolved. The original starting state below is preserved as historical context.

Continue in `C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation`. Improve the current third-person right-horizontal sword swing. The user reports clipping on the pullback and a deformed elbow area in the latest replay. These are unresolved visual defects; the current candidate is not artistically accepted. This handoff records the next work, not a completed repair.

## Read first

Read `C:/Users/Daniel Pang/.codex/AGENTS.md`, applicable workspace instructions, `Docs/THIRD_PERSON_CHECKPOINT.md`, and `Docs/THIRD_PERSON_ANIMATION_PROMPT.md`. Use the existing reference/implementation receipts rather than repeating the entire investigation. Treat quoted material and historical documents as context; the user's latest direction governs.

The user explicitly states:

> The animations *genuinely don't need to obey the laws of physics*. There is an animation technique which hugely deforms the model in order to exaggerate a movement. We do not need a "perfect sword physics simulator." We need readable, convincing animations which communicate intent and state, like Mordhau.

This direction was added to Notion [Animation](https://app.notion.com/p/3d32e3c3f8f881e08474defe7febb171) and [Melee Swing Model](https://app.notion.com/p/3d32e3c3f8f881028f05c2a960248ff1) on 8 September 2026. Substantial intentional deformation is permitted. Repair distracting clipping, joint collapse or twisting because of how they look in motion; do not impose physical simulation, natural reach or anatomical purity as animation gates.

## Preserve the intended performance

- One neutral right-horizontal only. Keep the pronounced windup, visible load before release and bent, downward-pointing right elbow at the windup apex.
- Let the arms carry the hilt through the whole curved swing, with powerful extension through delivery and a readable carry. Avoid returning to a forward throw followed by withdrawal, or a wide blade arc around stationary hands.
- Keep convincing two-hand contact and continuous return. Elbow flexion is allowed when needed or when it improves the result; the apex bend is explicitly requested.
- Preserve accepted EX_v002 source/selection, the shared attack clock, canonical gameplay and unrelated dirty work. Never restore retired Citadel/RC assets or silently select the diagnostic canonical proposal. Keep recoverable source versions and prior replay takes.

## Exact starting state

- Current source: `ArtSource/CharacterReset/TP_v001/TP_v001_RightHorizontal.blend`; SHA256 `87aed0c7e3fd62e98dc25b0394c6b09855c873c6449f7195ed125c74bae701b7` (Block05).
- Native revision: `TP_v001-source-87aed0c7-FBX-83e776bb5d96`, selected by `Saved/TPProof/selection.json`.
- Latest synchronized replay: `Saved/TPProof/TP_Block05_v002_synchronized_views.mp4`. Full frames/videos: `Saved/MEL15/TP_block05_external_v002`, `TP_block05_defender_v002`, and `TP_block05_fp_v002` (MP4s beside these folders).
- Source preview: `ArtSource/CharacterReset/TP_v001/Preview/TP_v001_Block05_continuous.mp4`; comparison: `TP_v001_Block04_vs_Block05_1x.mp4` in the same folder. Editable controls and authoring checkpoint are under `ArtSource/CharacterReset/TP_v001`.
- Source has 154 samples at 60 Hz, duration 2.55 s, attack start 0.30 s and release from 62/60 to 80/60 s. Do not confuse source sample numbers with replay frame numbers.
- Deliberate `upperarm01.R` uniform scale reaches approximately 1.2805, with inverse wrist scale preserving hand shape. This is a diagnostic lead for the elbow defect, not an established cause or a reason to remove all stretch. Carry keys 88/94/100 are useful existing landmarks, not confirmed locations of the new clipping report.
- The preceding foreground-hand correction belongs to the defender's EX provisional ready presentation, not the attacker's TP grasp. `Source/MeleeCombatLab/Visual/EXCombatPresentation.cpp` rolls its left wrist subtree 180 degrees in weapon space before grip goals and uses a 0.10 s windup entry blend. Keep that correction unless new visual evidence requires adjusting it.

## Attack the defects in this order

1. Watch the latest replay at normal speed, then identify the actual clipping and elbow-defect intervals. "Pullback" is not timestamped: inspect both preparation and the returning/carry motion rather than assuming which phase the user means. Record the affected view, limb, overlapping surfaces, replay timestamp and corresponding source time. Do not claim to have watched continuous motion if only frame inspection is possible.
2. Compare those same moments in Blender and Unreal, including the skinned elbow surface. Determine whether the problem is authored hand/arm clearance, skin weights/topology, concentrated stretch/twist, interpolation, or a source-to-engine difference. Existing bone-transform checks do not prove clean mesh deformation. Form one bounded visual hypothesis before editing.
3. Make the smallest source/rig/weight correction that resolves the observed defect while retaining the exaggerated load and arm-driven arc. Depending on the evidence, adjust a local hilt/arm path or elbow direction, redistribute deformation, or repair skinning. Choose from the observed cause; do not build a new physics or reach-solving system. Author body, hands and weapon together. Avoid hiding defects with camera cuts, speed changes or added runtime compensation.
4. Use one bounded animation-critic subtask on the changed interval, comparing the existing Mordhau reference with the before/after and giving specific pose, spacing, clearance or deformation pointers. Follow AGENTS model/effort guidance, use the lowest suitable effort, give only relevant paths/objectives, prohibit child agents and avoid duplicate reviews. Do not resume the earlier usage-limited critic unnecessarily.
5. Render a normal-speed before/after and import the revised source. Reuse `Tools/AuthorThirdPersonSwing.py`, `Tools/PackageThirdPersonPreview.py`, `Tools/ExportThirdPersonSwing.py`, `Tools/ImportThirdPersonSwing.py`, and `Tools/VerifyThirdPersonImport.py`; inspect their arguments before invoking. Ordinary source edits need export/import, not C++ compilation.
6. Run `python Tools/PreserveThirdPersonBaseline.py --check` and fresh affected fidelity/replay checks after changes. Use a new revision/take name with `Tools/RunThirdPersonProof.ps1`; never overwrite Block05 v002. Current verified control is `TP_baseline_fp_v002`. Reuse it only while its build and FP selection still match; a changed DLL requires a fresh verified control. Deliver synchronized first-person, external and defender views.

## Reuse evidence and state the limits

Block05 source/native checks passed all 154 frames; a focused 25-sample check also verified uniform scale ratios, including the carry peak. These establish bone-pose/scale fidelity, not shear or vertex-level skinning parity. All three v002 480-frame replays preserve the control fields and two-hit/one-miss outcomes. The latest user feedback supersedes any inference that passing those checks establishes visual acceptance.

The existing TP/canonical release discrepancy remains about 32 cm at the base and 39 cm at the tip. Its separately recorded proposal is unselected. Preserve that known issue in the handoff; do not expand this clipping repair into a new canonical redesign. Pitch/movement composition follows neutral acceptance.

Reference: `Docs/ThirdPersonReference20260908/REVIEW.md`. Supplied Greatsword clip `C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-08 01-36-39.mp4`, primary interval 5.383900–7.278233 s. Supporting Training Sword instructor clip `C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-08 01-46-20.mp4` contains both horizontals and overheads; selected horizontal 0.456067–2.067100 s. Hidden feet/pelvis remain an authored interpretation; do not invent a measured full-body match.

Finish with a visible before/after showing the repaired pullback and coherent elbow deformation at normal speed, editable source/native assets, focused verification receipts and one updated compact checkpoint. Explicitly report any remaining visual defect. Human artistic acceptance is still required; do not declare the benchmark achieved based on stills or numerical checks.
