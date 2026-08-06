# End-to-End Pipeline Demonstration & Walkthrough

This guide details how to execute the complete end-to-end data ingestion, PySpark cleansing, BigQuery Gold Star Schema loading, MySQL to AlloyDB migration verification, and SRE production readiness evaluation using `src.e2e_runner`.

---

## ⚡ 1. Executing the Single Pipeline Entrypoint

Execute the complete end-to-end pipeline from terminal:

```bash
python -m src.e2e_runner
```

---

## 🔄 2. Sequential Execution Stages

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               STAGE 1: ARCHITECTURE INFRASTRUCTURE VALIDATION                      │
│  Validates GCS Buckets, IAM Least Privilege, Dataproc, BQ Datasets, AlloyDB, Secret Manager, KMS │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               STAGE 2: DATASET INGESTION & BRONZE LANDING                         │
│  Lands raw NYC Taxi trip feeds (Parquet/CSV) into gs://<project>-raw-bronze/                      │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            STAGE 3: PYSPARK ETL & DATA QUALITY ENGINE                             │
│  Executes 10 Data Quality rules on Dataproc; routes invalid records to gs://<project>-quarantine/ │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             STAGE 4: GOLD DATA WAREHOUSE LOADING                                  │
│  Executes incremental SQL MERGE into BigQuery Gold Star Schema dimension and fact tables          │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         STAGE 5: MIGRATION & FULL OBSERVABILITY AUDIT                             │
│  Validates MySQL -> AlloyDB CDC replication lag, traces OTel spans, and emits structured logs    │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        STAGE 6: SRE PRODUCTION READINESS & GO-LIVE REPORTING                      │
│  Evaluates 8 operational excellence dimensions and exports final_platform_validation.json       │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 3. Generated Sample Output Artifacts

Execution outputs sample JSON reports to [`examples/sample_outputs/`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/examples/sample_outputs/):
- `architecture_validation_report.json`
- `performance_report.json`
- `final_platform_validation.json`
- `production_readiness.json`
- `health_report.json`
- `cost_report.json`
- `sla_report.json`
