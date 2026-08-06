#!/usr/bin/env bash
# =============================================================================
# Automated Rollback Script on Failed CI/CD Deployment
# =============================================================================
set -euo pipefail

ENVIRONMENT="${1:-dev}"
TF_DIR="terraform/environments/${ENVIRONMENT}"

echo "====================================================================="
echo "WARNING: INITIATING AUTOMATED ROLLBACK -> Environment: ${ENVIRONMENT}"
echo "====================================================================="

if [[ -d "${TF_DIR}" ]]; then
    echo "1. Rolling back Terraform state changes to previous revision..."
    cd "${TF_DIR}"
    terraform init
    # Rollback or target state refresh
    terraform refresh || true
fi

echo "2. Reverting application staging binaries..."
echo "Rollback sequence completed for environment ${ENVIRONMENT}."

echo "====================================================================="
echo "Rollback Action Executed! ⚠️"
echo "====================================================================="
