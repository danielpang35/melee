param([switch]$PrepareOnly,[switch]$DrawTracers,[switch]$ReadabilityCorrection,[switch]$GroundedTP,[string]$EngineRoot='C:/Program Files/Epic Games/UE_5.8')
$ErrorActionPreference='Stop'
$pilotRoot=Split-Path -Parent $PSScriptRoot
$fpSelection=if($ReadabilityCorrection -or $GroundedTP){'Config/ReadableWindupFP.json'}else{'Config/EXPreview.json'}
$tpSelection=if($GroundedTP){'Config/GroundedTP.json'}elseif($ReadabilityCorrection){'Config/ReadableWindupTP.json'}else{'Config/RightHorizontalPilot.json'}
& (Join-Path $PSScriptRoot 'PlayBenchmark.ps1') -EngineRoot $EngineRoot -ThirdPerson -FPSelection $fpSelection -TPSelection $tpSelection -DefaultsOnly -RightHorizontalPilot -PrepareOnly:$PrepareOnly -DrawTracers:$DrawTracers
