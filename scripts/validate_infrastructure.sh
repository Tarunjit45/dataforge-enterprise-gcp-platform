#!/usr/bin/env bash
# Infrastructure Validation & Verification Script
# Verifies GCP Cloud Foundation resources provisioned by Terraform.

set -euo pipefail

PROJECT_ID="${1:-${GCP_PROJECT_ID:-enterprise-data-dev-12345}}"
REGION="${2:-${GCP_REGION:-us-central1}}"

echo "========================================================="
echo "GCP Enterprise Data Platform - Infrastructure Validation"
echo "Project ID: ${PROJECT_ID}"
echo "Region:     ${REGION}"
echo "========================================================="

PASSED_CHECKS=0
FAILED_CHECKS=0

log_pass() {
    echo "  [PASS] $1"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
}

log_fail() {
    echo "  [FAIL] $1"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
}

echo "1. Validating Private VPC Networking & Subnets..."
if gcloud compute networks describe "vpc-data-platform" --project="${PROJECT_ID}" &>/dev/null; then
    log_pass "VPC Network 'vpc-data-platform' exists."
else
    log_fail "VPC Network 'vpc-data-platform' missing."
fi

if gcloud compute routers list --project="${PROJECT_ID}" --filter="region:${REGION}" | grep -q "vpc-data-platform-router"; then
    log_pass "Cloud NAT Router exists in region ${REGION}."
else
    log_fail "Cloud NAT Router missing in region ${REGION}."
fi

echo "2. Validating Cloud Storage CMEK Buckets..."
for BUCKET_SUFFIX in "raw-bronze" "processed-silver" "gold-artifacts" "quarantine" "platform-logs"; do
    BUCKET_NAME="${PROJECT_ID}-${BUCKET_SUFFIX}"
    if gcloud storage buckets describe "gs://${BUCKET_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
        log_pass "Cloud Storage Bucket 'gs://${BUCKET_NAME}' exists."
    else
        log_fail "Cloud Storage Bucket 'gs://${BUCKET_NAME}' missing."
    fi
done

echo "3. Validating BigQuery Serverless Datasets..."
for DATASET_PREFIX in "dev_raw_staging" "dev_silver_cleansed" "dev_gold_analytics" "dev_monitoring_telemetry"; do
    if bq show --project_id="${PROJECT_ID}" "${DATASET_PREFIX}" &>/dev/null; then
        log_pass "BigQuery Dataset '${DATASET_PREFIX}' exists."
    else
        log_fail "BigQuery Dataset '${DATASET_PREFIX}' missing."
    fi
done

echo "4. Validating Dedicated Service Accounts..."
for SA_NAME in "sa-dataproc-etl" "sa-bigquery-loader" "sa-gcs-runner" "sa-github-actions" "sa-monitoring-emitter" "sa-database-migration"; do
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    if gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" &>/dev/null; then
        log_pass "Service Account '${SA_NAME}' exists."
    else
        log_fail "Service Account '${SA_NAME}' missing."
    fi
done

echo "5. Validating Dataproc Workflow Templates..."
if gcloud dataproc workflow-templates list --project="${PROJECT_ID}" --region="${REGION}" | grep -q "ephemeral-pyspark-job"; then
    log_pass "Dataproc Workflow Template 'ephemeral-pyspark-job' exists."
else
    log_fail "Dataproc Workflow Template 'ephemeral-pyspark-job' missing."
fi

echo "========================================================="
echo "Validation Complete. Passed: ${PASSED_CHECKS}, Failed: ${FAILED_CHECKS}"
echo "========================================================="

if [ "${FAILED_CHECKS}" -gt 0 ]; then
    exit 1
fi
