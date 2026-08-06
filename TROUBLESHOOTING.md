# Operational Troubleshooting & Diagnostic Guide

This guide provides diagnostic procedures and resolution steps for common operational issues.

---

## 🛠 1. Common Issues & Solutions

### A. PySpark `AnalysisException: Path does not exist`
- **Symptom**: PySpark job fails when reading Bronze GCS bucket.
- **Cause**: Ingestion lander has not populated the raw partition folder.
- **Resolution**: Verify ingestion pipeline completed and check GCS manifest file presence (`gs://<bronze-bucket>/manifests/`).

### B. BigQuery `Access Denied: Table <dataset>.<table_id>`
- **Symptom**: BigQuery loader fails with HTTP 403 Forbidden.
- **Cause**: Service account missing `roles/bigquery.dataEditor` or `roles/bigquery.jobUser`.
- **Resolution**: Run `python -m src.operations.iam_audit` to verify IAM role bindings.

### C. Datastream CDC Replication Lag > 10s
- **Symptom**: `high_cdc_lag` alert fires during MySQL to AlloyDB migration.
- **Cause**: Source MySQL binlog generation exceeds streaming pipeline capacity.
- **Resolution**: Increase Datastream stream capacity or verify network VPC peering bandwidth.

---

## 🔍 2. Diagnostic Commands

Run unit tests and verification:
```bash
pytest
```
Run platform health checks:
```bash
python -c "from src.observability.health_checks import ServiceHealthChecker; ServiceHealthChecker().generate_health_report()"
```
Run IAM audit check:
```bash
python -c "from src.operations.iam_audit import IAMAuditEngine; print(IAMAuditEngine().audit_iam_policy())"
```
