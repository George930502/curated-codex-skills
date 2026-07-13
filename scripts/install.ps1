[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$source = Join-Path $repoRoot 'skills'
$destination = Join-Path (Join-Path $HOME '.agents') 'skills'

New-Item -ItemType Directory -Force -Path $destination | Out-Null

$skills = @(Get-ChildItem -LiteralPath $source -Directory -Force)
foreach ($skill in $skills) {
    Copy-Item -LiteralPath $skill.FullName -Destination $destination -Recurse -Force
}

Write-Output ("Installed {0} skills into {1}" -f $skills.Count, $destination)
