#!/usr/bin/env bash
# OpenAgentSec Environment Setup Script (PRD v4.0.2 Phase 7.6.4)
set -euo pipefail

echo "========================================="
echo " OpenAgentSec Environment Setup"
echo "========================================="

PYTHON_BIN=$(command -v python3 || command -v python)
echo "Using Python: $($PYTHON_BIN --version)"

VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Upgrading pip and installing OpenAgentSec in editable mode..."
pip install --upgrade pip
pip install -e .
pip install pytest

echo "========================================="
echo " Environment ready! Run 'source venv/bin/activate'"
echo "========================================="
