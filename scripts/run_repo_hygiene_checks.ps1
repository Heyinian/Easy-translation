param(
    [switch]$WarnOnly
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$checks = @(
    "check_repo_guard.ps1",
    "check_gitignore_hygiene.ps1"
)

$failed = $false

foreach ($checkName in $checks) {
    $checkPath = Join-Path $scriptRoot $checkName
    Write-Host ""
    Write-Host "=== Running $checkName ==="

    if ($WarnOnly) {
        & $checkPath -WarnOnly
    } else {
        & $checkPath
    }

    if ($LASTEXITCODE -ne 0) {
        $failed = $true
    }
}

Write-Host ""
if ($failed -and -not $WarnOnly) {
    Write-Host "Repository hygiene checks result: failed"
    exit 1
}

if ($failed -and $WarnOnly) {
    Write-Warning "Repository hygiene checks result: warn-only with failures present"
    exit 0
}

Write-Host "Repository hygiene checks result: passed"
exit 0
