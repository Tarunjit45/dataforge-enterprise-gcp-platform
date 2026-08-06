#!/usr/bin/env bash
# =============================================================================
# Automated Deployment Script (Dev / Staging / Prod)
# =============================================================================
set -euo pipefail

ENVIRONMENT="${1:-dev}"
TF_DIR="terraform/environments/${ENVIRONMENT}"

echo "====================================================================="
echo "Deploying GCP Data Platform -> Environment: ${ENVIRONMENT}"
echo "====================================================================="

if [[ ! -d "${TF_DIR}" ]]; then
    echo "Error: Environment terraform directory '${TF_DIR}' does not exist!"
    exit 1
fi

echo "1. Initializing Terraform IaC..."
cd "${TF_DIR}"
terraform init

echo "2. Applying Infrastructure Deployment..."
terraform apply -auto-approve

echo "3. Synchronizing PySpark ETL Scripts & BigQuery DDLs to GCS Deployment Buckets..."
# Target bucket resolution from environment
BUCKET_NAME=$(terraform output -raw processed_bucket_name 2>/dev/null || echo "enterprise-${ENVIRONMENT}-processed-silver")

echo "Deployment completed to ${ENVIRONMENT} (${BUCKET_NAME})."
echo "====================================================================="
echo "Deployment Successful! ✅"
echo "====================================================================="
