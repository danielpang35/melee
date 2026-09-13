param(
    [ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Tag='TP_neutral_external_v001',
    [ValidateSet('firstperson','external','defender','side')][string]$View='external',
    [string]$Selection='Saved/TPProof/selection.json',
    [string]$FPSelection='Config/EXPreview.json',
    [switch]$Baseline,[switch]$Compose,[switch]$RightHorizontalPilot,[switch]$DrawTracers,[switch]$TracerSmoke,[switch]$ReadabilitySmoke,[switch]$PoseReview,
    [string]$EngineRoot='C:/Program Files/Epic Games/UE_5.8')
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$out=Join-Path $root ('Saved/MEL15/'+$Tag)
if(Test-Path -LiteralPath $out){throw 'Capture exists; choose a fresh tag.'}
$null=New-Item -ItemType Directory -Force -Path (Split-Path -Parent $out)
$selectionPath=if([System.IO.Path]::IsPathRooted($Selection)){$Selection}else{Join-Path $root $Selection}
if(!$Baseline -and !(Test-Path -LiteralPath $selectionPath)){throw "Missing TP selection: $selectionPath"}
$argsList=@(('"'+$root+'/MeleeCombatLab.uproject"'),'/Engine/Maps/Entry','-game','-windowed','-nosplash',
    '-ResX=960','-ResY=720','-ForceRes','-RenderOffscreen','-unattended','-usefixedtimestep','-fps=60',
    '-TPProof',('-EXGameplayCapture='+$Tag),('-EXGameplayView='+$View),
    ('-abslog="'+$root+'/Saved/MEL15/'+$Tag+'.log"'))
if(!$Baseline){$argsList+=('-TPPreview="'+$selectionPath+'"')}
$fpPath=if([IO.Path]::IsPathRooted($FPSelection)){$FPSelection}else{Join-Path $root $FPSelection}
$argsList+=('-EXPreview="'+$fpPath+'"')
if($Compose){$argsList+='-TPCompose'}
if($ReadabilitySmoke){if(!$RightHorizontalPilot){throw 'ReadabilitySmoke requires RightHorizontalPilot'};$argsList+='-ReadabilitySmoke'}
if($PoseReview){if(!$RightHorizontalPilot){throw 'PoseReview requires RightHorizontalPilot'};$argsList+='-TPPoseReview'}
if($DrawTracers -or $TracerSmoke){$argsList+='-DrawTracers'}
if($TracerSmoke){$argsList+=@('-TracerSmoke','-ExecCmds="mcl.DrawTracers 1"')}
if($RightHorizontalPilot){$argsList+=@('-RightHorizontalPilot','-CombatDefaultsOnly',('-CombatTuningReceipt="'+$out+'/engine-tuning.json"'))}
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.exe') -ArgumentList $argsList -WindowStyle Hidden -PassThru
$receipt=@{pid=$process.Id;tag=$Tag;view=$View;baseline=[bool]$Baseline;composition=[bool]$Compose;arguments=$argsList;
    module_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root 'Binaries/Win64/UnrealEditor-MeleeCombatLab.dll')).Hash;
    fp_selection=(Get-Content -Raw -LiteralPath $fpPath|ConvertFrom-Json)}
if(!$Baseline){$receipt.tp_selection=Get-Content -Raw -LiteralPath $selectionPath|ConvertFrom-Json;$receipt.tp_selection_sha256=(Get-FileHash -LiteralPath $selectionPath -Algorithm SHA256).Hash}
$receipt|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $root ('Saved/MEL15/'+$Tag+'-launch.json'))
$frameCount=if($PoseReview){540}elseif($ReadabilitySmoke){960}elseif($RightHorizontalPilot){720}else{480}
Write-Output "TP proof launched: PID $($process.Id), $Tag, $View, $frameCount frames at 60 fps."
