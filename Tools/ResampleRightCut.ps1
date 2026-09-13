param([string]$Output='Saved/AstraRightCut/reference.csv')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$vsRoot=& $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
& (Join-Path $vsRoot 'Common7/Tools/Launch-VsDevShell.ps1') -Arch amd64 -HostArch amd64 -SkipAutomaticLocation | Out-Null
$sourceRoot=Join-Path $projectRoot 'Source/MeleeCombatLab'
Push-Location (Join-Path $projectRoot 'Saved/AstraRightCut')
try {
    & cl.exe /nologo /std:c++20 /EHsc /W4 /WX /O2 "/I$sourceRoot" (Join-Path $PSScriptRoot 'CascadeurReference.cpp') (Join-Path $sourceRoot 'Combat/Attacks/AttackStateMachine.cpp') (Join-Path $sourceRoot 'Combat/CombatSimulation.cpp') /Fe:CascadeurReference.exe
    if($LASTEXITCODE -ne 0){throw 'Reference compilation failed'}
    & ./CascadeurReference.exe (Join-Path $projectRoot 'ArtSource/Cascadeur/tuning.tsv') (Join-Path $projectRoot $Output) 0 (Join-Path $projectRoot 'Config/RightCutWeapon.csv')
    if($LASTEXITCODE -ne 0){throw 'Reference resampling failed'}
} finally { Pop-Location }
