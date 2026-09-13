# MeleeCombatLab

> **GitHub review edition:** start with [the review entry point](Docs/GITHUB_REVIEW.md) and [art gallery](Docs/Review/README.md). Native art archives and runtime asset binaries remain in the full local project; this checkout is for source/design review.


A single-player first-person longsword lab in Unreal Engine 5.8. Aim, timing and footwork drive combat; C++ owns the attack clock, movement, blade contact and damage.

**Every agent starts with [AGENTS.md](AGENTS.md) and [current development](Docs/DEVELOPMENT.md).** Policy MCL-DEV-2026-09-08: generate several cheap complete-motion candidates, compare, select, refine, repeat. Expensive routine validation is unnecessary.

## Current baseline
EX_v002 first-person right-horizontal source and native Unreal playback are user-approved. Integration and same-process package selection exist. The corrected TP/body pilot was rejected; FP animation and swing feel received positive feedback. Preserve FP feel while diagnosing defender readability and reassessing workflow/tools. Third-person and the complete playable exchange remain under development; [the TP checkpoint](Docs/THIRD_PERSON_CHECKPOINT.md) owns the current candidate. MB_v005_SurfaceRepair on the AccuRig skeleton is the current authoring body; Config/WorkingCharacter.json owns selection. KN_v002 and CF_v001 remain preserved earlier foundations. Historical Citadel/RC work is not the new animation starting point.

## Fast authoring
```powershell
python Tools/AnimationLab.py new right_horizontal_batch01
python Tools/AnimationLab.py render right_horizontal_batch01
```
Open ArtSource/AnimationLab/right_horizontal_batch01/index.html. The default native adapter creates one technical control proof on KN_v002. Author three distinct complete performances through the native adapter workflow before comparing them with one source-speed camera. Select a winner and refine it using [the workflow](Docs/ANIMATION_WORKFLOW.md); only winners go to engine integration.

## Play and build
```powershell
.\Tools\PlayBenchmark.ps1
.\Tools\PlayBenchmark.ps1 -ThirdPerson
.\Tools\PlayBenchmark.ps1 -DefaultsOnly
```
The launcher records the accepted FP selection, optional explicit TP selection, module and tuning input identities. It performs no automatic captures or tests. Use -PrepareOnly to record the launch without starting Unreal. Add -DefaultsOnly for a comparison that loads an isolated copy of project defaults and ignores Saved tuning, including on F4 LOAD. Saved settings remain untouched by launching this mode.

Normal tuning loads in order: built-in values → `Config/CombatDefaults.json` → `Saved/Config/CombatTuning.json` when present. Later files override matching fields; the loader clamps finite numeric values to supported ranges. Invalid loads report failure and retain the previous effective values. F4 RESET restores built-in values, not the project JSON; SAVE and PROMOTE still explicitly write settings. F4 edits/reset remain available in defaults-only mode, so it fixes the load inputs rather than locking the whole session.

F4 diagnostics and developer logs identify loaded paths, outcomes and effective values. A benchmark's `launch.json` records preparation; Unreal writes `engine-tuning.json` beside it when tuning is loaded or changed. Inspect that engine receipt for actual effective values and their identity; a preparation receipt alone does not prove a successful load. Direct launches support `-CombatDefaultsOnly`, `-CombatDefaults="<absolute JSON path>"` and `-CombatTuningReceipt="<absolute output path>"`. [MEL-41 implementation evidence](Docs/TUNING_PROVENANCE_CHECKPOINT.md) records the focused verification.

Build only changed C++ or integration code with Tools/Build.ps1. UE 5.8, Visual Studio C++ and the Windows SDK are required. Heavy renders, imports and builds run sequentially; default compiler concurrency is two.

## Controls
WASD/mouse move/look; Shift sprint; Ctrl crouch; Space jump; LMB strike; E/wheel-up stab; RMB parry; Q legal feint; 1–6 attack origins; F2 training pattern; F3 diagnostics; F4 live tuning; F5 external inspection; F6 infinite stamina; R reset.

Directions name attack origin. Aim/footwork change spatial contact without accelerating playback. Config/CombatDefaults.json contains project tuning.

The [external audit disposition](Docs/EXTERNAL_AUDIT_DISPOSITION.md) separates confirmed tuning differences, historical validation results, and deferred changes with Linear owners.

## Visual quality and art production

The [confirmed reference direction](Docs/MEL17_REFERENCE_ROUTE.md) anchors the [visual rubric and current audit](Docs/ART_CRITIC_REVIEW.md), [art/performance implementation guide](Docs/Visual/STYLE_AND_PERFORMANCE.md), [game UI guide](Docs/Visual/UI_STYLE_GUIDE.md) and [movement inventory](Docs/ANIMATION_WORKFLOW.md#finished-slice-movement-inventory). Target: 100–144 FPS on mid-tier PCs; exact hardware/resolution and measured support remain open. Scores describe inspected evidence, not human acceptance or shipping certification.

## Ownership and directories
- Source/MeleeCombatLab/Combat: authoritative simulation and collision.
- Camera, Visual, Character and Movement: presentation, input and locomotion.
- ArtSource/CharacterReset: current character and selected authored source.
- ArtSource/AnimationLab: isolated snapshots, candidates, previews and selection decisions.
- Content/Config: runtime assets and settings.
- Tools: authoring, launch and focused verification; [tool guide](Tools/README.md).
- Docs: current rules/workflow/checkpoints; Docs/Archive: history.
- Saved/Intermediate/Binaries: local generated output; do not use ignored evidence as the only production source.

[Linear](https://linear.app/meleeslasher/project/melee-combat-lab-longsword-exchange-c906057fa194) owns execution; [Notion](https://app.notion.com/p/3d32e3c3f8f88166821dcab5f044efa2) owns design/acceptance. [VALIDATION.md](VALIDATION.md) defines lean checks. [Documentation ownership](Docs/DOCUMENTATION_OWNERSHIP.md) defines authority; [audit](Docs/DOCUMENTATION_AUDIT.md) inventories local records. [Project scope](PROJECT_SPEC.md) is a derived design summary. Preserve [Citadel attribution](ArtSource/Citadel/CREDITS.md) and [audio attribution](ArtSource/CombatAudio/CREDITS.md). No complete authored library, multiplayer or shipping-performance acceptance is claimed.
