# PowerShell script to start the dashboard
Set-StrictMode -Version Latest
if (-Not (Test-Path -Path .venv)) {
    python -m venv .venv
    Write-Host "Created virtual environment .venv"
}
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run agent_dashboard.py --server.port 8503
