# End-to-End Operational Troubleshooting Guide

This guide provides step-by-step diagnostic workflows for resolving issues during end-to-end pipeline execution.

---

## 🛠 1. Diagnostic Workflows

### Scenario A: Pipeline Fails at Ingestion Stage
- **Check**: Inspect ingestion manifest file in `gs://<project>-raw-bronze/manifests/`.
- **Command**: `python -m src.ingestion.pipeline`

### Scenario B: PySpark ETL Job Fails on Dataproc
- **Check**: Inspect Dataproc driver logs in Google Cloud Logging using `trace_id`.
- **Query**: `jsonPayload.trace_id = "<TRACE_ID>"`

### Scenario C: High Quarantine Rate (> 10%)
- **Check**: Query Quarantine bucket files to inspect `_failed_rule` attributes.
- **Action**: Check source feed schema drift using `SchemaDriftDetector`.

### Scenario D: BigQuery MERGE Deadlocks
- **Check**: Confirm daily partitioning on `trip_date` is present in SQL MERGE statement.
- **Command**: `python -c "from src.warehouse.loader import GoldWarehouseLoader; print(GoldWarehouseLoader().generate_incremental_merge_sql('gold.fact_trip', 'silver.trips', 'trip_key'))"`
