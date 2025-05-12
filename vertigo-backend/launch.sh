#!/bin/bash

# === Step 1: Define paths ===
VENV_DIR="$(pwd)/env"
PYTHON_EXEC="$VENV_DIR/bin/python"

# === Step 2: Create virtual environment if not exists ===
if [ ! -f "$PYTHON_EXEC" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# === Step 3: Install requirements ===
echo "[INFO] Installing dependencies..."
"$PYTHON_EXEC" -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies."
    exit 1
fi

# === Step 4: Run the app ===
echo "[INFO] Launching app..."
xdg-open http://localhost:6166 >/dev/null 2>&1 &

# Activate the environment and run the Python app
source "$VENV_DIR/bin/activate"
python -m vertigo.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to launch app."
    exit 1
fi
