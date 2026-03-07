# Runs tests, ruff and mypy (where available)
param(
    [switch]$InstallDev
)
if ($InstallDev) {
    python -m pip install --upgrade pip
    pip install -e '.[dev]'
}

Write-Host "Running pytest..."
python -m pytest -q
$pytestExit = $LASTEXITCODE
if ($pytestExit -ne 0) { exit $pytestExit }

Write-Host "Running ruff..."
python -m ruff check src tests
$ruffExit = $LASTEXITCODE
if ($ruffExit -ne 0) { Write-Host "ruff reported issues (non-zero exit)." }

Write-Host "Running mypy (optional)..."
python -m mypy src 2>&1 | Out-Host

Write-Host "Done."
