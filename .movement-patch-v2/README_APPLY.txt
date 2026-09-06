MeleeCombatLab grounded movement — v2 local-drift installer

WHY V2 EXISTS
-------------
The original patch was based on repository commit:
02d9d7ee97cfef4c58d20146ad89216b2de3f82b

The local checkout reported conflicts in:
- Source/MeleeCombatLab/Character/MeleeCharacter.cpp
- Source/MeleeCombatLab/Tests/CombatPlaytest.cpp
- README.md

V2 deliberately does not modify those files.

Instead, the new movement component retains compatibility fields:
- bSprint
- ForwardInput
- Momentum
- Lunge

They are compatibility/telemetry shims only. They DO NOT drive the new
authoritative locomotion law. This allows local character, HUD/playtest, and
other code that still references the old public API to compile while preserving
the new velocity solver.

Exact PowerShell command from the repository root:

Expand-Archive -LiteralPath .\MeleeCombatLab-grounded-movement-v2.zip -DestinationPath .\.movement-patch-v2 -Force; & .\.movement-patch-v2\Apply-GroundedMovement.ps1

The installer first uses git apply --check. If the compatibility step fails
after the core patch is applied, it automatically reverses the core patch.
