param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Tag,
    [ValidateRange(38,55)][int]$Scenario=45,
    [ValidateSet('front','side','rear3q','defender','firstperson','legacy')][string]$Camera='side',
    [ValidateSet('standing','moving','crouch')][string]$Pose='standing',
    [ValidateSet('miss','body','parry','wall')][string]$Outcome='miss',
    [ValidateSet('combo','riposte','parry')][string]$Sequence,
    [ValidateRange(-85,85)][double]$Pitch=0,
    [ValidateRange(0,2)][double]$LeadIn=0.2,
    [double]$Angle,
    [ValidateRange(15,120)][int]$Fps=30,
    [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',
    [switch]$Neutral,
    [switch]$NeutralMaterial,
    [switch]$LegacyPerformance,
    [switch]$CascadeurPreview,
    [switch]$CascadeurLoop,
    [switch]$StayOpen,
    [switch]$SkipUbtSdkSetup,
    [switch]$Wait,
    [switch]$PassThru,
    [switch]$PrintOnly
)
$ErrorActionPreference='Stop'
if($Neutral -and $PSBoundParameters.ContainsKey('Outcome')){throw 'An explicit outcome requires an attack; remove -Neutral or omit -Outcome.'}
if($Sequence -and ($Neutral -or $PSBoundParameters.ContainsKey('Outcome'))){throw '-Sequence requires a separate run without -Neutral or -Outcome.'}
$projectRoot=Split-Path -Parent $PSScriptRoot
$project=Join-Path $projectRoot 'MeleeCombatLab.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$captureRoot=Join-Path $projectRoot ('Saved\ArmRepair\'+$Tag)
if(Test-Path -LiteralPath $captureRoot){throw "Capture tag already exists; choose a new tag: $captureRoot"}
$culture=[System.Globalization.CultureInfo]::InvariantCulture
$arguments=@(('"'+$project+'"'),'/Engine/Maps/Entry','-game','-windowed','-ResX=1280','-ResY=720','-ForceRes','-nosplash','-unattended',('-log='+$Tag+'.log'),
    '-CombatPlaytest','-CombatPlaytestQuit','-MotionReview','-AllMotionFrames','-ArmPoseAudit','-MotionReviewKeys',
    ('-ArmReviewTag='+$Tag),('-MotionReviewScenario='+$Scenario),
    ('-MotionReviewPose='+$Pose),('-MotionReviewPitch='+$Pitch.ToString($culture)),
    ('-MotionReviewLeadIn='+$LeadIn.ToString($culture)),'-usefixedtimestep',('-fps='+$Fps))
if($Camera -ne 'legacy'){$arguments+=('-MotionReviewCamera='+$Camera)}
if($PSBoundParameters.ContainsKey('Angle')){$arguments+=('-MotionReviewAngle='+$Angle.ToString($culture))}
# Omitted -Outcome retains the existing air-review behavior, including neutral poses.
if($PSBoundParameters.ContainsKey('Outcome')){$arguments+=('-MotionReviewOutcome='+$Outcome)}
if($Neutral){$arguments+='-NeutralPoseReview'}
if($NeutralMaterial){$arguments+='-NeutralArmMaterial'}
if($LegacyPerformance){$arguments+='-LegacyArmPerformance'}
if($CascadeurPreview){$arguments+='-CascadeurPreview'}
if($CascadeurLoop){$arguments+='-CascadeurLoop'}
if($StayOpen){$arguments=@($arguments | Where-Object {$_ -ne '-CombatPlaytestQuit'})}
if($Sequence){$arguments+=('-MotionReviewSequence='+$Sequence)}
if($PrintOnly){
    Write-Output ('"'+$editor+'" '+($arguments -join ' '))
    return
}
$priorSkipSdk=$env:UE_SKIP_UBT_SDK_SETUP
try {
    if($SkipUbtSdkSetup){$env:UE_SKIP_UBT_SDK_SETUP='1'}
    $process=Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
} finally {
    if($null -eq $priorSkipSdk){Remove-Item Env:UE_SKIP_UBT_SDK_SETUP -ErrorAction SilentlyContinue}
    else {$env:UE_SKIP_UBT_SDK_SETUP=$priorSkipSdk}
}
Write-Host "MEL-15 rendered review PID: $($process.Id); capture: $captureRoot"
if($Wait){
    while(-not $process.WaitForExit(15000)){Write-Host "Waiting for $Tag (PID $($process.Id))"}
    $process.Refresh()
    if($process.ExitCode -ne 0){throw "Review $Tag exited with code $($process.ExitCode); inspect Saved/Logs/$Tag.log"}
    $resultFile=Join-Path $captureRoot 'results.json'
    if(-not(Test-Path -LiteralPath $resultFile)){throw "Review exited without results.json: $captureRoot"}
    $results=@((Get-Content -LiteralPath $resultFile -Raw | ConvertFrom-Json).results)
    if($results.Count -ne 1){throw "Review did not produce exactly one scenario: $captureRoot"}
    if(-not $results[0].passed){Write-Warning "$Tag captured but failed regression validation; inspect $resultFile"}
    Write-Host "Completed $Tag."
}
if($PassThru){Write-Output $process}
