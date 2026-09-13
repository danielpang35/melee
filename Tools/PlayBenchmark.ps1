param(
    [string]$EngineRoot='C:/Program Files/Epic Games/UE_5.8',
    [switch]$ThirdPerson,
    [string]$FPSelection='Config/EXPreview.json',
    [string]$TPSelection='Saved/TPProof/selection.json',
    [switch]$DefaultsOnly,
    [switch]$RightHorizontalPilot,
    [switch]$DrawTracers,
    [switch]$PrepareOnly
)
$ErrorActionPreference='Stop'
$benchmarkRoot=Split-Path -Parent $PSScriptRoot
$module=Join-Path $benchmarkRoot 'Binaries/Win64/UnrealEditor-MeleeCombatLab.dll'
$fpPath=if([IO.Path]::IsPathRooted($FPSelection)){$FPSelection}else{Join-Path $benchmarkRoot $FPSelection}
$fp=Get-Content -Raw -LiteralPath $fpPath | ConvertFrom-Json
if($FPSelection -eq 'Config/EXPreview.json' -and $fp.revision -ne 'EX_v002-source-1615b76b-FBX-6a34514c-native-unreduced-v1'){
    throw 'The accepted FP benchmark selection changed; resolve deliberately before launching this benchmark.'
}
$tag='benchmark-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff')
$folder=Join-Path $benchmarkRoot ('Saved/Benchmark/'+$tag)
$null=New-Item -ItemType Directory -Path $folder
$argumentList=@(('"'+$benchmarkRoot+'/MeleeCombatLab.uproject"'),'/Engine/Maps/Entry',
    '-game','-windowed','-nosplash','-ResX=1280','-ResY=720',('-abslog="'+$folder+'/game.log"'))
$loadedTuningPath=Join-Path $folder 'engine-tuning.json'
$argumentList+=('-CombatTuningReceipt="'+$loadedTuningPath+'"')
if($RightHorizontalPilot){$argumentList+='-RightHorizontalPilot'}
if($DrawTracers){$argumentList+='-DrawTracers'}
$receipt=@{policy='MCL-DEV-2026-09-08';prepared_at=(Get-Date).ToString('o');
    fp_selection=$fp;fp_selection_sha256=(Get-FileHash -LiteralPath $fpPath -Algorithm SHA256).Hash;
    module_sha256=(Get-FileHash -LiteralPath $module -Algorithm SHA256).Hash;
    combat_defaults_sha256=(Get-FileHash -LiteralPath (Join-Path $benchmarkRoot 'Config/CombatDefaults.json') -Algorithm SHA256).Hash;
    third_person=[bool]$ThirdPerson;status='prepared';
    tuning_mode=$(if($DefaultsOnly){'defaults-only'}else{'normal'});
    right_horizontal_pilot=[bool]$RightHorizontalPilot;
    engine_tuning_receipt=$loadedTuningPath;
    limitation='Prepared file/module identities are not engine-loaded evidence. Inspect engine-tuning.json and game.log after launch. F4 edits/reset remain possible; this is not a session tuning lock or human acceptance.'}
$source=Join-Path $benchmarkRoot 'ArtSource/CharacterReset/EX_v002/EX_v002_MordhauRight.blend'
if($fp.source_path){$source=Join-Path $benchmarkRoot $fp.source_path}
$receipt.actual_fp_source_sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
if($receipt.actual_fp_source_sha256 -ine $fp.source_sha256){throw 'Accepted FP source differs from its selector.'}
$weaponData=Join-Path $benchmarkRoot $fp.weapon_motion
$receipt.weapon_motion_sha256=(Get-FileHash -LiteralPath $weaponData -Algorithm SHA256).Hash
$package=Join-Path $benchmarkRoot 'Content/EXPreview/EX_v002/EX_v002_Anim.uasset'
if($fp.animation_package_file){$package=Join-Path $benchmarkRoot $fp.animation_package_file}
$receipt.actual_animation_package_sha256=(Get-FileHash -LiteralPath $package -Algorithm SHA256).Hash
if($receipt.actual_animation_package_sha256 -ine $fp.animation_package_sha256){throw 'Accepted animation package differs from its selector.'}
$userTuning=Join-Path $benchmarkRoot 'Saved/Config/CombatTuning.json'
$receipt.user_tuning_present=Test-Path -LiteralPath $userTuning
if($receipt.user_tuning_present){
    $receipt.user_tuning_sha256=(Get-FileHash -LiteralPath $userTuning -Algorithm SHA256).Hash
    Copy-Item -LiteralPath $userTuning -Destination (Join-Path $folder 'CombatTuning.json')
}
Copy-Item -LiteralPath $fpPath -Destination (Join-Path $folder 'fp-selection.json')
$argumentList+=('-EXPreview="'+(Join-Path $folder 'fp-selection.json')+'"')
Copy-Item -LiteralPath (Join-Path $benchmarkRoot 'Config/CombatDefaults.json') -Destination (Join-Path $folder 'CombatDefaults.json')
if($DefaultsOnly){
    # Reload the same isolated project snapshot; Saved settings stay on disk and are ignored.
    $defaultsSnapshot=Join-Path $folder 'CombatDefaults.json'
    $argumentList+='-CombatDefaultsOnly'
    $argumentList+=('-CombatDefaults="'+$defaultsSnapshot+'"')
    $receipt.defaults_snapshot_sha256=(Get-FileHash -LiteralPath $defaultsSnapshot -Algorithm SHA256).Hash
}
if($ThirdPerson){
    $tpPath=if([IO.Path]::IsPathRooted($TPSelection)){$TPSelection}else{Join-Path $benchmarkRoot $TPSelection}
    $tp=Get-Content -Raw -LiteralPath $tpPath | ConvertFrom-Json
    $snapshot=Join-Path $folder 'tp-selection.json'
    Copy-Item -LiteralPath $tpPath -Destination $snapshot
    $argumentList+=('-TPPreview="'+$snapshot+'"')
    $receipt.tp_selection=$tp
    $receipt.tp_selection_sha256=(Get-FileHash -LiteralPath $snapshot -Algorithm SHA256).Hash
    $receipt.tp_package_sha256=@{}
    foreach($field in @('mesh','animation','weapon_mesh')){
        $asset=$tp.$field.Split('.')[0]
        if(!$asset.StartsWith('/Game/')){throw 'TP benchmark asset must be a project package.'}
        $assetFile=Join-Path $benchmarkRoot ('Content/'+$asset.Substring(6)+'.uasset')
        $receipt.tp_package_sha256[$field]=(Get-FileHash -LiteralPath $assetFile -Algorithm SHA256).Hash
    }
    if($tp.source_path){
        $receipt.actual_tp_source_sha256=(Get-FileHash -LiteralPath (Join-Path $benchmarkRoot $tp.source_path) -Algorithm SHA256).Hash
        if($receipt.actual_tp_source_sha256 -ine $tp.source_sha256){throw 'TP source differs from its selector.'}
    }
}
$receipt.arguments=$argumentList
$receiptPath=Join-Path $folder 'launch.json'
$receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath
if(!$PrepareOnly){
    $engine=Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.exe'
    # This is the user's interactive play window, not a background capture helper.
    $process=Start-Process -FilePath $engine -ArgumentList $argumentList -WindowStyle Normal -PassThru
    $receipt.status='launched'
    $receipt.pid=$process.Id
    $receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath
}
Write-Output $receiptPath
