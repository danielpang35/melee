# Native control adapter — archived Knight/CF compatibility

The working native body is selected by [WorkingCharacter.json](../../Config/WorkingCharacter.json).
AccuRig control adaptation and TP retargeting are pending. `AnimationLab new` without
an explicit adapter stops before creating files, preventing accidental Knight drafts.

Explicit `--adapter cf-controls-v1` batches snapshot `ArtSource/UserKnight/KN_v002/Knight_Animation.blend` and its
manifest. Body and deform rig are resolved from scene metadata; the existing
`CF_*` controls and adapter ID are retained for compatibility. The Knight's
body is CF-derived anatomy fitted to the supplied armor, with an independent
rest skeleton. Armor is in `Knight Armor (Deferred)`, hidden in viewport/render.
Do not unhide it for routine animation previews. Previous immutable CF batches
continue using their snapshotted rig/authoring code.

Exploration only. No export/import, runtime selection, damage authority or artistic acceptance.

`python Tools/AnimationLab.py new NAME --adapter cf-controls-v1` creates one isolated control proof with snapshots of its rig, adapter, camera and reference metadata. `python Tools/AnimationLab.py render NAME` uses the shared AnimationLab render lock and the saved MEL-36 camera. The complete native frame range is encoded at its source FPS, including one final-frame display interval. The legacy adapter retains its own 154-frame contract.

The initial `pose-controls.json` supplies sparse hand/body posing intentions, independent timings and descriptive events. It never supplies a blade trajectory. Primary hand posing assistance is evaluated only at authored keys. The resulting `.blend` is the editable source: `CF_CTRL` native FK curves, grasp transforms, support articulation and elbow-plane curves. Derived `weapon-samples.json` is an output. Never use it to regenerate the performance.

## Native controls

| Control | Space and behavior |
|---|---|
| CF_CTRL root and spine05–01 | Parent-local body/pelvis/chest FK; body and chest are independently keyed |
| clavicle.R/L, shoulder01.R/L | Independent parent-local shoulder/scapular approximation; no automatic torso compensation |
| upperarm01/02, lowerarm01/02, wrist.R | Native primary FK. Wrist articulation moves the palm and attached sword. Split forearm bones are editable twist channels; no automatic twist redistribution or scaling |
| CF_PrimaryGrasp | Editable wrist-local shaft frame derived from actual CF knuckles/palm; sword is its child, offset guardward by 70 mm |
| CF_SupportSocket | Primary-grasp-relative support placement, 125 mm pommelward |
| CF_SupportArticulation | Live shaft-local support wrist XYZ rotation about the fixed grip center; its separately timed native curves articulate the hand while the support target follows |
| CF_SupportGrasp | Editable support wrist-local palm calibration. After changing its transform, update CF_SupportWristTarget.matrix_basis to CF_SupportGrasp.matrix_basis.inverted(); then inspect the grasp |
| CF_ElbowPlane_L | Live world-space pole for the optional native support IK |
| CF_ElbowPlane_R | Visible world-space posing-assistance reference. Right playback remains FK; moving this reference alone does not rewrite FK curves |
| CF_CTRL support_influence | Shared 0–1 influence for support IK and wrist orientation. Match the evaluated pose before changing modes |
| finger1–5 segments, metacarpals | Editable native FK calibration; digit placement is rough and needs closer artistic review |

`rig.pose_arm` is the bounded two-link posing aid, not a playback solver. `rig.match_support_to_fk(CF_CTRL)` captures the current evaluated support arm, keys the previous-frame influence, switches both constraints with constant keys and writes the matched FK pose at the active frame. It changes the future mode; matching the return to IK is not implemented. Do not animate an unmatched space switch. Primary hand IK mode and automatic FK/IK round-trip are deliberately outside this proof.

Initial blocking now converts world grasp orientation to continuous native wrist
keys with `rig.key_world_grasp_orientations` after the parent arm curves are final.
This explicit authoring bake samples each source frame; the resulting wrist FK
remains editable and the sword remains attached to its grasp. It fixes the
demonstrated sparse-local carry winding without changing support reach or arm
scale. Re-running initial blocking is not a native refinement workflow: edit the
saved source directly to preserve artist curve edits.

## Refine native source

Initial blocking now finalizes parent-curve handles before `rig.key_world_grasp_orientations` converts authored world grasp rotations into compatible native wrist keys at each source frame. This resolves the MEL-37 carry wrist turnover; the resulting wrist curves remain editable. Changing parent motion later requires deliberate native wrist editing or another explicit conversion on an isolated copy. The native-input path does not regenerate or overwrite those edits.

The deeper `MEL37_KN_choreography_batch2/A_deep_countercoil` study exposed a separate limitation: sparse primary-arm FK interpolation can lose the intended hand route between keys (frame 45 drops roughly 420 mm below authored carry height). Continuous wrist orientation does not guarantee hand-path fidelity. This rejected source is retained as a focused diagnostic; do not treat the rough control proof as artistic or arbitrary-motion validation. See `Saved/MEL37Resume/critic-batch2.md` and the current TP checkpoint.

Use the existing explicit `select` command only after reviewing a complete preview. `refine` copies the selected `.blend` into a new candidate's `native-input.blend`. Edit that file's native curves, markers, range or FPS; render the new candidate. The adapter opens those native edits directly and derives new samples without regenerating from the initial JSON. Preview identity includes the native input hash. Existing previewed sources/inputs are immutable; new edits need another take. No candidate is selected by generation or rendering.

The saved fixed perspective camera may crop grip/weapon regions. Do not move it per candidate. Native timing and reach are exploratory and differ from accepted EX; selection requires an explicit later integration decision. The receipt distinguishes rough capability evidence, sampled-frame inspection and unavailable continuous/human review.

Targeted checks: `python Tools/AnimationAuthoring/test_adapters.py`.
