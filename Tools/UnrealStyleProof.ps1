param([ValidateSet('import','environment','capture','open','save','restore')][string]$Mode='open',[ValidatePattern('^USP_v[0-9]{3}$')][string]$Revision='USP_v001',[ValidateSet('builtin','authored')][string]$Environment='builtin',[ValidateSet('control','normals','combined')][string]$Variant='combined',[ValidatePattern('^Environment_v[0-9]{3}$')][string]$EnvironmentRevision='Environment_v001',[ValidateSet('default','environment_compare','environment_step','environment_response','orientation_camera','maps_environment','material_compare','native','stage','geometry','amplitude','worldnormal','response','transfer')][string]$CaptureSet='default',[Alias('KeySpecular')][ValidateRange(0,1)][double]$KeySpecularScale=1.0,[ValidateRange(-360,360)][double]$CubemapAngle=0,[ValidateSet('baseline','reference18')][string]$CameraProfile='baseline',[ValidateSet('Stage_v001','Stage_v002','Stage_v003')][string]$StageRevision='Stage_v001',[switch]$Wait,[switch]$Full)
$ErrorActionPreference='Stop'
if($CaptureSet -eq 'transfer' -and $Full){throw 'Transfer stills must pass before full motion capture'}
$proofRoot=Split-Path -Parent $PSScriptRoot
$proofEditor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$proofArgs=@(('"'+(Join-Path $proofRoot 'MeleeCombatLab.uproject')+'"'),'-nosplash','-unattended','-LabProfile=Competitive',('-StyleProofRevision='+$Revision),('-StyleProofEnvironment='+$Environment),('-StyleProofEnvironmentRevision='+$EnvironmentRevision),('-StyleProofCaptureSet='+$CaptureSet),('-StyleProofCubemapAngle='+$CubemapAngle.ToString([System.Globalization.CultureInfo]::InvariantCulture)),('-StyleProofCameraProfile='+$CameraProfile),('-StyleProofStageRevision='+$StageRevision),('-StyleProofVariant='+$Variant),('-StyleProofKeySpecular='+$KeySpecularScale.ToString([System.Globalization.CultureInfo]::InvariantCulture)))
if($Mode -in @('open','save','restore')) {
    $proofArgs+=@(('-ExecutePythonScript="'+(Join-Path $PSScriptRoot 'OpenUnrealStyleProof.py')+'"'))
} else {
    $proofScript=if($Mode -in @('import','environment')){'ImportUnrealStyleProof.py'}else{'CaptureUnrealStyleProof.py'}
    $proofArgs+=@('-windowed','-ResX=960','-ResY=960','-ForceRes','-usefixedtimestep','-fps=30',('-ExecutePythonScript="'+(Join-Path $PSScriptRoot $proofScript)+'"'),('-abslog="'+(Join-Path $proofRoot ('Saved\ArtReview\UnrealStyle\'+$Revision+'\'+$Mode+'.log'))+'"'))
}
if($Mode -eq 'save'){$proofArgs+='-StyleProofSaveWinning';$proofArgs+=('-abslog="'+(Join-Path $proofRoot ('Saved\ArtReview\UnrealStyle\'+$Revision+'\save.log'))+'"')}
if($Mode -eq 'restore'){$proofArgs+='-StyleProofRestoreWinning';$proofArgs+=('-abslog="'+(Join-Path $proofRoot ('Saved\ArtReview\UnrealStyle\'+$Revision+'\restore.log'))+'"')}
if($Mode -eq 'environment'){$proofArgs+='-StyleProofImportEnvironment'}
if($Full){$proofArgs+='-USPFull'}
$proofProcess=Start-Process -FilePath $proofEditor -ArgumentList $proofArgs -WindowStyle Hidden -PassThru
Write-Output ('Style proof '+$Mode+' PID '+$proofProcess.Id)
if($Wait){
    $proofProcess.WaitForExit()
    if($proofProcess.ExitCode -ne 0){throw ('Unreal exited '+$proofProcess.ExitCode)}
    if($Mode -ne 'open'){
        $proofLog=Join-Path $proofRoot ('Saved\ArtReview\UnrealStyle\'+$Revision+'\'+$Mode+'.log')
        $proofMarker=if($Mode -in @('import','environment')){'USP_IMPORT_SUCCESS'}elseif($Mode -eq 'save'){'USP_SAVE_SUCCESS'}elseif($Mode -eq 'restore'){'USP_RESTORE_SUCCESS'}else{'USP_CAPTURE_SUCCESS'}
        if(-not(Select-String -LiteralPath $proofLog -Pattern $proofMarker -Quiet)){throw ('Missing success marker; inspect '+$proofLog)}
    }
}
