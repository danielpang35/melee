param()

$ErrorActionPreference = 'Stop'

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$CorePatch = Join-Path $Here 'grounded-movement.patch'
$CompatPatch = Join-Path $Here 'local-drift-compatibility.patch'

$Excludes = @(
    '--exclude=Source/MeleeCombatLab/Character/MeleeCharacter.cpp',
    '--exclude=Source/MeleeCombatLab/Tests/CombatPlaytest.cpp',
    '--exclude=README.md'
)

Write-Host 'Preflighting grounded movement core against the current working tree...'
& git apply --check @Excludes $CorePatch
if ($LASTEXITCODE -ne 0) {
    throw 'Core movement patch still conflicts with the current checkout. No files were changed.'
}

Write-Host 'Applying grounded movement core (preserving locally drifted character/playtest/README files)...'
& git apply @Excludes $CorePatch
if ($LASTEXITCODE -ne 0) {
    throw 'Core movement patch failed unexpectedly.'
}

try {
    Write-Host 'Preflighting local-drift compatibility layer...'
    & git apply --check $CompatPatch
    if ($LASTEXITCODE -ne 0) {
        throw 'Compatibility layer did not match the freshly patched movement component.'
    }

    Write-Host 'Applying compatibility layer...'
    & git apply $CompatPatch
    if ($LASTEXITCODE -ne 0) {
        throw 'Compatibility layer failed unexpectedly.'
    }
}
catch {
    Write-Warning 'Compatibility step failed; reverting the core movement patch.'
    & git apply -R @Excludes $CorePatch | Out-Null
    throw
}

Write-Host ''
Write-Host 'Grounded movement v2 applied successfully.'
Write-Host 'Local edits in MeleeCharacter.cpp, CombatPlaytest.cpp, and README.md were preserved.'
Write-Host ''
Write-Host 'Next:'
Write-Host '  .\Tools\TestCore.ps1 -MovementOnly -Sanitize'
Write-Host '  .\Tools\Build.ps1 -Automation'
