# Enterprise GCP Data Platform Architecture & System Design

The Enterprise GCP Data Migration & ETL Platform is a production-grade analytics data platform designed to process batch and streaming datasets, validate data quality, populate a BigQuery Gold Data Warehouse, migrate MySQL databases to AlloyDB for PostgreSQL, and maintain zero-trust DevSecOps and observability standards.

---

## 🏛 1. High-Level Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     DATA INGESTION LAYER                                          │
│  HTTP / REST Connectors  │  GCS File Landers  │  NYC Taxi Parquet/CSV Feeds                      │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 BRONZE STORAGE (GCS LANDING)                                      │
│  gs://<project>-raw-bronze/                                                                       │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             PYSPARK ETL ENGINE & DATA QUALITY (DATAPROC)                          │
│  ├── PySpark Data Cleaning & Schema Standardization (Bronze -> Silver)                            │
│  ├── Data Quality Assertion Engine (Null, Range, Regex, Referential Integrity Rules)               │
│  └── Quarantine Isolator: Invalid records routed to gs://<project>-quarantine/                    │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SILVER STORAGE (GCS PROCESSED)                                    │
│  gs://<project>-processed-silver/ (Cleaned Parquet Datasets)                                     │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              GOLD DATA WAREHOUSE (BIGQUERY STAR SCHEMA)                           │
│  ├── Dimension Tables: dim_customer, dim_vendor, dim_location, dim_payment_type, dim_date, etc.    │
│  ├── Fact Table: fact_trip (Partitioned by trip_date, Clustered by keys)                          │
│  └── Analytics Data Marts: Executive Summary & Geographic Demand Views                            │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 2. Data Flow Architecture (Bronze $\rightarrow$ Silver $\rightarrow$ Gold)

1. **Bronze (Raw)**: Incoming external data files and payload streams are landed in GCS Bronze buckets with attached ingestion manifests.
2. **Silver (Cleansed)**: PySpark batch jobs on Dataproc process Bronze files, apply data quality assertions, filter invalid records to GCS Quarantine, and write standardized Parquet files to GCS Silver.
3. **Gold (Analytics)**: Incremental SQL MERGE operations load Silver Parquet datasets into BigQuery Gold Star Schema dimension and fact tables, refreshing downstream reporting views and data marts.

---

## 🗄 3. MySQL to AlloyDB Migration Architecture

```
MySQL Source DB ──► Datastream CDC ──► GCS Staging ──► AlloyDB PostgreSQL (Target)
       │                                                      ▲
       └────── Assessment & Schema Converter (DDL) ───────────┘
```

---

## 🔒 4. CI/CD & DevSecOps Architecture

Workload Identity Federation provides keyless authentication for GitHub Actions. Pipelines run linting, unit tests ($\ge 85\%$ coverage threshold), `Trivy`/`tfsec`/`Bandit`/`Semgrep` security scans, Terraform IaC deployment, smoke tests, and automated rollback on failure.
