[CmdletBinding()]
param(
    [string]$Destination = (Join-Path (Join-Path $HOME '.agents') 'skills')
)

$ErrorActionPreference = 'Stop'

function Test-SubstDrive {
    param([string]$Path)

    $commandPath = Join-Path $env:SystemRoot 'System32\subst.exe'
    if (-not (Test-Path -LiteralPath $commandPath -PathType Leaf)) {
        throw 'Cannot inspect Windows substituted drives without subst.exe.'
    }
    $prefix = [System.IO.Path]::GetPathRoot($Path) + ': =>'
    $LASTEXITCODE = 0
    $output = @(& $commandPath)
    if (-not $? -or $LASTEXITCODE -ne 0) {
        throw 'Windows substituted-drive inspection failed.'
    }
    foreach ($line in $output) {
        if ($line.TrimStart().StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

function Resolve-UnaliasedDirectory {
    param([string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Path).Path)
    if (Test-SubstDrive $fullPath) {
        throw 'Refusing to install through a filesystem alias.'
    }
    $current = [System.IO.Path]::GetPathRoot($fullPath)
    foreach ($segment in $fullPath.Substring($current.Length) -split '[\\/]') {
        if (-not $segment) {
            continue
        }
        $current = Join-Path $current $segment
        if ((Get-Item -LiteralPath $current -Force).Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            throw 'Refusing to install through a filesystem alias.'
        }
    }
    return $fullPath
}

function Remove-Entry {
    param([string]$Path)

    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if (-not $item) {
        return
    }
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        if ($item.PSIsContainer) {
            [System.IO.Directory]::Delete($item.FullName)
        } else {
            [System.IO.File]::Delete($item.FullName)
        }
    } elseif ($item.PSIsContainer) {
        foreach ($child in @(Get-ChildItem -LiteralPath $item.FullName -Force)) {
            Remove-Entry $child.FullName
        }
        [System.IO.Directory]::Delete($item.FullName)
    } else {
        $item.Attributes = [System.IO.FileAttributes]::Normal
        [System.IO.File]::Delete($item.FullName)
    }
}

function Test-PathAtOrBelow {
    param([string]$Path, [string]$Root)

    $prefix = $Root + [System.IO.Path]::DirectorySeparatorChar
    return [System.String]::Equals($Path, $Root, [System.StringComparison]::OrdinalIgnoreCase) -or
        $Path.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
}

$repoRoot = Resolve-UnaliasedDirectory (Join-Path $PSScriptRoot '..')
$source = Resolve-UnaliasedDirectory (Join-Path $repoRoot 'skills')
if (@($Destination -split '[\\/]' | Where-Object { $_ -eq '..' }).Count -gt 0) {
    throw 'Refusing to install through an unresolved parent segment.'
}
$requested = [System.IO.Path]::GetFullPath($Destination)

if ($requested -eq [System.IO.Path]::GetPathRoot($requested)) {
    throw 'Refusing to install skills into the filesystem root.'
}
$existing = $requested
while (-not (Test-Path -LiteralPath $existing -PathType Container)) {
    $parent = [System.IO.Directory]::GetParent($existing)
    if (-not $parent -or $parent.FullName -eq $existing) {
        throw "Cannot resolve an existing parent for $requested."
    }
    $existing = $parent.FullName
}
$existing = Resolve-UnaliasedDirectory $existing
if (Test-PathAtOrBelow $existing $source) {
    throw 'Refusing to install into the packaged source catalog.'
}

New-Item -ItemType Directory -Force -Path $requested | Out-Null
$destination = Resolve-UnaliasedDirectory $requested
if (Test-PathAtOrBelow $destination $source) {
    throw 'Refusing to install into the packaged source catalog.'
}

$skills = @(Get-ChildItem -LiteralPath $source -Directory)
$recoveryPlans = @{}
foreach ($skill in $skills) {
    $target = Join-Path $destination $skill.Name
    $validTransactions = @()
    $backupTransactions = @()
    foreach ($staleTransaction in @(Get-ChildItem -LiteralPath $destination -Directory -Force -Filter ('.{0}.install.*' -f $skill.Name))) {
        $marker = Join-Path $staleTransaction.FullName '.curated-codex-skills-transaction'
        if ($staleTransaction.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            throw 'Refusing to recover through a transaction filesystem alias.'
        }
        if (-not (Test-Path -LiteralPath $marker -PathType Leaf)) {
            continue
        }
        $markerContent = [System.IO.File]::ReadAllText($marker)
        if ($markerContent -ne ($skill.Name + "`n") -and $markerContent -ne ($skill.Name + "`r`n")) {
            continue
        }
        $validTransactions += $staleTransaction
        $staleBackup = Join-Path $staleTransaction.FullName 'old'
        if ($null -ne (Get-Item -LiteralPath $staleBackup -Force -ErrorAction SilentlyContinue)) {
            $backupTransactions += $staleTransaction
        }
    }
    $targetExists = $null -ne (Get-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue)
    if (-not $targetExists -and $backupTransactions.Count -gt 1) {
        throw "Multiple interrupted transactions exist for $($skill.Name); refusing ambiguous recovery."
    }
    $recoveryPlans[$skill.Name] = @($validTransactions)
}

foreach ($skill in $skills) {
    $target = Join-Path $destination $skill.Name
    $validTransactions = @($recoveryPlans[$skill.Name])
    foreach ($staleTransaction in $validTransactions) {
        $staleBackup = Join-Path $staleTransaction.FullName 'old'
        $targetExists = $null -ne (Get-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue)
        $backupExists = $null -ne (Get-Item -LiteralPath $staleBackup -Force -ErrorAction SilentlyContinue)
        if (-not $targetExists -and $backupExists) {
            try {
                Move-Item -LiteralPath $staleBackup -Destination $target
            } catch {
                throw "Could not restore interrupted transaction $($staleTransaction.FullName)."
            }
        }
        try {
            Remove-Entry $staleTransaction.FullName
        } catch {
            Write-Warning "Could not remove stale transaction $($staleTransaction.FullName)."
        }
    }
    $transaction = Join-Path $destination ('.{0}.install.{1}' -f $skill.Name, [guid]::NewGuid())
    $staging = Join-Path $transaction 'new'
    $backup = Join-Path $transaction 'old'
    New-Item -ItemType Directory -Path $transaction | Out-Null
    try {
        Set-Content -LiteralPath (Join-Path $transaction '.curated-codex-skills-transaction') -Value $skill.Name
    } catch {
        Remove-Entry $transaction
        throw
    }
    try {
        Copy-Item -LiteralPath $skill.FullName -Destination $staging -Recurse -Force
    } catch {
        Remove-Entry $transaction
        throw
    }

    $hadTarget = $null -ne (Get-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue)
    if ($hadTarget) {
        try {
            Move-Item -LiteralPath $target -Destination $backup
        } catch {
            Remove-Entry $transaction
            throw
        }
    }
    try {
        Move-Item -LiteralPath $staging -Destination $target
    } catch {
        if ($hadTarget) {
            try {
                Move-Item -LiteralPath $backup -Destination $target
            } catch {
                throw "Install failed; rollback is preserved at $backup."
            }
        }
        Remove-Entry $transaction
        throw
    }
    try {
        Remove-Entry $transaction
    } catch {
        Write-Warning "Installed $($skill.Name), but could not remove transaction $transaction."
    }
}

Write-Output ("Installed {0} skills into {1}" -f $skills.Count, $destination)

$feature = 'default_mode_request_user_input'
$codex = Get-Command codex -ErrorAction SilentlyContinue
if (-not $codex) {
    Write-Warning "Codex CLI was not found. Install or update Codex, then enable $feature."
    Write-Output "PowerShell: codex features enable $feature"
} else {
    $featureSucceeded = $false
    try {
        $LASTEXITCODE = 0
        $featureOutput = @(& codex features list 2>$null)
        $featureSucceeded = $? -and $LASTEXITCODE -eq 0
    } catch {
        $featureOutput = @()
    }
    if (-not $featureSucceeded) {
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
