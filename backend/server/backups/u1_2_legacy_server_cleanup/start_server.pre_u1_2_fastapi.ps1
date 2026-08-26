# start_server.ps1 — reliable starter for LinkCraftor (Windows/PowerShell)
$ErrorActionPreference = "Stop"

# 1) Go to project root
Set-Location "C:\Users\HP\Documents\LinkCraftor"

# 2) Make a virtual environment if missing
if (!(Test-Path ".venv")) {
  Write-Host "Creating virtual environment..."
  py -m venv .venv
}

# 3) Activate venv
& ".\.venv\Scripts\Activate.ps1"

# 4) Ensure required packages
pip install --upgrade pip >$null
pip install flask flask-cors >$null

# 5) Choose a free port (prefer 8001, else 8003)
$port = 8001
$inUse = (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue)
if ($inUse) {
  Write-Host "Port $port busy. Switching to 8003."
  $port = 8003
}

# 6) Tell server.py which port to use
$env:LINKCRAFTOR_PORT = "$port"

# 7) Start the server
Write-Host "Starting server on http://127.0.0.1:$port ..."
python server.py
