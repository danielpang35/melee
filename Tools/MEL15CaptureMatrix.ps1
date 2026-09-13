param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$TagPrefix,
    [ValidateSet('front','side','rear3q','defender','firstperson','moving','crouch','pitchup','pitchdown','fp_moving','fp_crouch','side_pitchup','side_pitchdown')]
    [string[]]$Jobs=@('firstperson','side'),
    [ValidateRange(0,2)][double]$LeadIn=0.2,
    [ValidateRange(15,120)][int]$Fps=30,
    [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',
    [switch]$SkipUbtSdkSetup,
    [switch]$PrintOnly
)
$ErrorActionPreference='Stop'
if(@($Jobs | Select-Object -Unique).Count -ne $Jobs.Count){throw 'Each matrix job must appear only once.'}
$definitions=@{
    front=@{Camera='front';Pose='standing';Pitch=0}
    side=@{Camera='side';Pose='standing';Pitch=0}
    rear3q=@{Camera='rear3q';Pose='standing';Pitch=0}
    defender=@{Camera='defender';Pose='standing';Pitch=0}
    firstperson=@{Camera='firstperson';Pose='standing';Pitch=0}
    moving=@{Camera='side';Pose='moving';Pitch=0}
    crouch=@{Camera='side';Pose='crouch';Pitch=0}
    pitchup=@{Camera='firstperson';Pose='standing';Pitch=85}
    pitchdown=@{Camera='firstperson';Pose='standing';Pitch=-85}
    fp_moving=@{Camera='firstperson';Pose='moving';Pitch=0}
    fp_crouch=@{Camera='firstperson';Pose='crouch';Pitch=0}
    side_pitchup=@{Camera='side';Pose='standing';Pitch=85}
    side_pitchdown=@{Camera='side';Pose='standing';Pitch=-85}
}
$projectRoot=Split-Path -Parent $PSScriptRoot
# Check every selected destination before starting the first owned instance.
foreach($job in $Jobs){
    $folder=Join-Path $projectRoot ('Saved\ArmRepair\'+$TagPrefix+'_'+$job)
    if(Test-Path -LiteralPath $folder){throw "Matrix tag already exists; choose a fresh TagPrefix: $folder"}
}
foreach($job in $Jobs){
    $definition=$definitions[$job]
    $parameters=@{Tag=($TagPrefix+'_'+$job);Camera=$definition.Camera;Pose=$definition.Pose;Pitch=$definition.Pitch;
        LeadIn=$LeadIn;Fps=$Fps;EngineRoot=$EngineRoot;SkipUbtSdkSetup=$SkipUbtSdkSetup;PrintOnly=$PrintOnly}
    if(-not $PrintOnly){$parameters.Wait=$true;Write-Host "Starting matrix job $job ($($definition.Camera), $($definition.Pose), pitch $($definition.Pitch))."}
    & (Join-Path $PSScriptRoot 'MEL15CaptureSet.ps1') @parameters
}
if(-not $PrintOnly){Write-Host "Completed $($Jobs.Count) matrix jobs, $($Jobs.Count*4) cuts; prefix $TagPrefix."}
