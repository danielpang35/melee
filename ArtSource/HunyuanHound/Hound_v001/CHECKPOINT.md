# Hound exemplar checkpoint

13 September 2026. Policy MCL-DEV-2026-09-08. One compact evidence/identity record; [the illustrated guide](../../../Docs/Visual/HOUND_SURFACE_STYLE_GUIDE.md) holds interpretation and recipes. [Notion](https://app.notion.com/p/3d42e3c3f8f881abb5c1c356dc68ee07) owns the user's design decision.

- **Selected style source:** byte-preserved [exemplar_style.fbx](Source/exemplar_style.fbx), SHA-256 `b17d0a1a06af68a3cfe423d0f862eff567442bf99b991311cdf9aab5a2630f17`; supporting [11-hound-bascinet.png](Source/11-hound-bascinet.png), SHA-256 `9dc54bd6b4cccbe7b9410e2f5615ee533a658c947fc478d189321a577ae0545b`. Originals remain at `D:/`. Daniel reports Hunyuan generation; generator version/settings and broader provenance are not present in the delivered files. Texture names do not establish generation date.
- **Decision:** primary surface-style authority, preserving the approved painted appearance and extending principles across the game. Visual guide/recipes only; no working-preset or runtime integration scope. The later question about changing light is addressed by a proposed selective reconstruction route and controlled source diagnostics.
- **Visible finding:** broad cool/warm steel patches and pale highlights exist in base color. The supplied shader darkens under opposing/cool-fill illumination, while painted reflection locations persist. The model is one object containing both busts from the reference sheet, with simplified mail, distorted breathing holes and uneven rear detail. Its style approval does not approve topology or a new character.
- **Evidence:** [manifest](manifest.json), four extracted unchanged maps, [native inspection scene](Inspection.blend), nine individual stills and six illustrated boards under [Review](Review/01-style-anatomy.png). Front/rear/left/right refer to the larger bust's heading; the smaller bust faces differently. The [palette](palette.json) measures only UV-covered pixels in annotated rectangles. [Verification](verification.json) checks source/map/render/native identities and sample coverage.
- **Delivery checks:** six boards visually inspected, including all four named model views. Package identity/native-load/palette checks pass; 26 targeted local path/content/source checks pass and the affected existing documents pass `git diff --check` (line-ending normalization warnings only). The Notion update was read back with the new direction, literal repository paths, historical acceptance, existing page mentions and reference image preserved. No C++ build or engine test was required for this documentation/source-inspection task.
- **Limits:** static Blender inspection; no continuous motion review, Hunyuan-viewer match, Unreal import, changed gameplay, performance result or new human review of derived assets. Warm/opposite/cool setups are diagnostic conditions rather than calibrated game lighting. The Blender native save produced a thumbnail-path warning; the saved scene was subsequently reopened and its mesh and four packed maps verified.
- **Next useful action:** if material production is subsequently requested, compare one isolated helmet/shoulder reconstruction against the unchanged exemplar under moving light and fixed exposure, then use the existing Unreal transfer route. No production asset is selected by this checkpoint.
- **Efficiency correction:** sample rectangles can include UV padding despite appearing painted. Intersect them with actual UV coverage before calculating colors; reuse the completed renders when correcting only palette measurements.

## Reproduce the evidence

Run from the repository root. These commands write only this isolated reference package; preserve existing evidence before deliberately regenerating it. `Inspection.blend` is an inspection scene, not a newly authored production material. No Hunyuan generation or Unreal session is invoked.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b --factory-startup --python-exit-code 1 --python ArtSource/HunyuanHound/Hound_v001/inspect_source.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b --factory-startup --python-exit-code 1 --python ArtSource/HunyuanHound/Hound_v001/verify_package.py -- --measure-palette
powershell -NoProfile -ExecutionPolicy Bypass -File ArtSource/HunyuanHound/Hound_v001/make_boards.ps1
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b --factory-startup --python-exit-code 1 --python ArtSource/HunyuanHound/Hound_v001/verify_package.py
```

Palette-only layout updates use `make_boards.ps1 -PaletteOnly`; they require no new model render. The verifier uses the same source UVs and checks the measured colors against the original image data. Image reduction demonstrates composition only, not engine mip/LOD behavior.
