param([switch]$Apply)
$ErrorActionPreference='Stop'
$canonicalRoot=Split-Path -Parent $PSScriptRoot
$canonicalRules=Join-Path $canonicalRoot 'AGENTS.md'
if(!(Test-Path -LiteralPath $canonicalRules)){throw 'Create the canonical project rules first.'}
$globalInstructions='C:/Users/Daniel Pang/.codex/AGENTS.md'
$worktrees=@(git -C $canonicalRoot worktree list --porcelain | Where-Object { $_.StartsWith('worktree ') } | ForEach-Object { $_.Substring(9) } | Where-Object { [IO.Path]::GetFullPath($_).TrimEnd('\') -ne [IO.Path]::GetFullPath($canonicalRoot).TrimEnd('\') })
$marker='<!-- MCL-PROJECT-RULES -->'
$endMarker='<!-- /MCL-PROJECT-RULES -->'
$block=@"
$marker
## MeleeCombatLab project rule entry
When working on MeleeCombatLab (a checkout containing MeleeCombatLab.uproject), read the canonical project rules at $canonicalRules and Docs/DEVELOPMENT.md beside them before acting. Policy MCL-DEV-2026-09-08 applies to every project thread and agent, including existing/new worktrees. Include the absolute rules path in every delegation and require recipients to read it. These project rules supersede older project handoff validation prescriptions. On another host use the repository's AGENTS.md; if absent, obtain the project rules before implementation. This section applies only to this project and leaves the general instructions above unchanged.
$endMarker
"@
$targets=@($globalInstructions)
foreach($worktree in $worktrees){
    if(Test-Path -LiteralPath (Join-Path $worktree 'MeleeCombatLab.uproject')){
        $targets+=Join-Path ([IO.Path]::GetFullPath($worktree)) 'AGENTS.md'
    }
}
$results=@()
foreach($target in $targets){
    $old=if(Test-Path -LiteralPath $target){[IO.File]::ReadAllText($target)}else{''}
    $pattern=[regex]::Escape($marker)+'[\s\S]*?'+[regex]::Escape($endMarker)
    $updated=if($old.Contains($marker)){[regex]::Replace($old,$pattern,[System.Text.RegularExpressions.MatchEvaluator]{param($match) $block})}else{$old.TrimEnd()+"`r`n`r`n"+$block+"`r`n"}
    if($Apply -and $updated -cne $old){[IO.File]::WriteAllText($target,$updated,[Text.UTF8Encoding]::new($false))}
    $results+=@{path=$target;changed=($updated -cne $old);applied=[bool]$Apply}
}
$results | ConvertTo-Json
