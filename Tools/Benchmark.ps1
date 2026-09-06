param([string]$Label='baseline',[string]$Profile='Baseline',[switch]$CleanCapture)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$editor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$project=Join-Path $projectRoot 'MeleeCombatLab.uproject'
$argsList=@(('"'+$project+'"'),'/Engine/Maps/Entry','-game','-windowed','-ResX=1920','-ResY=1080','-ForceRes','-nosplash','-NoVSync',('-VisualBenchmark='+$Label),('-LabProfile='+$Profile),'-ExecCmds="t.MaxFPS 0"','-csvGpuStats')
if ($CleanCapture) { $argsList += '-CitadelCapture' }
$process=Start-Process -FilePath $editor -ArgumentList $argsList -WindowStyle Hidden -PassThru
Write-Output "Visual benchmark PID: $($process.Id); label: $Label; profile: $Profile"
