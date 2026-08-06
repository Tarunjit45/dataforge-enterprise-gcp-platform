# Centralized Structured JSON Logging & Error Taxonomy Guide

This guide describes the structured JSON logging standards enforced by `TelemetryLogger`.

---

## 📝 1. Structured JSON Format

Every log entry emitted to `stdout` or Google Cloud Logging is serialized as a JSON object:

```json
{
  "timestamp": "2026-08-06T21:05:00.000000+00:00",
  "severity": "ERROR",
  "message": "Data Quality assertion failed for column VendorID",
  "logger": "quality_engine",
  "correlation_id": "c7a91823-11ef-4011-89ab-019283719283",
  "execution_id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "batch_id": "batch_20260806_001",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "error_category": "DATA_QUALITY_ERROR"
}
```

---

## 🏷 2. Error Taxonomy & Severity Levels

| Category | Code | Severity | Description |
| --- | --- | --- | --- |
| `DATA_QUALITY_ERROR` | `ERR_DQ_001` | `ERROR` | Data Quality assertion failed or threshold breached. |
| `INFRASTRUCTURE_ERROR` | `ERR_INFRA_002` | `CRITICAL` | Cloud storage, network connection, or DB driver failure. |
| `MIGRATION_ERROR` | `ERR_MIG_003` | `ERROR` | Database schema conversion or data extraction failure. |
| `ETL_FAILURE` | `ERR_ETL_004` | `CRITICAL` | PySpark transformation or write pipeline error. |

---

## 🔍 3. Google Cloud Logging Queries

Filter logs by Correlation ID in GCP Log Explorer:
```json
jsonPayload.correlation_id = "c7a91823-11ef-4011-89ab-019283719283"
```
Filter Critical Infrastructure Errors:
```json
severity = "CRITICAL" AND jsonPayload.error_category = "INFRASTRUCTURE_ERROR"
```
