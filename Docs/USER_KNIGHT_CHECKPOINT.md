# Knight body and armor integration

Policy MCL-DEV-2026-09-08. Owner: root. 9 September 2026.

Daniel requested the Knight in the current testing/editing pipeline, with body
and armor separate and future animations authored on a body that fits the Knight.
This supersedes the prior full-armor rest presentation default. No motion is
selected or accepted.

## Selected character

`ArtSource/UserKnight/KN_v002/Knight_Animation.blend` is the editable source.
`KN01_Rig` / `KN02_BodySkeleton` drives `KN01_Body` and the two eye meshes in
`Knight Body (Animate)`. `Knight Armor (Deferred)` contains the preserved supplied
armor/clothing shell, hidden in viewport and render by default. Its initial
weights remain editable for later armor work.

The supplied FBXs contain exterior armor/clothing, not a complete underlying
anatomical body. The body therefore uses CF_v001 topology and weights with the
Knight's resting arm placement. Daniel rejected the first localized shell fitting
because it distorted the head and arms. That version is retained only as rejected
evidence under `Saved/UserKnight/body-fit/rejected-distortion/`.

The corrected source preserves anatomy with uniform 0.96 scale and 0.08 m rearward
placement. Ordinary 4-degree hip abduction and 20-degree outward foot rotations
align the legs with the boots. There is no local head/arm compression or shell
projection. The body is inspected on its own and inside the armor. This is static
fitting; detailed armor articulation/clearance throughout new motion remains later
work, and the body must retain plausible standalone anatomy.

KN02 retains the 102 bone names/hierarchy but changes rest transforms. It is an
independent skeleton: do not bind historical CF, EX or TP clips just because the
names match. `manifest.json` records source/output identities and provenance.
CF_v001, KN_v001 and accepted EX/config remain protected originals. Earlier fit
passes and previews are preserved under `Saved/UserKnight/body-fit/`.

## Editing and testing route

- `python Tools/PrepareKnightBody.py`: explicitly rebuild the fitted body/armor
  source and body-only `SK_KnightBody.fbx`; no source originals are overwritten.
- `python Tools/AnimationLab.py new NAME`, then `render NAME`: new batches default
  to Knight body/native controls and snapshot the character, manifest and adapter.
  The `CF_*` controls and `cf-controls-v1` ID remain compatibility names. The
  default take is a technical control proof, not a selected performance. Existing
  CF snapshots and explicit `--adapter legacy` retain their historical character.
- `Tools/ImportKnightBody.py`: explicit isolated `/Game/UserKnight/KN_v002` mesh,
  skeleton and material import. No animations or armor are imported by this tool.
  Version or explicitly verify the reference pose after any future rest change.
- Default gameplay presentation loads this body in the existing independent
  Knight rest branch. New playable animation binding remains future work.
  `-KnightArmor` restores the previous full Knight; `-FoundationBody` restores the
  historical foundation presentation. The white floor remains the default;
  `-ArchivedCourtyard` restores the preserved courtyard.

## Evidence

`Saved/UserKnight/body-verification.json`: 102 bones, 13,380 body vertices,
normalized weights, maximum rest deformation below 0.0000002 m, and a native
arm-control edit moves the body by 0.347 m while armor remains hidden. Protected
input hashes match. The four existing targeted adapter checks passed once.
`Saved/UserKnight/body-code-review.md` records the independent scoped review and
its fit follow-up; no code blocker found. No gameplay clock/contact/state change.

`Saved/UserKnight/body-fit/body.png` and `armor-fit.png` show the corrected rest
comparison. `body-anatomy-preservation.json` verifies all 9,519 vertices unaffected
by the deliberate leg posing match original anatomy exactly under the uniform
transform, including head and arms. Final source SHA-256:
`cb12d96c19301bfd0b156ae5e5c13f6659795c66b7ec19b5720d560982e01ea8`.

The default workflow ran once through a 97-frame/30 Hz source-speed preview in
85.58 seconds. That `KN_v002_ready` snapshot and earlier `KN_v002_body_pipeline`
contain the subsequently rejected shape and are historical tooling evidence only.
The final corrected source separately passes rest/native-control checks. The
active MEL-37 owner was notified of the final identity and owns subsequent motion
work; no historical proof is a selected animation. Source and preview inspection
here used still images, not continuous temporal or human animation acceptance.

Both scoped C++ builds passed. The body imported on an independent KN_v002
skeleton; the first PIE check found all three characters using the correct mesh
(103 imported bones including FBX root), with white floor top Z=0. Its screenshot
exposed a material-assignment defect: Unreal array iteration returned struct
copies, and the native serialized material cache also required the existing
setter. The importer now retains edited slots in a fresh list, asserts assigned
interfaces, refreshes the native cache, and reproduces the source study shorts
mask at the uniform body scale. Material-only correction skips mesh reimport.
Final material-only correction and PIE verification completed successfully; the
process exited 0. `Saved/UserKnight/body-engine/rest-engine00001.png` was inspected
and shows the corrected standalone body with the study shorts, without the
fallback material. `body-engine/verification.json`, `body-import.json`, and
`body-material-final-launch.json` record the actual mesh, skeleton, source and
compiled module. No further body/source changes followed the frozen identity.
The existing Knight branch remains rest-only and does not play TP attack clips.

## Preserved supplied sources

The original selection is the negative-X, front-facing figure from
`ArtSource/UserKnight/KN_v001/Originals/20260909174448_72c77e03.fbx`.
Both supplied FBXs retain their SHA-256 identities in KN_v001/manifest.json;
neither supplied bones or textures. `Knight_Components.blend`, `Knight_Source.blend`
and `Knight_Rig.blend` remain intact. The full KN_v001 runtime armor skin has
approximately 61,000 triangles and remains available for later armor development.
