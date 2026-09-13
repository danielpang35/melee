MeleeCombatLab — Grounded Body Controller
Base repository: danielpang35/melee
Base commit: 02d9d7ee97cfef4c58d20146ad89216b2de3f82b

Run this ONE LINE from the repository root after placing this ZIP there:

Expand-Archive -LiteralPath .\MeleeCombatLab-grounded-movement.zip -DestinationPath .\.movement-patch -Force; git apply --check .\.movement-patch\grounded-movement.patch; if ($LASTEXITCODE -eq 0) { git apply .\.movement-patch\grounded-movement.patch }

The command first checks that the patch applies cleanly, then applies it only if the check succeeds.

After applying, the intended local validation sequence is:

.\Tools\TestCore.ps1 -MovementOnly -Sanitize
.\Tools\Build.ps1 -Automation
.\Tools\Playtest.ps1

The full CombatTests suite has a documented pre-existing stationary-double-parry failure on this checkout; use -MovementOnly to isolate the new locomotion contract.
