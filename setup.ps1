# Create venv if it doesn't exist
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

# Activate venv
.\.venv\Scripts\Activate.ps1

# Upgrade pip
pip install --upgrade pip
pip install pip-tools

# If requirements.txt exists, install from it
if (Test-Path "requirements.txt") {
    pip-sync requirements.txt
} else {
    pip-compile requirements.in
}
