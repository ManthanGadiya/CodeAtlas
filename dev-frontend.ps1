# Runs the CodeAtlas frontend dev server, installing dependencies on first run.
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Push-Location "$root\frontend"
if (-not (Test-Path node_modules)) {
    Write-Host "[CodeAtlas] Installing frontend dependencies..."
    npm install
}
Write-Host "[CodeAtlas] Starting frontend on http://localhost:3000 ..."
npm run dev
Pop-Location
