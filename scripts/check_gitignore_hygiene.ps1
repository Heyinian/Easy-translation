param(
    [switch]$WarnOnly
)

$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$gitignorePath = Join-Path $repoRoot ".gitignore"

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

if (-not (Test-Path -LiteralPath $gitignorePath)) {
    Add-Failure "Missing .gitignore at repo root."
} else {
    $gitignoreLines = Get-Content -LiteralPath $gitignorePath | ForEach-Object { $_.Trim() }
    $requiredPatterns = @(
        "artifacts/",
        "*.log",
        "*.tmp",
        ".vs/",
        "bin/",
        "obj/",
        "node_modules/",
        ".venv/",
        "coverage/",
        "config/**/*.local.json"
    )

    foreach ($pattern in $requiredPatterns) {
        if ($gitignoreLines -contains $pattern) {
            Add-Pass ".gitignore contains baseline pattern: $pattern"
        } else {
            Add-Failure ".gitignore is missing baseline pattern: $pattern"
        }
    }
}

if (Get-Command git -ErrorAction SilentlyContinue) {
    $insideWorkTree = (& git -c core.autocrlf=false -c core.safecrlf=false -C $repoRoot rev-parse --is-inside-work-tree 2>$null)
    if ($LASTEXITCODE -eq 0 -and ($insideWorkTree | Select-Object -First 1) -eq "true") {
        $untrackedPaths = & git -c core.autocrlf=false -c core.safecrlf=false -C $repoRoot ls-files --others --exclude-standard 2>$null
        if ($LASTEXITCODE -eq 0) {
            $suspiciousPatterns = @(
                '(?i)(^|/)\.vs(/|$)',
                '(?i)(^|/)\.idea(/|$)',
                '(?i)(^|/)(bin|obj|Debug|Release|x64|x86|TestResults|dist|coverage)(/|$)',
                '(?i)(^|/)node_modules(/|$)',
                '(?i)(^|/)(\.venv|venv)(/|$)',
                '(?i)(^|/)(__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache)(/|$)',
                '(?i)\.(log|tmp|cache|user|suo|rsuser|pdb|ilk|nupkg|pyc)$',
                '(?i)(^|/)Thumbs\.db$',
                '(?i)(^|/)Desktop\.ini$',
                '(?i)(^|/)artifacts(/|$)',
                '(?i)(^|/)config/.+\.local\.(json|yaml|yml)$'
            )

            $allowedPlaceholderPaths = @(
                'artifacts/README.md',
                'artifacts/.gitkeep'
            )

            foreach ($path in @($untrackedPaths | Where-Object { $_ })) {
                $normalized = $path.Replace('\', '/')
                if ($allowedPlaceholderPaths -contains $normalized) {
                    Add-Pass "Allowed tracked-placeholder-style path present: $normalized"
                    continue
                }

                foreach ($pattern in $suspiciousPatterns) {
                    if ($normalized -match $pattern) {
                        Add-Failure "Suspicious local-only path is not ignored: $normalized"
                        break
                    }
                }
            }
        } else {
            Add-Warning "Unable to query untracked files; skipping suspicious-path scan."
        }
    } else {
        Add-Warning "Repository is not a valid git worktree; skipping suspicious-path scan."
    }
} else {
    Add-Warning "git was not available; skipping suspicious-path scan."
}

Write-Host "Running .gitignore hygiene audit..."
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
    Write-Host ".gitignore hygiene audit result: failed"
    exit 1
}

if ($failures.Count -gt 0 -and $WarnOnly) {
    Write-Warning ".gitignore hygiene audit result: warn-only with failures present"
    exit 0
}

Write-Host ".gitignore hygiene audit result: passed"
exit 0
