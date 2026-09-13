param([switch]$Sanitize)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$vsInstall=& $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (!$vsInstall) { throw 'Visual Studio C++ tools not found.' }
& (Join-Path $vsInstall 'Common7/Tools/Launch-VsDevShell.ps1') -Arch amd64 -HostArch amd64 -SkipAutomaticLocation | Out-Null
$outputDir=Join-Path $projectRoot 'Tests/bin/Audio'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
Push-Location $outputDir
try {
    $source=Join-Path $projectRoot 'Source/MeleeCombatLab'
    $flags=@('/nologo','/std:c++20','/EHsc','/W4','/WX','/Zi',"/I$source")
    if ($Sanitize) { $flags+='/fsanitize=address' }
    & cl.exe @flags (Join-Path $projectRoot 'Tests/AudioTests.cpp') (Join-Path $source 'Combat/CombatSimulation.cpp') (Join-Path $source 'Combat/Attacks/AttackStateMachine.cpp') '/Fe:AudioTests.exe'
    if ($LASTEXITCODE -ne 0) { throw 'Audio test compilation failed.' }
    & ./AudioTests.exe
    if ($LASTEXITCODE -ne 0) { throw 'Audio tests failed.' }
} finally { Pop-Location }
