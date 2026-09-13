param([string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$editor=Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.exe'
$project=Join-Path $projectRoot 'MeleeCombatLab.uproject'
if(!(Test-Path -LiteralPath $editor)){throw 'Pass the installed Unreal Engine root.'}
$arguments=@(('"'+$project+'"'),'/Engine/Maps/Entry','-game','-windowed','-ResX=1600','-ResY=900','-nosplash','-CascadeurPreview','-log=AstraRightCut_Playable.log')
Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
