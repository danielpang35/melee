param(
    [ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Revision='Block05',
    [ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Take='v001',
    [ValidatePattern('^[A-Za-z0-9_-]+$')][string]$BaselineTag='TP_baseline_fp_v001')
$ErrorActionPreference='Stop'
$proofRoot=Split-Path -Parent $PSScriptRoot
$baseline=Get-Content -Raw -LiteralPath (Join-Path $proofRoot "Saved/MEL15/$BaselineTag/verification.json")|ConvertFrom-Json
if(!$baseline.launch.baseline){throw 'The control must be a verified baseline capture.'}
$fpPath=Join-Path $proofRoot 'Config/EXPreview.json'
$fpSelection=Get-Content -Raw -LiteralPath $fpPath|ConvertFrom-Json|ConvertTo-Json -Depth 20 -Compress
$baselineFp=$baseline.launch.fp_selection|ConvertTo-Json -Depth 20 -Compress
if($fpSelection -cne $baselineFp){throw 'First-person selection differs from the verified baseline.'}
$fpHash=(Get-FileHash -Algorithm SHA256 -LiteralPath $fpPath).Hash
$tpPath=Join-Path $proofRoot 'Saved/TPProof/selection.json'
$tpHash=(Get-FileHash -Algorithm SHA256 -LiteralPath $tpPath).Hash
$currentModule=(Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $proofRoot 'Binaries/Win64/UnrealEditor-MeleeCombatLab.dll')).Hash
if($baseline.launch.module_sha256 -ne $currentModule){throw 'Build differs from verified control; capture a fresh baseline first.'}
$cases=@(@{Suffix='external';View='external'},@{Suffix='fp';View='firstperson'},@{Suffix='defender';View='defender'})
foreach($case in $cases){
    $proofTag='TP_'+$Revision.ToLowerInvariant()+'_'+$case.Suffix+'_'+$Take
    if(Test-Path -LiteralPath (Join-Path $proofRoot "Saved/MEL15/$proofTag")){throw "Capture exists: $proofTag. Choose a fresh take."}
}
foreach($case in $cases){
    $proofTag='TP_'+$Revision.ToLowerInvariant()+'_'+$case.Suffix+'_'+$Take
    if((Get-FileHash -LiteralPath $tpPath).Hash -ne $tpHash -or (Get-FileHash -LiteralPath $fpPath).Hash -ne $fpHash){throw 'Animation selection changed during proof.'}
    & (Join-Path $PSScriptRoot 'CaptureThirdPersonProof.ps1') -Tag $proofTag -View $case.View
    $launch=Get-Content -Raw -LiteralPath (Join-Path $proofRoot "Saved/MEL15/$proofTag-launch.json")|ConvertFrom-Json
    if($launch.tp_selection_sha256 -ne $tpHash -or ($launch.fp_selection|ConvertTo-Json -Depth 20 -Compress) -cne $baselineFp){throw 'Capture selection differs from the pinned proof.'}
    Wait-Process -Id $launch.pid -ErrorAction SilentlyContinue
    if((Get-FileHash -LiteralPath $tpPath).Hash -ne $tpHash -or (Get-FileHash -LiteralPath $fpPath).Hash -ne $fpHash){throw 'Animation selection changed during capture.'}
    & python (Join-Path $PSScriptRoot 'VerifyThirdPersonProof.py') $proofTag --compare $BaselineTag
    if($LASTEXITCODE -ne 0){throw "Proof failed: $proofTag"}
}
& python (Join-Path $PSScriptRoot 'PackageThirdPersonProof.py') --revision $Revision --take $Take
if($LASTEXITCODE -ne 0){throw 'Review video assembly failed.'}
