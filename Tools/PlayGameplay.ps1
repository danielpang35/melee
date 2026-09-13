param([string]$EngineRoot='C:/Program Files/Epic Games/UE_5.8',
    [switch]$Capture,[ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Tag='EX_gameplay',
    [ValidateSet('firstperson','external','defender')][string]$View='firstperson')
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$out=Join-Path $root ('Saved/MEL15/'+$Tag)
if($Capture -and (Test-Path -LiteralPath $out)){throw 'Capture exists; select a fresh -Tag.'}
if(!(Test-Path -LiteralPath (Join-Path $root 'Binaries/Win64/UnrealEditor-MeleeCombatLab.dll'))){throw 'Build the delivery checkout with Tools/Build.ps1 first.'}
$arguments=@(('"'+$root+'/MeleeCombatLab.uproject"'),'/Engine/Maps/Entry',
    '-game','-windowed','-nosplash',('-abslog="'+$root+'/Saved/MEL15/'+$Tag+'.log"'))
if($Capture){$arguments+=@('-ResX=640','-ResY=360','-ForceRes','-RenderOffscreen','-unattended','-usefixedtimestep','-fps=60',('-EXGameplayCapture='+$Tag),('-EXGameplayView='+$View))}
else{$arguments+=@('-ResX=1280','-ResY=720')}
$style=if($Capture){'Hidden'}else{'Normal'}
$process=Start-Process (Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.exe') -ArgumentList $arguments -WindowStyle $style -PassThru
$receipt=@{pid=$process.Id;tag=$Tag;capture=[bool]$Capture;view=$View;arguments=$arguments;
    module_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root 'Binaries/Win64/UnrealEditor-MeleeCombatLab.dll')).Hash;
    selection=(Get-Content -Raw -LiteralPath (Join-Path $root 'Config/EXPreview.json') | ConvertFrom-Json)}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $root ('Saved/MEL15/'+$Tag+'-launch.json'))
Write-Output "Gameplay PID $($process.Id). WASD move; mouse aim; LMB directional cut; 1 right horizontal; RMB parry; Q feint; E stab; R reset; F2 opponent pattern; F5 external view."
