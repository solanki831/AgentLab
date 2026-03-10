# Create venv and install requirements
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Write-Host "Setup complete. Activate with: . \.venv\Scripts\Activate.ps1"