#!/usr/bin/env bash
# =============================================================================
# Automated Artifact Packaging Script
# =============================================================================
set -euo pipefail

ENVIRONMENT="${1:-dev}"
VERSION="${2:-1.0.0}"
RELEASE_DIR="release_artifacts/${ENVIRONMENT}"

echo "====================================================================="
echo "Packaging Release Artifacts for Environment: ${ENVIRONMENT} (v${VERSION})"
echo "====================================================================="

mkdir -p "${RELEASE_DIR}"

echo "1. Packaging PySpark ETL Engine & Configs..."
tar -czf "${RELEASE_DIR}/pyspark_etl_${VERSION}.tar.gz" src/ config/ requirements.txt

echo "2. Packaging BigQuery Warehouse SQL Definitions..."
tar -czf "${RELEASE_DIR}/warehouse_sql_${VERSION}.tar.gz" src/warehouse/sql/ config/bq_schemas/

echo "3. Packaging Migration Engine Schemas & Mappings..."
tar -czf "${RELEASE_DIR}/migration_engine_${VERSION}.tar.gz" src/migration/ config/migration/

echo "4. Release package complete:"
ls -lh "${RELEASE_DIR}/"

echo "====================================================================="
echo "Packaging Successful! ✅"
echo "====================================================================="
