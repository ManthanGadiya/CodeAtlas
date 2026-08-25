# Runs the CodeAtlas backend using the project's own virtual environment,
# creating/repairing it if needed — immune to shell activation state.
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

if (-not (Test-Path "$root\.venv\Scripts\python.exe")) {
    Write-Host "[CodeAtlas] Creating virtual environment (.venv)..."
    python -m venv "$root\.venv"
    & "$root\.venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
}

& "$root\.venv\Scripts\python.exe" -m pip show codeatlas-backend *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[CodeAtlas] Installing backend dependencies into .venv..."
    Push-Location "$root\backend"
    & "$root\.venv\Scripts\python.exe" -m pip install -e ".[dev]" --quiet
    Pop-Location
}

Write-Host "[CodeAtlas] Starting API on http://127.0.0.1:8000 ..."
Push-Location "$root\backend"
& "$root\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload
Pop-Location
