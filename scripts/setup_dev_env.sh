#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo "Initializing GCP Data Migration & ETL Platform Dev Environment"
echo "============================================================"

# Ensure Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Create virtual environment if not present
if [ ! -d ".venv" ]; then
    echo "==> Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "==> Activating virtual environment..."
source .venv/bin/activate || source .venv/Scripts/activate

# Upgrade pip & install dev dependencies
echo "==> Installing development dependencies..."
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .

# Setup pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "==> Installing pre-commit git hooks..."
    pre-commit install
fi

echo "============================================================"
echo "Development environment initialized successfully!"
echo "Run 'pytest' to verify unit tests."
echo "============================================================"
