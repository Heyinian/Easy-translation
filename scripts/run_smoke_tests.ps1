param(
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot

if ([string]::IsNullOrWhiteSpace($PythonPath)) {
    $venvPython = Join-Path $repoRoot ".venv312\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        $PythonPath = $venvPython
    } else {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCommand) {
            $PythonPath = $pythonCommand.Source
        } else {
            throw "Python executable was not found. Pass -PythonPath explicitly."
        }
    }
}

Write-Host "Running smoke tests with: $PythonPath"
& $PythonPath -m unittest discover -s tests -p "test_*.py" -v
exit $LASTEXITCODE
