# Cloud Monitoring Alert Incident Response Runbook

This runbook outlines standard operating procedures for resolving fired Cloud Monitoring alerts evaluated by `AlertEvaluator`.

---

## 🚨 Alert Response Procedures

### 1. `pipeline_failure` (Severity: CRITICAL)
- **Condition**: Pipeline execution state = `FAILED`.
- **Response**:
  1. Inspect `execution_summary.json` and structured JSON logs filtered by `correlation_id`.
  2. Identify root cause in PySpark job or schema validator.
  3. If unrecoverable, trigger `scripts/rollback.sh`.

### 2. `high_cdc_lag` (Severity: HIGH)
- **Condition**: `cdc_replication_lag_seconds > 10.0s`.
- **Response**:
  1. Check Google Datastream connection profile status.
  2. Inspect MySQL source binlog generation rate.
  3. Pause migration cutover until lag falls below 5.0s.

### 3. `dq_score_below_threshold` (Severity: HIGH)
- **Condition**: `data_quality_score_percent < 70.0%`.
- **Response**:
  1. Inspect `quality_report.json` and `_failed_rule` attributes in quarantine storage.
  2. Check source data feed for schema drift or null spikes.

### 4. `high_cost_anomaly` (Severity: MEDIUM)
- **Condition**: `daily_spend_usd > $150.0`.
- **Response**:
  1. Query `INFORMATION_SCHEMA.JOBS_BY_PROJECT` to find expensive BigQuery queries.
  2. Verify Dataproc clusters auto-scale down during idle windows.
