# Requires the preserved disposable skeletal package copied from the prior reload proof.
param([ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Tag='EX_gameplay_reload')
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$selection=Join-Path $root 'Config/EXPreview.json'
$candidatePath=Join-Path $root 'Content/EXPreview/ReloadTest/EX_ReloadCandidate.uasset'
if(!(Test-Path -LiteralPath $candidatePath)){throw 'The disposable EX_ReloadCandidate package is required; do not alter the approved package.'}
$original=[IO.File]::ReadAllBytes($selection)
$candidate=[Text.Encoding]::UTF8.GetString($original) | ConvertFrom-Json
$candidate.revision='UNAPPROVED-production-reload-root-offset-10cm'
$candidate.assets[0].animation='/Game/EXPreview/ReloadTest/EX_ReloadCandidate.EX_ReloadCandidate'
$candidate.animation_package_sha256=(Get-FileHash -LiteralPath $candidatePath).Hash
$launch=$null
$log=Join-Path $root ('Saved/MEL15/'+$Tag+'.log')
$out=Join-Path $root ('Saved/MEL15/'+$Tag)
function Wait-Frame([int]$number){
    $path=Join-Path $out ('frames/{0:d4}.png' -f $number)
    $deadline=[DateTime]::UtcNow.AddMinutes(3)
    while(!(Test-Path -LiteralPath $path)){
        if($launch -and !(Get-Process -Id $launch.pid -ErrorAction SilentlyContinue)){throw 'Replay exited before reload checkpoint.'}
        if([DateTime]::UtcNow -gt $deadline){throw "No capture frame $number"}
        Start-Sleep -Seconds 2
    }
}
try {
    & (Join-Path $PSScriptRoot 'PlayGameplay.ps1') -Capture -Tag $Tag
    $launch=Get-Content -Raw -LiteralPath (Join-Path $root ('Saved/MEL15/'+$Tag+'-launch.json')) | ConvertFrom-Json
    Wait-Frame 30
    $candidate | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $selection
    # Player finishes the immutable first attack before accepting the edit.
    Wait-Frame 172
    $text=Get-Content -Raw -LiteralPath $log
    if(([regex]::Matches($text,'selected=UNAPPROVED-production-reload-root-offset-10cm')).Count -ne 3){throw 'All three production actors did not select the disposable package at rest.'}
    [IO.File]::WriteAllBytes($selection,$original)
    Wait-Frame 335
    $text=Get-Content -Raw -LiteralPath $log
    $approved=([Text.Encoding]::UTF8.GetString($original) | ConvertFrom-Json).revision
    if(([regex]::Matches($text,'selected='+[regex]::Escape($approved))).Count -ne 6){throw 'Approved package was not restored in all three actors.'}
    $after=(Get-FileHash -LiteralPath (Join-Path $root 'Binaries/Win64/UnrealEditor-MeleeCombatLab.dll')).Hash
    if($after -ne $launch.module_sha256){throw 'Build changed during reload test.'}
    @{pid=$launch.pid;same_process=$true;module_sha256=$after;recompiled=$false;restored=$true;
        candidate=$candidate;scope='Production idle-boundary selection/replay of a newly named skeletal package; not in-place reimport or artistic acceptance'} |
        ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $out 'reload-verification.json')
} finally {
    [IO.File]::WriteAllBytes($selection,$original)
    if($launch){$process=Get-Process -Id $launch.pid -ErrorAction SilentlyContinue;if($process -and $process.ProcessName -eq 'UnrealEditor'){Stop-Process -Id $launch.pid}}
}
