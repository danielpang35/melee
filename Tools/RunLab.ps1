param([string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',[switch]$Playtest,[switch]$QuitAfterTest)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$projectFile=Join-Path $projectRoot 'MeleeCombatLab.uproject'
if (!(Test-Path $editor)) {throw 'Unreal editor executable is missing.'}
$labArguments=@(('"'+$projectFile+'"'),'/Engine/Maps/Entry','-game','-windowed','-ResX=1600','-ResY=900','-nosplash','-NoVSync')
if ($Playtest) {$labArguments+='-CombatPlaytest'}
if ($QuitAfterTest) {$labArguments+='-CombatPlaytestQuit'}
$windowStyle='Normal'
if ($Playtest) {$windowStyle='Hidden'}
$labProcess=Start-Process -FilePath $editor -ArgumentList $labArguments -WindowStyle $windowStyle -PassThru
Write-Output "MeleeCombatLab PID: $($labProcess.Id)"
