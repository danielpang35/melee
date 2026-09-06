# Citadel presentation rebuild

This direction supersedes the earlier incremental REHAUL plan. The user's later
revision permits combat changes where they improve the result. Existing unrelated
working-tree changes were present at the start of this work.

## Discard decisions

- Remove the lathed knight body and separate cylindrical arm renderer from play.
- Replace the generated sword assembly with one textured historical weapon.
- Replace grid paving, flat box banners, and repeated battlements as the scene's
  organizing language. Use deep galleries and a gatehouse with a varied skyline.
- Move floating target labels and training diagnostics behind F3.
- Retain the instancing infrastructure, shared simulation, and test fixtures.

## Art direction

A late-medieval limestone tournament court. Cream sandstone, charcoal slate,
oxblood and blue heraldry, worn dark steel, and sparing gold. Gallery shadow and
warm raking sunlight give the armored silhouettes a clear setting. Architecture
has a hierarchy: low dueling space, shaded arcade, roofline, royal gatehouse,
watchtower. Texture density is world-scale on stone rather than stretched UVs.

## Presentation architecture

1. Combat simulation owns state transitions, blade endpoints, contact, and defense.
2. `MeleePresentationPose` computes a sword frame and body/hand intent from state.
3. `KnightPresentation` evaluates the weighted rig: body lead and settle,
   distance-driven stride, head aim, reaction, two-bone arm IK, final hand frames.
4. `CombatRigMesh` commits component-space transforms in one hierarchy pass.
   Full-body and isolated first-person meshes share the deformation skeleton.
5. `WeaponPresentationComponent` applies a single calibrated transform to the
   complete imported sword. Its visual blade base and tip match simulation.
6. The courtyard instances persistent imported modules and uses simple explicit
   collision hulls. Decorative meshes never add accidental weapon collision.

The new runtime is a direct bone-pose backend, not an AnimBP or a Control Rig
asset. Authored animation clips can replace the body/stride evaluation before
the final grip constraints. Root motion and notifies do not supply damage.

## Reproducible asset build

1. `python Tools/FetchPresentationAssets.py` fetches and verifies the CC0 library
   and the CC-BY knight source archive. Preserve the attribution file.
2. Source archives, hashes, and license details are recorded in
   `ArtSource/Citadel/manifest.json` and `CREDITS.md`.
3. With Blender's `bpy` 4.2 available, run `python Tools/BuildCitadelArt.py`.
   The local build uses an isolated dependency directory, `Saved/ArtRuntime`.
4. Build the editor module with `Tools/Build.ps1` first; the importer uses its
   native `CitadelAssetTools` bridge. Run `Tools/ImportCitadelArt.py` using Unreal's
   Python commandlet. It creates
   persistent meshes, PBR materials, and textures under `/Game/Visual/Citadel`.
   Run `Tools/BuildCitadelEffects.py` in the same commandlet for cloth and sparks.
5. Run the rendered playtest and benchmark. Checked-in generated assets are
   sufficient for normal use; rebuilding source art is optional.

See the asset credits for licenses and modifications. Production quality must be
judged from rendered motion, not from asset import success or passing math tests.

## Combat change

Riposte windup now arrives at the raised release hilt, and recovery starts from
the raised release endpoint. Previously each transition teleported the hilt
12 cm. The actual release curve and attack timings are unchanged. This changes
the authoritative windup/recovery trajectory and is covered by direction/stab
continuity checks; it uses the user's explicit revision allowing combat changes.

## Rig and pipeline constraints

The skeleton preserves FBX reference scale during every bone override. Grip
targets use the imported estoc's measured blade/handle calibration. Clavicle
protraction precedes arm IK; final foot IK compensates for pelvis loading and
crouch on the flat gameplay floor. Runtime locomotion and reactions are scripted
poses, not a captured/authored animation library. Fingers remain in the source
hand pose; individual finger articulation, cloth simulation on the character,
ragdoll death, and final deformation cleanup remain production work.

Unreal 5.8's transient skeletal material field must be written through
native `USkeletalMesh::SetMaterials` through `CitadelAssetTools`, and the shared
skeleton must be created and saved explicitly.
The asset contract test checks both persisted dependencies, bone mapping, facing,
human scale, and sword calibration. `Benchmark.ps1 -CleanCapture` waits for shader
and asset compilation before the route warmup and removes the stats overlay.

## Verified delivery — September 6, 2026

The latest editor build succeeds. Fresh-process Unreal automation passes 3/3,
including persisted asset dependencies. Native presentation validation passes
615,111 sampled assertions under AddressSanitizer. The rendered tour passes
34/38. The native combat suite still fails the previously recorded double-parry
assertion after 557 checks; the four rendered failures are recorded in
`../../VALIDATION.md`. This is not an all-green combat validation.

Reviewed game captures and preserved reports are in `Captures/Citadel`:

- `first-person-parry.png`: actual first-person mesh, material, grip and weapon.
- `route_0.png` through `route_2.png`: full-body and arena presentation.
- `rendered-results.json` and `automation-results.json`: final test reports.
- `benchmark-summary.json`: 1080p High development-editor capture, 7.20 ms mean,
  9.91 ms p95, on this Ryzen 1600 / RTX 5070 machine. Clean capture disables unit
  stats; zero CPU/GPU scope counters mean unavailable, not zero cost.

This implements the replacement asset pipeline, skeletal presentation backend,
and tournament environment. It does **not** establish AAA vertical-slice quality.
The reviewed scene still needs bespoke architectural detailing, richer set
dressing and atmosphere; animation needs authored attack/reaction coverage,
closed finger grips and deformation refinement. These are visible art gaps,
not problems that mathematical pose checks can certify away.
