# Bound compiler concurrency after commit-memory failures; 0 restores automatic selection.
param([string]$EngineRoot,[switch]$Launch,[switch]$Automation,[ValidateRange(0,128)][int]$MaxParallelActions=2,[int]$ModuleSuffix=0,[switch]$NoUBA)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$projectFile=Join-Path $projectRoot 'MeleeCombatLab.uproject'
if (!$EngineRoot) {
    $candidates=@('C:\Epic Games\UE_5.8','C:\Program Files\Epic Games\UE_5.8')
    $EngineRoot=$candidates | Where-Object { Test-Path (Join-Path $_ 'Engine\Build\BatchFiles\Build.bat') } | Select-Object -First 1
}
if (!$EngineRoot) { throw 'UE 5.8 not installed yet. Pass -EngineRoot with the UE_5.8 folder after installation completes.' }
$version=Get-Content (Join-Path $EngineRoot 'Engine\Build\Build.version') -Raw | ConvertFrom-Json
if ($version.MajorVersion -ne 5 -or $version.MinorVersion -ne 8) { throw 'This project requires Unreal Engine 5.8.' }
$ubt = Join-Path $EngineRoot 'Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll'

$dotnet = Get-ChildItem `
    (Join-Path $EngineRoot 'Engine\Binaries\ThirdParty\DotNet') `
    -Filter 'dotnet.exe' `
    -Recurse |
    Select-Object -First 1 -ExpandProperty FullName

if (!$dotnet) {
    throw 'Could not locate Unreal Engine bundled dotnet.exe.'
}

if (!(Test-Path $ubt)) {
    throw "Could not locate UnrealBuildTool.dll at $ubt"
}

$extraBuildArgs=@()
# UBT may delete any hot-reload output, including suffixed modules. Never
# launch a build that is already known to fail, or terminate an editor session.
$moduleDir=Join-Path $projectRoot 'Binaries/Win64'
$locked=@()
foreach($module in Get-ChildItem -LiteralPath $moduleDir -Filter 'UnrealEditor-MeleeCombatLab*.dll' -ErrorAction SilentlyContinue){
    try {
        $probe=[System.IO.File]::Open($module.FullName,[System.IO.FileMode]::Open,[System.IO.FileAccess]::ReadWrite,[System.IO.FileShare]::None)
        $probe.Dispose()
    } catch [System.IO.IOException] { $locked+=$module.FullName }
}
if($locked.Count){
    $owners=@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue | ForEach-Object {
        $process=$_
        try {$process.Modules | Where-Object {$locked -contains $_.FileName} | ForEach-Object {"PID $($process.Id): $($_.FileName)"}} catch {}
    })
    throw ("Build blocked by loaded/locked gameplay modules. Save and close the matching Unreal session, then rerun Tools/Build.ps1. A fresh suffix cannot bypass UBT cleanup. No process was closed.`n"+($owners+$locked -join "`n"))
}
if ($MaxParallelActions -gt 0) { $extraBuildArgs += "-MaxParallelActions=$MaxParallelActions" }
if ($NoUBA) { $extraBuildArgs += '-NoUBA' }
if ($ModuleSuffix -gt 0) { $extraBuildArgs += "-ModuleWithSuffix=MeleeCombatLab,$ModuleSuffix" }
& $dotnet $ubt `
    MeleeCombatLabEditor `
    Win64 `
    Development `
    "-Project=$projectFile" `
    -WaitMutex `
    -NoHotReloadFromIDE @extraBuildArgs

if ($LASTEXITCODE -ne 0) {
    throw "Unreal editor target build failed (exit $LASTEXITCODE)."
}
if ($Automation) {
    & (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe') $projectFile -unattended -nop4 -NullRHI '-ExecCmds=Automation RunTests MeleeCombatLab' '-TestExit=Automation Test Queue Empty' "-ReportExportPath=$projectRoot\Saved\Automation"
    if ($LASTEXITCODE -ne 0) { throw 'Unreal automation process failed; inspect Saved/Automation and Saved/Logs.' }
}
if ($Launch) {
    Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList @(('"'+$projectFile+'"'),'/Engine/Maps/Entry','-game','-windowed','-ResX=1600','-ResY=900','-log') -WindowStyle Hidden
}
