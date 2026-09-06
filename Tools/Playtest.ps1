param([string]$Profile='Competitive')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$editor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$project=Join-Path $projectRoot 'MeleeCombatLab.uproject'
$arguments=@(('"'+$project+'"'),'/Engine/Maps/Entry','-game','-windowed','-ResX=1600','-ResY=900','-ForceRes','-nosplash','-CombatPlaytest','-CombatPlaytestQuit',('-LabProfile='+$Profile))
$process=Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output "Rendered playtest PID: $($process.Id); report: Saved/Playtests/results.json"
