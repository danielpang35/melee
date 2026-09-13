$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$vs=& $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if(!$vs){throw 'MSVC not found'}
& (Join-Path $vs 'Common7/Tools/Launch-VsDevShell.ps1') -Arch amd64 -HostArch amd64 -SkipAutomaticLocation | Out-Null
$out=Join-Path $root 'Saved/MEL15/production'
Push-Location $out
try {
    & cl.exe /nologo /std:c++20 /EHsc /W4 /WX /Od ("/I"+$root+'/Source/MeleeCombatLab') ($root+'/Tests/EXGameplayTests.cpp') ($root+'/Source/MeleeCombatLab/Combat/Attacks/AttackStateMachine.cpp') ($root+'/Source/MeleeCombatLab/Combat/CombatSimulation.cpp') /Fe:EXGameplayTests.exe
    if($LASTEXITCODE -ne 0){throw 'EX contact compilation failed'}
    & ./EXGameplayTests.exe ($out+'/EXWeapon.txt')
    if($LASTEXITCODE -ne 0){throw 'EX contact tests failed'}
} finally {Pop-Location}
