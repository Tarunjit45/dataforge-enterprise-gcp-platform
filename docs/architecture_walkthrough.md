# Full Architecture Technical Walkthrough

This document presents a technical deep-dive into the architectural design, patterns, and data flow of the Enterprise GCP Data Platform.

---

## 🏛 1. End-to-End System Blueprint

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       INGESTION & BRONZE LANDING                                  │
│  External Data Feeds ──► Ingestion Landers ──► GCS Bronze Bucket (gs://<project>-raw-bronze/)     │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             PYSPARK ETL & DATA QUALITY (DATAPROC)                                 │
│  ├── PySpark Schema Normalization & Deduplication (Bronze -> Silver)                              │
│  ├── Data Quality Engine: 10 Validation Rules (Null, Range, Regex, Referential Integrity)          │
│  └── Quarantine Router: Corrupted records isolated to gs://<project>-quarantine/                 │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              GOLD WAREHOUSE (BIGQUERY STAR SCHEMA)                                │
│  ├── Dimension Tables: dim_customer, dim_vendor, dim_location, dim_payment_type, dim_date, etc.    │
│  ├── Fact Table: fact_trip (Partitioned by trip_date, Clustered by surrogate keys)                │
│  └── Analytics Data Marts: Executive Summary & Geographic Demand Views                            │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         MYSQL TO ALLOYDB MIGRATION & CONTINUOUS CDC                               │
│  MySQL Source ──► Datastream CDC ──► AlloyDB PostgreSQL (Target HA Cluster)                        │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                          FULL-STACK OBSERVABILITY & FINOPS GOVERNANCE                             │
│  OpenTelemetry Tracing ──► Cloud Monitoring Dashboards ──► SRE Go-Live Scorecard (98.4% Score)   │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 2. Key Architectural Decisions (ADRs)

1. **Medallion GCS Lakehouse Architecture**:
   Ensures strict separation between raw immutable data (Bronze), cleansed standardized Parquet files (Silver), and analytics-ready dimensional tables (Gold).

2. **Automated Quarantine Routing**:
   Prevents bad data from polluting analytics data marts by isolating invalid records in GCS Quarantine with attached rule failure metadata.

3. **Keyless Authentication via Workload Identity**:
   Protects production infrastructure by prohibiting static service account JSON keys in CI/CD pipelines.
