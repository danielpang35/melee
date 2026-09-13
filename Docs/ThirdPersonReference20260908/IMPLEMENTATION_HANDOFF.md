# TP native proof implementation checkpoint

2026-09-08. Opt-in technical proof; artistic and gameplay acceptance remain open. The parent owns engine builds, import execution, capture and integration verification. The author owns the separate TP source and visual revision. This checkpoint covers the consumer and pipeline helpers only.

## Files owned by this implementation

- New `Source/MeleeCombatLab/Visual/TPCombatPresentation.h/.cpp`: separate native TP sequence, body and authored static weapon, all-frame source/native validation, shared simulation source clock, cosmetic transition blend, diagnostics and idle selection reload.
- Narrow additions in `KnightPresentation.h/.cpp`: instantiate the optional consumer, pass the already computed fallback pose, expose diagnostics and choose external body visibility. Existing dirty foundation work is preserved; the full Git diff is not this change's ownership boundary.
- Narrow additions in `EXCombatPresentation.h/.cpp`: restore canonical visible weapon at each ordinary presentation call and expose visibility control so active external TP does not draw two weapons. No EX selection, sampling, motion, contact or timing code was changed.
- New `Tools/ExportThirdPersonSwing.py` and `Tools/ImportThirdPersonSwing.py`. No original exporter/importer was edited.

## Contracts

`-TPPreview=Saved/TPProof/selection.json` opts in. Without the flag, the original presentation remains selected. The selector names separate mesh, compatible animation, static TP weapon, immutable source weapon/skeleton sample files and revision; it cannot publish canonical motion. Unsupported states retain the original fallback after the cosmetic transition. Idle samples source .30; active neutral uses `State.exSourceTime`. Release bypasses transition blending. Body-world positioning follows authoritative capsule feet and yaw; local source root/pelvis shifts never move the capsule. Aim pitch and support-aware movement composition remain open beyond this early neutral proof.

Source contract: `ArtSource/CharacterReset/TP_v001/TP_v001_RightHorizontal.blend`; CF rig `CF01_CharacterRig`, 102 deform bones, unchanged CF hierarchy, rig object identity; source frames 1–154 at 60 Hz, world feet origin, −Y forward, −X anatomical right, +Z up. Weapon root is blade base, +Z tip at 1.035 m. Full body/eyes export independently from weapon meshes. TP grip/guard geometry is preserved in a dedicated static weapon FBX and imported materials.

Loader rejects incompatible hierarchy, duration, missing source samples, invalid weapon endpoints or source/native fidelity failure; previous valid selection is retained and the rejection logged. Every 154 source frames × 102 bones checks head positions and pose/rest deformation rotations against the native sampler. Current limits are 0.10 cm and 0.15°. Captured `TPPoseErrorCm` and `TPWeaponErrorCm` separately measure committed output against the sampled native pose/weapon. `TPBladeBaseErrorCm` and `TPBladeTipErrorCm` measure visual/canonical world endpoint differences; they do not prove complete contact ordering or gameplay fidelity.

Public Knight diagnostics: `TPSelected`, `TPActive`, `TPAuthored`, `TPRevision`, `TPSourceTime`, `TPPoseErrorCm`, `TPWeaponErrorCm`, `TPBladeBaseErrorCm`, `TPBladeTipErrorCm`, `TPBlendWeight`, `TPImportPoseErrorCm`, `TPImportRotationErrorDegrees`. The parent owns capture CSV integration.

Importer revision identity includes the explicit import profile, importer bytes and complete manifest bytes (which bind all export files). Changed pipeline settings or metadata generate a fresh native package. Selected raw data is copied to `Saved/TPProof/revisions/<identity>` so a later source export cannot corrupt an earlier selection. Newly named package reload is supported; in-place reimport is not claimed.

## Commands

Run from the project directory using PowerShell. Ordinary source changes need the last three steps only once this consumer is built.

```powershell
& ./Tools/Build.ps1 -MaxParallelActions 2
python ./Tools/ExportThirdPersonSwing.py
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' "$PWD/MeleeCombatLab.uproject" -run=pythonscript "-script=$PWD/Tools/ImportThirdPersonSwing.py" -unattended -nop4 -nullrhi
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' "$PWD/MeleeCombatLab.uproject" -game -TPPreview=Saved/TPProof/selection.json
```

The parent supplies the scoped automated proof command through `Tools/CaptureThirdPersonProof.ps1`. Import writes `Saved/TPProof/selection.json`, `import-receipt.json` and compressed component-space `native-import-samples.json` at phase keys and diagnostic subframes. It does not modify `Config/EXPreview.json`.

## Verified evidence / next gate

Final frozen Block04 source `fe1bbc88d8b1594c89218e47c19768147634293ce9489e5b4e0a58672344db93` was exported once after source/key review by its author and critic. Full FBX roundtrip passed: maximum bone-head error 0.000416124 cm and deformation rotation error 0.05595291°. Dedicated static TP weapon was included. The export receipt rehashed and preserved EX selection, EX source and both CF source identities. The parent reports both consumer compile passes succeeded. No builds were run by this agent.

Block02's author-reported visual/canonical release discrepancy around 43 cm was an explicit prototype conflict. Block04 is the selected source for fresh import and engine measurement; do not transfer Block02's exact endpoint metrics or claim contact agreement without the new replay. The parent owns the all-frame runtime import gate, replay and final contact/visual interpretation.

Independent review corrections applied: revision identity binds importer/profile and full manifest, preventing stale native assets when pipeline code changes. The importer preserves partial native imports and chooses a fresh `_retryNN` destination if a mesh lacks its compatible single sequence; it considers at most20 attempts and never deletes the failed assets. `Saved/TPProof/import-attempt.json` records the destination before import, and the final receipt records `attempt_destination` plus preserved incomplete attempts. Remaining engine execution results belong in the parent's final verification receipt.

First actual import exposed a Python binding name difference for the unreduced codec. The importer now loads `/Script/Engine.AnimCompress_BitwiseCompressOnly` as a native UClass, which `new_object` explicitly supports in the local engine's Python implementation. Remaining pose methods, enums and evaluation properties are checked before asset import. The parent owns the corrected commandlet retry and subsequent runtime fidelity gate; the first import failure is not a source/animation verdict.
