#!/usr/bin/env bash
# =============================================================================
# Automated Build Script for Enterprise GCP Data Platform
# =============================================================================
set -euo pipefail

echo "====================================================================="
echo "Building Enterprise GCP Data Platform Application Package..."
echo "====================================================================="

BUILD_DIR="dist"
rm -rf "${BUILD_DIR}" *.egg-info build

echo "1. Validating Python syntax and compiling bytecode..."
python3 -m compileall src/

echo "2. Building Python distribution wheel & source tarball..."
python3 -m pip install --upgrade build setuptools wheel > /dev/null 2>&1 || true
python3 -m build --outdir "${BUILD_DIR}"

echo "3. Build complete. Generated artifacts:"
ls -lh "${BUILD_DIR}/"

echo "====================================================================="
echo "Build Successful! ✅"
echo "====================================================================="
