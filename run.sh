# !/bin/bash
set -euo pipefail

# run from the directory this script lives in
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[run] CWD: $(pwd)"
echo "[run] python: $(python -V)"
ls -lah

# DPS expects a relative 'output/' folder; create it if missing
mkdir -p output

# sanity: your script name here
test -f subset_mask_cog.py || { echo "[run] ERROR: subset_mask_cog.py not found"; exit 1; }

echo "[run] starting job..."
python subset_mask_cog.py
echo "[run] finished."
