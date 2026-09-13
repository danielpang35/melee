param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Tag,
    [ValidateSet('front','side','rear3q','defender','firstperson','legacy')][string]$Camera='side',
    [ValidateSet('standing','moving','crouch')][string]$Pose='standing',
    [ValidateRange(-85,85)][double]$Pitch=0,
    [ValidateRange(0,2)][double]$LeadIn=0.2,
    [ValidateRange(15,120)][int]$Fps=30,
    [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',
    [switch]$SkipUbtSdkSetup,
    [switch]$NeutralMaterial,
    [switch]$Wait,
    [switch]$PassThru,
    [switch]$PrintOnly
)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$project=Join-Path $projectRoot 'MeleeCombatLab.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$captureRoot=Join-Path $projectRoot ('Saved\ArmRepair\'+$Tag)
if(Test-Path -LiteralPath $captureRoot){throw "Capture tag already exists; choose a new tag: $captureRoot"}
$culture=[System.Globalization.CultureInfo]::InvariantCulture
$arguments=@(('"'+$project+'"'),'/Engine/Maps/Entry','-game','-windowed','-ResX=1280','-ResY=720','-ForceRes','-nosplash','-unattended',('-log='+$Tag+'.log'),
    '-CombatPlaytest','-CombatPlaytestQuit','-MotionReview','-AllMotionFrames','-ArmPoseAudit','-MotionReviewKeys','-MotionReviewSet=core',
    ('-ArmReviewTag='+$Tag),('-MotionReviewPose='+$Pose),
    ('-MotionReviewPitch='+$Pitch.ToString($culture)),('-MotionReviewLeadIn='+$LeadIn.ToString($culture)),
    '-UseFixedTimeStep',('-FPS='+$Fps),'-LabProfile=Competitive')
# Omit the camera override to match preserved baseline inspection footage.
if($Camera -ne 'legacy'){$arguments+=('-MotionReviewCamera='+$Camera)}
if($NeutralMaterial){$arguments+='-NeutralArmMaterial'}
if($PrintOnly){Write-Output ('"'+$editor+'" '+($arguments -join ' '));return}
$priorSkipSdk=$env:UE_SKIP_UBT_SDK_SETUP
try {
    if($SkipUbtSdkSetup){$env:UE_SKIP_UBT_SDK_SETUP='1'}
    $process=Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
} finally {
    if($null -eq $priorSkipSdk){Remove-Item Env:UE_SKIP_UBT_SDK_SETUP -ErrorAction SilentlyContinue}
    else {$env:UE_SKIP_UBT_SDK_SETUP=$priorSkipSdk}
}
Write-Host "MEL-15 four-cut review PID: $($process.Id); capture: $captureRoot"
if($Wait){
    # Observe only the instance launched above. Never enumerate or terminate
    # the user's editor or other Unreal processes.
    while(-not $process.WaitForExit(15000)){Write-Host "Waiting for $Tag (PID $($process.Id))"}
    $process.Refresh()
    if($process.ExitCode -ne 0){throw "Review $Tag exited with code $($process.ExitCode); inspect Saved/Logs/$Tag.log"}
    $resultFile=Join-Path $captureRoot 'results.json'
    if(-not (Test-Path -LiteralPath $resultFile)){throw "Review exited without results.json: $captureRoot"}
    $results=(Get-Content -LiteralPath $resultFile -Raw | ConvertFrom-Json).results
    $expected=@('air_external_right','air_external_upper_right','air_external_upper_left','air_external_left')
    if(@($results).Count -ne 4 -or (($results.scenario -join ',') -ne ($expected -join ','))){throw "Review did not run precisely scenarios45 through48: $captureRoot"}
    $failed=@($results | Where-Object { -not $_.passed })
    if($failed.Count -gt 0){Write-Warning "$Tag captured all four cuts but has regression failures: $($failed.scenario -join ', ')"}
    Write-Host "Completed $Tag; four cuts captured."
}
if($PassThru){Write-Output $process}
