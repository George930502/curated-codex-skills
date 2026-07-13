[CmdletBinding()]
param(
    [string]$Destination = (Join-Path (Join-Path $HOME '.agents') 'skills')
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$source = Join-Path $repoRoot 'skills'
$destination = $Destination

New-Item -ItemType Directory -Force -Path $destination | Out-Null

$skills = @(Get-ChildItem -LiteralPath $source -Directory -Force)
foreach ($skill in $skills) {
    Copy-Item -LiteralPath $skill.FullName -Destination $destination -Recurse -Force
}

Write-Output ("Installed {0} skills into {1}" -f $skills.Count, $destination)

$feature = 'default_mode_request_user_input'
$codex = Get-Command codex -ErrorAction SilentlyContinue
if (-not $codex) {
    Write-Warning "Codex CLI was not found. Install or update Codex, then enable $feature."
    Write-Output "PowerShell: codex features enable $feature"
    return
}

$featureLine = @(& codex features list 2>$null) |
    Where-Object { $_ -match "^$([regex]::Escape($feature))\s" } |
    Select-Object -First 1

if (-not $featureLine) {
    Write-Warning "This Codex version does not list $feature. Update Codex before using native approval."
    return
}

if ($featureLine -notmatch '\btrue\s*$') {
    Write-Warning "$feature is disabled; prompt alignment will be blocked in Default mode."
    Write-Output "PowerShell: codex features enable $feature"
    Write-Output 'Then fully close Codex and start a new session.'
} else {
    Write-Output "$feature is enabled."
}
