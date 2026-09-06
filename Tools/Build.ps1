param([string]$EngineRoot,[switch]$Launch,[switch]$Automation)
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
& (Join-Path $EngineRoot 'Engine\Build\BatchFiles\Build.bat') MeleeCombatLabEditor Win64 Development "-Project=$projectFile" -WaitMutex -NoHotReloadFromIDE
if ($LASTEXITCODE -ne 0) { throw "Unreal editor target build failed (exit $LASTEXITCODE)." }
if ($Automation) {
    & (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe') $projectFile -unattended -nop4 -NullRHI '-ExecCmds=Automation RunTests MeleeCombatLab;Quit' '-TestExit=Automation Test Queue Empty' "-ReportExportPath=$projectRoot\Saved\Automation"
    if ($LASTEXITCODE -ne 0) { throw 'Unreal automation process failed; inspect Saved/Automation and Saved/Logs.' }
}
if ($Launch) {
    Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList @(('"'+$projectFile+'"'),'/Engine/Maps/Entry','-game','-windowed','-ResX=1600','-ResY=900','-log') -WindowStyle Hidden
}
