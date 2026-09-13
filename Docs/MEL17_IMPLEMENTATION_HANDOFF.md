# MEL-17 implementation handoff

The accepted material baseline is **ST_v002 / USP_v016**. The user explicitly accepted material and motion after receiving the three actual Unreal clips. `Saved/ArtReview/UnrealStyle/USP_v016/user_acceptance.json` binds that response to the captured evidence. The independent critic's visual assessment is in `Docs/MEL17_TRANSFER_CRITIC.md`; the critic inspected frame contacts and selected full-size PNGs, without claiming video playback.

## Open the accepted proof

From the repository root, with Unreal Engine 5.8 installed:

```powershell
.\Tools\UnrealStyleProof.ps1 -Mode open -Revision USP_v016 -Environment authored -EnvironmentRevision Environment_v005 -Variant combined -StageRevision Stage_v003 -CubemapAngle -90
```

The saved map is `/Game/Visual/StyleProof/USP_v016/L_HelmetStyleProof`. It uses an isolated no-pawn GameMode, the fitted proof camera, opaque Default Lit, imported normals/tangents, construction-normal foundation plus authored endpoint, Competitive TAA, disabled SSR/GI/reflection methods and no Nanite or collision. `winning_state.json` records the saved variant, environment, stage and camera. No global renderer, combat code or broader character assets were changed by this implementation.

## Editable source and rebuild

Accepted source: `ArtSource/StyleReference/MEL17/SteelTransfer/ST_v002/Helmet_Steel_ST_v002.blend`. The source package retains region targets, protection/influence, packed target textures and construction normals. Frozen export: `ArtSource/StyleReference/MEL17/UnrealProof/USP_v016/`. The accepted Clay_v005 geometry and Steel_v025 material authorities remain unchanged.

Choose a new unused revision when rebuilding; completed revisions are immutable. With the existing Python 3.11 art runtime under `Saved/ArtRuntime`:

```powershell
python Tools/BuildUnrealStyleTransfer.py --prepare --revision USP_v018 --source-manifest ArtSource/StyleReference/MEL17/SteelTransfer/ST_v002/source_manifest.json
python Tools/BuildUnrealStyleTransfer.py --bake --revision USP_v018
.\Tools\UnrealStyleProof.ps1 -Mode import -Revision USP_v018 -Environment authored -EnvironmentRevision Environment_v005 -CaptureSet transfer -StageRevision Stage_v003 -CubemapAngle -90 -Wait
.\Tools\UnrealStyleProof.ps1 -Mode capture -Revision USP_v018 -Environment authored -EnvironmentRevision Environment_v005 -CaptureSet transfer -StageRevision Stage_v003 -CubemapAngle -90 -Wait
```

The importer verifies source hashes, every imported triangle corner, UVs, material slots, normals, tangents and signs using an export of the actual built LOD0 buffers. UE 5.8's procedural-mesh inspection helper reports incorrect handedness; the dedicated FBX reader avoids that helper. Source-side finite tangent fallbacks and endpoint bakes match Unreal's interpolated basis.

## Evidence and limits

`USP_v016/run_002` contains five neutral transfer PNGs. `run_003` contains six daylight stills and three consecutive 60-frame sequences at 30 fps: helmet rotation, moving key and physical shade transition. All 186 images were fully decoded, and all delivery videos decoded to their expected frame counts. Effective viewport size was 1525x870 with an 870px square camera area. The measured gameplay-size helmet is 171px tall; this is a declared screen-size scenario, not full-game distance testing.

The baseline has 64,108 triangles, 16 parts/material slots and three 2048px maps. This is an isolated material proof; dedicated profiling, deformation, shoulder/breastplate transfer and full-body integration remain later work under their existing project gates.

Focused verification: 14 transfer-contract tests passed with one Windows symlink-permission skip; six capture-validation tests passed. Actual editor import/capture/save receipts provide runtime verification. Failed intermediate revisions remain preserved as diagnostic evidence.

## Controlled edit/reimport demonstration

ST_v003 changes only target direction in **Left wrapping brow, region 7**, by +6 degrees around object X. Its region footprint and alpha remain unchanged. The interior effective weight is 0.096, so the resulting shaded-normal change is approximately 0.6 degrees. USP_v017 is reserved for this demonstration; USP_v016 remains the accepted winning baseline. The demonstration is complete. USP_v017/run_002 captured five comparison images with clean exit. Smooth controls differ by at most2 RGB levels; authored differences above3 levels are confined to the selected brow region (888 front pixels and3,862 three-quarter pixels). Masks are byte-identical; all normal-map changes above1 LSB lie in region7. Tiny one-level numerical differences are itemized in export_receipt.json. repeatability_receipt.json binds export/import/capture and final restoration evidence. The accepted baseline was restored with actual component/camera/settings equality, clean exit and all77 asset files byte-identical across the final read-only restore. Earlier restore attempts reserialized one unchanged stage material; the helper now skips redundant writes and rejects mutation in read-only mode.


To verify/select the preserved baseline without saving any assets:

```powershell
.\Tools\UnrealStyleProof.ps1 -Mode restore -Revision USP_v016 -Environment authored -EnvironmentRevision Environment_v005 -Variant combined -StageRevision Stage_v003 -CubemapAngle -90 -Wait
```

The portable review folder and ZIP under `Saved/ArtReview/UnrealStyle/USP_v016` include accepted/demo editable sources, maps, scoped Unreal assets, tools, configuration and receipts with hashes. The `source/` directory preserves repository-relative paths for a compatible MeleeCombatLab checkout. Unreal5.8 and the Python art/video runtimes are external prerequisites; this packet does not bundle an engine installation or the whole gameplay project.
