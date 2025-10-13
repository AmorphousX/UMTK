#!/usr/bin/env bash
set -euo pipefail

# Run from v1.5 root directory
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$dir"

PY=${PYTHON:-python3}
DIST_DIR=${DIST_DIR:-dist/umtk-ui-mac}
WORK_DIR=${WORK_DIR:-build/pyi-mac}
ONEFILE=${ONEFILE:-0}

# Create venv to isolate build
if [ ! -d .venv-mac ]; then
  "$PY" -m venv .venv-mac
fi
source .venv-mac/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

if [ "$ONEFILE" = "1" ]; then
  ONEFILE_FLAG="--onefile"
else
  ONEFILE_FLAG=""
fi

# macOS needs framework build of Qt usually provided by wheels
# Collect data folders
DATA_ARGS=(
  --add-data "img:img"
  --add-data "style:style"
  --add-data "lib:lib"
  --add-data "UMTK_Design.ui:."
  --add-data "UMTK_Design_dynamic.ui:."
  --add-data "requirements.txt:."
)

pyinstaller ${ONEFILE_FLAG} \
  --name UMTK_UI \
  --noconfirm \
  --windowed \
  --hidden-import PyQt6 \
  --hidden-import PySide6 \
  --collect-submodules matplotlib \
  --collect-data matplotlib \
  --collect-data qt_material \
  --distpath "$DIST_DIR" \
  --workpath "$WORK_DIR" \
  "${DATA_ARGS[@]}" \
  main.py

echo "Build complete. Output in $DIST_DIR"
