#!/usr/bin/env bash
# =============================================================================
# Automated Post-Deployment Infrastructure & Application Smoke Tests
# =============================================================================
set -euo pipefail

ENVIRONMENT="${1:-dev}"
PROJECT_ID="${2:-enterprise-data-dev-12345}"
REGION="${3:-us-central1}"

echo "====================================================================="
echo "Executing Post-Deployment Smoke Tests -> Env: ${ENVIRONMENT} (${PROJECT_ID})"
echo "====================================================================="

echo "1. Running Infrastructure State Smoke Tests..."
if [[ -f "scripts/run_smoke_tests.sh" ]]; then
    bash scripts/run_smoke_tests.sh "${PROJECT_ID}" "${REGION}" || exit 1
fi

echo "2. Running Infrastructure Resource Validation..."
if [[ -f "scripts/validate_infrastructure.sh" ]]; then
    bash scripts/validate_infrastructure.sh "${PROJECT_ID}" "${REGION}" || exit 1
fi

echo "3. Running Application Core Verification Suites..."
python3 -m pytest tests/unit/test_config.py tests/unit/test_exceptions.py || exit 1

echo "====================================================================="
echo "All Smoke Tests PASSED Successfully! ✅"
echo "====================================================================="
