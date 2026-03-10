#!/usr/bin/env bash
set -e
if [ ! -d .venv ]; then
  python -m venv .venv
  echo "Created virtual env .venv"
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt
streamlit run agent_dashboard.py --server.port 8503
