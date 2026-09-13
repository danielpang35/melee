# Block04 review — extended delivery

8 September 2026. A complete, editable neutral right-horizontal prototype is now imported into Unreal. This is an early engine proof, with artistic and contact agreement still open; it is not an accepted replacement for EX_v002.

The user-directed change is clear arm extension through powerful delivery. Elbow flexion is conditional on necessity or a more immersive, convincing result. This direction was updated and fetched back in Notion's Animation and Melee Swing Model pages, the local third-person prompt, and the animation critic's review. Block04 extends the arms without scaling them or moving the shoulders forward to erase the extension. The critic passed the front/side delivery keys and confirmed the result in Unreal.

## Review media

- [Mordhau and source, normal speed](../../ArtSource/CharacterReset/TP_v001/Preview/TP_v001_Mordhau_comparison.mp4): distinct captures, onset alignment only. The player's Greatsword reference is primary; instructor Training Sword horizontals are supporting evidence. Overheads are excluded. Cropped reference feet/pelvis mean lower-body support is an authored interpretation.
- [Source continuous preview](../../ArtSource/CharacterReset/TP_v001/Preview/TP_v001_Block04_continuous.mp4) and [stepped preview](../../ArtSource/CharacterReset/TP_v001/Preview/TP_v001_Block04_stepped.mp4).
- [Source and engine at the same source clock](../../ArtSource/CharacterReset/TP_v001/Preview/TP_v001_Source_Engine_comparison.mp4), with the final engine idle reset explicitly labelled.
- [Synchronized first-person, external and defender replay](../../Saved/TPProof/TP_Block04_synchronized_views.mp4): identical neutral inputs and simulation clocks, two hits then one range miss, preserved canonical weapon.
- [Critic's specific findings](ANIMATION_CRITIQUE.md): extended delivery survives the pipeline. The later hands-at-waist catch may absorb momentum too narrowly; review it at normal speed before deciding whether to maintain outward reach longer. Blade fragmentation against the scene and overlap with the opponent are separate presentation issues.

The close defender view adds a genuine grip-readability blocker: trailing fingers cup beside/below the handle at capture0057; leading fingers form an open loop beside it at0063. Foreground occlusion does not explain all of this. Wrist closure is not finger contact. Correct the source with separate per-hand/per-joint grasp poses and thumb opposition around the actual handle, preserving the approved extended delivery and hilt path; inspect isolated hand close-ups before re-exporting.

Review performed here is decoded frame-sequence inspection. Continuous human playback acceptance remains pending.

## Technical evidence

Selected source SHA256: `fe1bbc88d8b1594c89218e47c19768147634293ce9489e5b4e0a58672344db93`. Native revision: `TP_v001-source-fe1bbc88-FBX-dfcffc2bfc14`.

Both scoped C++ builds passed. FBX roundtrip covered154 frames; runtime checked all154 frames ×102 deform bones, with maximum bone-head error0.000492870cm and relative rotation error0.000694626°. Independent seven-key/nine-subframe checks passed with maxima0.000329520cm /0.000346493°. Source/native identities and full finite sample coverage are required. These checks establish transform fidelity, not skin deformation or artistic quality.

The separate TP consumer samples the simulation's original1× source clock, uses full native release poses and its own exported weapon, and never selects its motion as canonical gameplay. EX_v002 source, native assets, timing, projection and selection remain preserved; ten pinned baseline files pass the hash check. All three480-frame replays passed and have identical combat/control fields and hit events versus the FP baseline. Neutral replay results are recorded per view in `Saved/MEL15/*/verification.json`.

Actual external release endpoint differences versus canonical are38.37cm at the base and39.03cm at the tip. Unchanged contact events demonstrate preservation of existing gameplay, not agreement of the cosmetic weapon with those contacts. This discrepancy is too large to accept as a solved presentation. A separate diagnostic proposed-canonical track compares contact consequences without applying it.

The [proposed-canonical tradeoff](../../Saved/TPProof/proposed-canonical/TRADEOFF.md) uses unchanged combat simulation in a standalone harness. Nine nearby targets remain hits, two distant targets remain misses, and one three-target fixture retains contact order. Several hit times change (up to33.33ms earlier in this bounded set); the150cm center contact shifts20.62cm lower despite equal hit time. This is a concrete alternative, not evidence that every contact remains equivalent or that further reconciliation with the current canonical path is impossible. No proposed track was applied.

## Editable source and next decision

[Blender source](../../ArtSource/CharacterReset/TP_v001/TP_v001_RightHorizontal.blend), [pose controls](../../ArtSource/CharacterReset/TP_v001/pose-controls.json), and [authoring loop](../../ArtSource/CharacterReset/TP_v001/AUTHORING_CHECKPOINT.md) preserve recoverable earlier blocks. Source helper controls are editable references plus baked FK, not a completed interactive IK/FK switching rig.

Edit source → inspect revised keys → render1× → export with `Tools/ExportThirdPersonSwing.py` → import with `Tools/ImportThirdPersonSwing.py` → run `Tools/VerifyThirdPersonImport.py` → capture fresh tags with `Tools/CaptureThirdPersonProof.ps1` → verify with `Tools/VerifyThirdPersonProof.py` against the baseline. Ordinary source edits need no C++ rebuild.

Before adopting this revision, review the delivery/catch at normal speed and decide how to reconcile the visible release with canonical contacts. The approved first-person swing and combat semantics cannot be replaced silently. Pitch adaptation and support-aware movement composition are still pending after neutral acceptance; current TP placement follows authoritative capsule feet and yaw.
