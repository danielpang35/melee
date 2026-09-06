# Citadel source assets

## Knight

**Knight**, by **piacenti**, from [OpenGameArt](https://opengameart.org/content/knight-2).
Licensed under [Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/).

Modifications for MeleeCombatLab: removed shield and original sword, normalized
scale, built a deformation skeleton, assigned skin weights, extracted a separate
first-person arm mesh, rebuilt the material for Unreal, and added runtime posing.
Neither the original artist nor OpenGameArt endorses this project.

Preserve this attribution in distributed credits. The original model is not an
authored animation pack; rigging and presentation integration are project work.

## Sword and environment surfaces

From [Poly Haven](https://polyhaven.com), under
[CC0 1.0](https://polyhaven.com/license):

- [Antique Estoc](https://polyhaven.com/a/antique_estoc)
- [White Sandstone Blocks 02](https://polyhaven.com/a/white_sandstone_blocks_02)
- [Cobblestone Floor 08](https://polyhaven.com/a/cobblestone_floor_08)
- [Roof Slates 02](https://polyhaven.com/a/roof_slates_02)

The sword was recalibrated to a blade base at Z=0 and tip at Z=100 cm. Materials
were rebuilt for Unreal. `manifest.json` records downloaded files, provider URLs,
and verified MD5 hashes. Textures use 2K source maps.

## Original project geometry

Arcade arch, dressed block, slate roof module, fountain baluster and bowl, and folded swallowtail cloth were
created for this project in `Tools/BuildCitadelArt.py`. Editable rig source and
FBX exports are in `Export`. No geometry from a commercial game was extracted.
