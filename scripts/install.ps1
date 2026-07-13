[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$source = Join-Path $repoRoot 'skills'
$destination = Join-Path $codexHome 'skills'

New-Item -ItemType Directory -Force -Path $destination | Out-Null

$skills = @(Get-ChildItem -LiteralPath $source -Directory -Force)
foreach ($skill in $skills) {
    Copy-Item -LiteralPath $skill.FullName -Destination $destination -Recurse -Force
}

Write-Output ("Installed {0} skills into {1}" -f $skills.Count, $destination)
