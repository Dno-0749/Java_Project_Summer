$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$backendDir = Join-Path $root "src"
$frontendDir = Join-Path $root "frontend"

function Test-Port($port) {
	return [bool](Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
}

Write-Host "[1/5] Creating the project environment..."
if (-not (Test-Path $python)) {
	python -m venv (Join-Path $root ".venv")
}

Write-Host "[2/5] Installing backend and frontend dependencies..."
& $python -m pip install --disable-pip-version-check -q -r (Join-Path $backendDir "requirements.txt")
& $python -m pip install --disable-pip-version-check -q -r (Join-Path $frontendDir "requirements.txt")

Write-Host "[3/5] Checking Supabase PostgreSQL connection..."
Push-Location $backendDir
try {
	& $python -c "from dotenv import load_dotenv; import os, psycopg2; load_dotenv('.env'); url=os.getenv('POSTGRES_DATABASE_URL') or os.getenv('DATABASE_URL'); conn=psycopg2.connect(url, connect_timeout=8); conn.close(); print('Supabase PostgreSQL: connected')"
} finally {
	Pop-Location
}

if (Test-Port 9999) {
	Write-Host "Backend port 9999 is already in use; reusing the existing backend."
} else {
	Write-Host "[4/5] Starting backend on http://localhost:9999..."
	$backend = Start-Process -FilePath $python -ArgumentList "app.py" -WorkingDirectory $backendDir -PassThru
}

if (Test-Port 5000) {
	Write-Host "Frontend port 5000 is already in use; reusing the existing frontend."
} else {
	Write-Host "[5/5] Starting frontend on http://localhost:5000..."
	$frontend = Start-Process -FilePath $python -ArgumentList "app.py" -WorkingDirectory $frontendDir -PassThru
}

function Wait-ForUrl($url, $label) {
	for ($attempt = 1; $attempt -le 15; $attempt++) {
		try {
			Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2 | Out-Null
			return
		} catch {
			Start-Sleep -Seconds 1
		}
	}
	throw "$label did not respond at $url"
}

Wait-ForUrl "http://127.0.0.1:9999/swagger.json" "Backend"
Wait-ForUrl "http://127.0.0.1:5000/" "Frontend"

Write-Host ""
Write-Host "Project is starting:"
Write-Host "  Frontend: http://localhost:5000"
Write-Host "  Backend:  http://localhost:9999/swagger.json"
if ($backend) { Write-Host "  Backend PID: $($backend.Id)" }
if ($frontend) { Write-Host "  Frontend PID: $($frontend.Id)" }
Write-Host "To stop processes: Get-Process python | Stop-Process"
