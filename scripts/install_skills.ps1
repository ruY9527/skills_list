[CmdletBinding()]
param(
    [switch]$All,
    [string[]]$Category = @(),
    [string[]]$Skill = @(),
    [string]$Target = (Join-Path $HOME ".codex\skills"),
    [switch]$List
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$SkillsRoot = Join-Path $RepoRoot "skills"
if (-not (Test-Path -LiteralPath $SkillsRoot -PathType Container)) {
    throw "Skills directory not found: $SkillsRoot"
}

$Catalog = @(
    foreach ($CategoryDirectory in Get-ChildItem -LiteralPath $SkillsRoot -Directory | Sort-Object Name) {
        foreach ($SkillDirectory in Get-ChildItem -LiteralPath $CategoryDirectory.FullName -Directory | Sort-Object Name) {
            if (-not (Test-Path -LiteralPath (Join-Path $SkillDirectory.FullName "SKILL.md") -PathType Leaf)) {
                continue
            }
            if ($CategoryDirectory.Name -notmatch '^[a-z0-9-]+$' -or $SkillDirectory.Name -notmatch '^[a-z0-9-]+$') {
                throw "Invalid category or skill directory name: $($SkillDirectory.FullName)"
            }
            [pscustomobject]@{
                Category = $CategoryDirectory.Name
                Id       = $SkillDirectory.Name
                Path     = $SkillDirectory.FullName
            }
        }
    }
)

if ($Catalog.Count -eq 0) {
    throw "No skills found under $SkillsRoot"
}

$SeenIds = @{}
foreach ($Item in $Catalog) {
    if ($SeenIds.ContainsKey($Item.Id)) {
        throw "Duplicate skill id '$($Item.Id)' across categories; flat installation would be ambiguous."
    }
    $SeenIds[$Item.Id] = $true
}

if ($List) {
    foreach ($CategoryName in ($Catalog.Category | Sort-Object -Unique)) {
        $Items = @($Catalog | Where-Object Category -eq $CategoryName)
        Write-Output "$CategoryName ($($Items.Count))"
        foreach ($Item in $Items) {
            Write-Output "  - $($Item.Id)"
        }
    }
    Write-Output "Total: $($Catalog.Count) skills"
    exit 0
}

if (-not $All -and $Category.Count -eq 0 -and $Skill.Count -eq 0) {
    throw "Choose -All, -Category <cat>, or -Skill <id>; use -List to inspect the catalog."
}
if ($All -and ($Category.Count -gt 0 -or $Skill.Count -gt 0)) {
    throw "-All cannot be combined with -Category or -Skill."
}

$Selected = @(
    $Catalog | Where-Object {
        $All -or ($Category.Count -gt 0 -and $Category -contains $_.Category) -or
            ($Skill.Count -gt 0 -and $Skill -contains $_.Id)
    }
)
if ($Selected.Count -eq 0) {
    throw "No catalog entries matched the requested category or skill."
}

foreach ($RequestedCategory in $Category) {
    if ($RequestedCategory -notin $Catalog.Category) {
        throw "Unknown category: $RequestedCategory"
    }
}
foreach ($RequestedSkill in $Skill) {
    if ($RequestedSkill -notin $Catalog.Id) {
        throw "Unknown skill: $RequestedSkill"
    }
}

$TargetRoot = [System.IO.Path]::GetFullPath($Target)
if (Test-Path -LiteralPath $TargetRoot -PathType Leaf) {
    throw "Target is a file, not a directory: $TargetRoot"
}
New-Item -ItemType Directory -Path $TargetRoot -Force | Out-Null
$TargetRoot = (Resolve-Path -LiteralPath $TargetRoot).Path

foreach ($Item in $Selected) {
    $Source = $Item.Path
    $Destination = Join-Path $TargetRoot $Item.Id
    if (Test-Path -LiteralPath $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null

    $Files = Get-ChildItem -LiteralPath $Source -Recurse -Force -File
    foreach ($File in $Files) {
        $Relative = $File.FullName.Substring($Source.Length).TrimStart('\', '/')
        if ($Relative -match '(^|[\\/])__pycache__([\\/]|$)' -or $File.Name -like '*.pyc') {
            continue
        }
        $DestinationFile = Join-Path $Destination $Relative
        $DestinationParent = Split-Path -Parent $DestinationFile
        New-Item -ItemType Directory -Path $DestinationParent -Force | Out-Null
        Copy-Item -LiteralPath $File.FullName -Destination $DestinationFile -Force
    }

    # Remove only the exact legacy underscore spelling of a migrated skill.
    if ($Item.Id.EndsWith('-codex')) {
        $LegacyId = $Item.Id.Substring(0, $Item.Id.Length - 6) + '_codex'
        $LegacyDestination = Join-Path $TargetRoot $LegacyId
        if (Test-Path -LiteralPath $LegacyDestination) {
            Remove-Item -LiteralPath $LegacyDestination -Recurse -Force
        }
    }
    Write-Output "Installed $($Item.Id) -> $Destination"
}

Write-Output "Installed $($Selected.Count) skill(s) into $TargetRoot"
Write-Output "Restart Codex to load the refreshed skills."
