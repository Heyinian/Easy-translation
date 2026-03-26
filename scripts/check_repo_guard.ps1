param(
    [switch]$WarnOnly,
    [string]$ApprovalFilePath = ""
)

$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot

if ([string]::IsNullOrWhiteSpace($ApprovalFilePath)) {
    $ApprovalFilePath = Join-Path $repoRoot "docs\approvals\ALLOW_DOC_STRUCTURE_CHANGE.json"
}

$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]
$passes = New-Object System.Collections.Generic.List[string]

function Add-Failure {
    param([string]$Message)
    $failures.Add($Message) | Out-Null
}

function Add-Warning {
    param([string]$Message)
    $warnings.Add($Message) | Out-Null
}

function Add-Pass {
    param([string]$Message)
    $passes.Add($Message) | Out-Null
}

function Test-RequiredPath {
    param([string]$RelativePath)

    $fullPath = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $fullPath)) {
        Add-Failure "Missing required path: $RelativePath"
        return
    }

    Add-Pass "Required path exists: $RelativePath"
}

function Test-DocumentMarkers {
    param(
        [string]$RelativePath,
        [string[]]$Markers
    )

    $fullPath = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $fullPath)) {
        Add-Failure "Missing canonical document: $RelativePath"
        return
    }

    $content = Get-Content -LiteralPath $fullPath -Raw
    foreach ($marker in $Markers) {
        if ($content -notlike "*$marker*") {
            Add-Failure "Canonical document marker missing in $RelativePath : $marker"
        }
    }
}

function Get-StructureChangeApproval {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    try {
        $approval = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        Add-Failure "Structure change approval file is not valid JSON: $Path"
        return $null
    }

    $requiredFields = @("approved", "reason", "approved_by", "requested_by", "scope", "created_on")
    foreach ($field in $requiredFields) {
        if (-not ($approval.PSObject.Properties.Name -contains $field)) {
            Add-Failure "Structure change approval file is missing required field '$field': $Path"
        }
    }

    if ($approval.approved -ne $true) {
        Add-Failure "Structure change approval file exists but approved is not true: $Path"
        return $null
    }

    if ([string]::IsNullOrWhiteSpace([string]$approval.reason)) {
        Add-Failure "Structure change approval file must include a non-empty reason: $Path"
    }

    if ([string]::IsNullOrWhiteSpace([string]$approval.approved_by)) {
        Add-Failure "Structure change approval file must include approved_by: $Path"
    }

    if ([string]::IsNullOrWhiteSpace([string]$approval.requested_by)) {
        Add-Failure "Structure change approval file must include requested_by: $Path"
    }

    if ($approval.scope -eq $null -or @($approval.scope).Count -eq 0) {
        Add-Failure "Structure change approval file must include at least one scope entry: $Path"
    }

    return $approval
}

function Get-GitCommandAvailable {
    return [bool](Get-Command git -ErrorAction SilentlyContinue)
}

function Test-GitHeadExists {
    if (-not (Get-GitCommandAvailable)) {
        return $false
    }

    $escapedRepoRoot = $repoRoot.Replace('"', '""')
    & cmd /c "git -c core.autocrlf=false -c core.safecrlf=false -C ""$escapedRepoRoot"" rev-parse --verify HEAD >nul 2>nul"
    return ($LASTEXITCODE -eq 0)
}

function Get-GitDiffLines {
    if (-not (Get-GitCommandAvailable)) {
        Add-Warning "git was not available; skipping destructive-change detection."
        return @()
    }

    $insideWorkTree = (& git -c core.autocrlf=false -c core.safecrlf=false -C $repoRoot rev-parse --is-inside-work-tree 2>$null)
    if ($LASTEXITCODE -ne 0 -or ($insideWorkTree | Select-Object -First 1) -ne "true") {
        Add-Warning "Repository is not a valid git worktree; skipping destructive-change detection."
        return @()
    }

    if (-not (Test-GitHeadExists)) {
        Add-Warning "Repository does not have a committed HEAD yet; skipping destructive-change detection."
        return @()
    }

    $lines = & git -c core.autocrlf=false -c core.safecrlf=false -C $repoRoot diff --name-status --find-renames=100 HEAD -- 2>$null
    if ($LASTEXITCODE -ne 0) {
        Add-Warning "Unable to query git diff against HEAD; skipping destructive-change detection."
        return @()
    }

    return @($lines | Where-Object { $_ })
}

function Get-BootstrapFinalizationState {
    $projectConfigPath = Join-Path $repoRoot "config\project\current_project.json"
    if (-not (Test-Path -LiteralPath $projectConfigPath)) {
        return $false
    }

    try {
        $projectConfig = Get-Content -LiteralPath $projectConfigPath -Raw | ConvertFrom-Json
    } catch {
        Add-Warning "Unable to parse config/project/current_project.json; treating bootstrap assets as required."
        return $false
    }

    if ($projectConfig.PSObject.Properties.Name -contains "bootstrap_finalized" -and $projectConfig.bootstrap_finalized -eq $true) {
        return $true
    }

    return $false
}

$bootstrapFinalized = Get-BootstrapFinalizationState

$requiredPaths = @(
    ".gitignore",
    "README.md",
    "config",
    "docs",
    "examples",
    "schemas",
    "scripts",
    "src",
    "tests",
    "artifacts",
    ".github\workflows\repo-hygiene.yml",
    "docs\START_HERE.md",
    "docs\current_status.md",
    "docs\backlog.md",
    "docs\roadmap.md",
    "docs\versioning_policy.md",
    "docs\development_guidelines.md",
    "docs\HANDOFF_PROTOCOL.md",
    "docs\archive\README.md",
    "docs\daily\README.md",
    "docs\developer_guide.md",
    "docs\user_manual.md",
    "docs\prompt_templates\README.md",
    "docs\prompt_templates\initialize_current_project.md",
    "docs\prompt_templates\remote_ai_session_start.md",
    "docs\prompt_templates\task_execution_prompt.md",
    "docs\prompt_templates\handoff_resume_prompt.md",
    "docs\execution_contract.md",
    "docs\config_contract.md",
    "docs\guard_profile_contract.md",
    "docs\artifact_contract.md",
    "docs\result_contract.md"
)

if (-not $bootstrapFinalized) {
    $requiredPaths += @(
        "docs\bootstrap_initializer_guide.md",
        "config\project\bootstrap_seed.example.json",
        "scripts\initialize_project_from_skeleton.ps1"
    )
}

$canonicalMarkerMap = @{
    "docs\START_HERE.md" = @("# START_HERE", "docs/current_status.md", "docs/backlog.md", "docs/roadmap.md")
    "docs\current_status.md" = @("## Current Phase", "## Current Working Version", "## Verified Reality")
    "docs\backlog.md" = @("## Priority Overview", "## Item Details")
    "docs\roadmap.md" = @("## Phase Overview", "## Release")
    "docs\versioning_policy.md" = @("## Base Rule", "## Pre-Release Phase Version Rule", "## Post-Release Version Rule")
    "docs\development_guidelines.md" = @("## Incremental Maintenance Rule", "## Repository Hygiene Rule")
    "docs\HANDOFF_PROTOCOL.md" = @("## Before Declaring A Checkpoint Complete", "## Handoff Output Rule")
    "docs\developer_guide.md" = @("## Purpose", "## Structural Rewrite Rule")
    "docs\user_manual.md" = @("## Quick Start", "## Initialization Workflow", "## Troubleshooting")
    "docs\prompt_templates\README.md" = @("## Available Templates", "## Repository Entry Rule")
    "docs\prompt_templates\initialize_current_project.md" = @("# Initialize Current Project Prompt", "Detect repository mode first.", "At the end of the intake round")
}

if (-not $bootstrapFinalized) {
    $canonicalMarkerMap["docs\bootstrap_initializer_guide.md"] = @("## Scope", "## Safety Rule", "## Project-Name Replacement Strategy")
}

foreach ($relativePath in $requiredPaths) {
    Test-RequiredPath -RelativePath $relativePath
}

foreach ($entry in $canonicalMarkerMap.GetEnumerator()) {
    Test-DocumentMarkers -RelativePath $entry.Key -Markers $entry.Value
}

$approval = Get-StructureChangeApproval -Path $ApprovalFilePath
if ($approval) {
    Add-Warning ("Structure change override active: " + $ApprovalFilePath)
}

$protectedPaths = @(
    ".gitignore",
    "README.md",
    "docs/START_HERE.md",
    "docs/current_status.md",
    "docs/backlog.md",
    "docs/roadmap.md",
    "docs/versioning_policy.md",
    "docs/development_guidelines.md",
    "docs/HANDOFF_PROTOCOL.md",
    "docs/archive/README.md",
    "docs/daily/README.md",
    "docs/developer_guide.md",
    "docs/user_manual.md",
    "docs/prompt_templates/README.md",
    "docs/prompt_templates/initialize_current_project.md",
    "docs/prompt_templates/remote_ai_session_start.md",
    "docs/prompt_templates/task_execution_prompt.md",
    "docs/prompt_templates/handoff_resume_prompt.md",
    "docs/execution_contract.md",
    "docs/config_contract.md",
    "docs/guard_profile_contract.md",
    "docs/artifact_contract.md",
    "docs/result_contract.md"
)

if (-not $bootstrapFinalized) {
    $protectedPaths += @(
        "docs/bootstrap_initializer_guide.md",
        "config/project/bootstrap_seed.example.json",
        "scripts/initialize_project_from_skeleton.ps1"
    )
}

$gitDiffLines = Get-GitDiffLines
foreach ($line in $gitDiffLines) {
    $parts = $line -split "`t"
    if ($parts.Count -lt 2) {
        continue
    }

    $status = $parts[0]
    $oldPath = $parts[1]
    $newPath = if ($parts.Count -ge 3) { $parts[2] } else { $null }

    if ($status.StartsWith("D")) {
        if ($protectedPaths -contains $oldPath) {
            if ($approval) {
                Add-Warning "Protected path deletion allowed by approval: $oldPath"
            } else {
                Add-Failure "Protected path deletion requires explicit approval: $oldPath"
            }
        }
    }

    if ($status.StartsWith("R")) {
        if ($protectedPaths -contains $oldPath) {
            if ($approval) {
                Add-Warning "Protected path rename allowed by approval: $oldPath -> $newPath"
            } else {
                Add-Failure "Protected path rename requires explicit approval: $oldPath -> $newPath"
            }
        }
    }
}

Write-Host "Running repository skeleton guard..."
foreach ($message in $passes) {
    Write-Host "[PASS] $message"
}
foreach ($message in $warnings) {
    Write-Warning $message
}
foreach ($message in $failures) {
    Write-Error $message -ErrorAction Continue
}

if ($failures.Count -gt 0 -and -not $WarnOnly) {
    Write-Host "Repository skeleton guard result: failed"
    exit 1
}

if ($failures.Count -gt 0 -and $WarnOnly) {
    Write-Warning "Repository skeleton guard result: warn-only with failures present"
    exit 0
}

Write-Host "Repository skeleton guard result: passed"
exit 0
