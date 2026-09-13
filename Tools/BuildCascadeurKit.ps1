param()
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$kitRoot=Join-Path $projectRoot 'ArtSource/Cascadeur'
$binaryRoot=Join-Path $projectRoot 'Saved/Cascadeur'
New-Item -ItemType Directory -Force -Path $kitRoot,$binaryRoot | Out-Null
$settings=Get-Content (Join-Path $projectRoot 'Config/CombatDefaults.json') -Raw | ConvertFrom-Json
$lines=@($settings.PSObject.Properties | Where-Object Name -ne 'SchemaVersion' | ForEach-Object {
    $_.Name+"`t"+([double]$_.Value).ToString('R',[Globalization.CultureInfo]::InvariantCulture)
})
[IO.File]::WriteAllLines((Join-Path $kitRoot 'tuning.tsv'),$lines)
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$vsRoot=& $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
& (Join-Path $vsRoot 'Common7/Tools/Launch-VsDevShell.ps1') -Arch amd64 -HostArch amd64 -SkipAutomaticLocation | Out-Null
$sourceRoot=Join-Path $projectRoot 'Source/MeleeCombatLab'
Push-Location $binaryRoot
try {
    & cl.exe /nologo /std:c++20 /EHsc /W4 /WX /O2 "/I$sourceRoot" (Join-Path $PSScriptRoot 'CascadeurReference.cpp') (Join-Path $sourceRoot 'Combat/Attacks/AttackStateMachine.cpp') (Join-Path $sourceRoot 'Combat/CombatSimulation.cpp') /Fe:CascadeurReference.exe
    if($LASTEXITCODE -ne 0){throw 'Reference exporter compilation failed'}
    & ./CascadeurReference.exe (Join-Path $kitRoot 'tuning.tsv') (Join-Path $kitRoot 'right_cut_reference.csv') 0
    if($LASTEXITCODE -ne 0){throw 'Reference export failed'}
} finally { Pop-Location }
& python (Join-Path $PSScriptRoot 'PrepareCascadeurKit.py')
if($LASTEXITCODE -ne 0){throw 'Cascadeur FBX kit preparation failed'}
