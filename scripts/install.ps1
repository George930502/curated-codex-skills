[CmdletBinding()]
param(
    [string]$Destination = (Join-Path (Join-Path $HOME '.agents') 'skills')
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$source = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'skills'))
$destination = $Destination

New-Item -ItemType Directory -Force -Path $destination | Out-Null
$destination = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $destination).Path)
if ($destination -eq [System.IO.Path]::GetPathRoot($destination)) {
    throw 'Refusing to install skills into the filesystem root.'
}
$current = [System.IO.Path]::GetPathRoot($destination)
foreach ($segment in $destination.Substring($current.Length) -split '[\\/]') {
    if (-not $segment) {
        continue
    }
    $current = Join-Path $current $segment
    if ((Get-Item -LiteralPath $current -Force).Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        throw 'Refusing to install through a filesystem alias.'
    }
}
$sourcePrefix = $source + [System.IO.Path]::DirectorySeparatorChar
if ([System.String]::Equals($destination, $source, [System.StringComparison]::OrdinalIgnoreCase) -or
    $destination.StartsWith($sourcePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Refusing to install into the packaged source catalog.'
}

$skills = @(Get-ChildItem -LiteralPath $source -Directory)
foreach ($skill in $skills) {
    $target = Join-Path $destination $skill.Name
    if (Test-Path -LiteralPath $target) {
        $item = Get-Item -LiteralPath $target -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            if ($item.PSIsContainer) {
                [System.IO.Directory]::Delete($item.FullName)
            } else {
                [System.IO.File]::Delete($item.FullName)
            }
        } else {
            Remove-Item -LiteralPath $target -Recurse -Force
        }
    }
    Copy-Item -LiteralPath $skill.FullName -Destination $destination -Recurse -Force
}

Write-Output ("Installed {0} skills into {1}" -f $skills.Count, $destination)

$feature = 'default_mode_request_user_input'
$codex = Get-Command codex -ErrorAction SilentlyContinue
if (-not $codex) {
    Write-Warning "Codex CLI was not found. Install or update Codex, then enable $feature."
    Write-Output "PowerShell: codex features enable $feature"
} else {
    $featureOutput = @(& codex features list 2>$null)
    if ($codex.CommandType -eq 'Application' -and $LASTEXITCODE -ne 0) {
        Write-Warning 'Codex feature inspection failed. Run "codex features list" and resolve the error before using native approval.'
    } else {
        $featureLine = $featureOutput |
            Where-Object { $_ -match "^$([regex]::Escape($feature))\s" } |
            Select-Object -First 1

        if (-not $featureLine) {
            Write-Warning "This Codex version does not list $feature. Update Codex before using native approval."
        } else {
            $featureState = ($featureLine -split '\s+')[-1]
            if ($featureState -eq 'true') {
                Write-Output "$feature is enabled."
            } elseif ($featureState -eq 'false') {
                Write-Warning "$feature is disabled; prompt alignment will be blocked in Default mode."
                Write-Output "PowerShell: codex features enable $feature"
                Write-Output 'Then fully close Codex and start a new session.'
            } else {
                Write-Warning "Codex reported an unrecognized state for $feature. Update Codex before using native approval."
            }
        }
    }
}

Write-Output 'Codex detects skill changes automatically; restart it if the skills do not appear.'
