# Enterprise MySQL → AlloyDB for PostgreSQL Data Migration Framework Architecture

The Enterprise Data Migration Framework provides a production-grade, automated database modernization platform designed to assess, convert, extract, load, continuously replicate (CDC), validate, cut over, and roll back enterprise MySQL workloads into Google Cloud AlloyDB for PostgreSQL with minimal downtime.

---

## 🏛 1. End-to-End Migration Architecture & Workflow

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                PHASE 1: ASSESSMENT & PLANNING                                     │
│  DatabaseAssessmentEngine (assessment.py)                                                         │
│  ├── Introspects MySQL Information Schema (mysql_introspection.sql)                               │
│  ├── Detects incompatible features (MyISAM, FULLTEXT, ZEROFILL, etc.)                             │
│  └── Outputs: migration_assessment.json & compatibility_report.json                               │
└─────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                PHASE 2: DDL SCHEMA TRANSLATION                                    │
│  SchemaConverter (schema_converter.py)                                                            │
│  ├── Applies data type mappings (datatype_mapping.yaml)                                           │
│  ├── Translates PKs, FKs, Indexes, Views, AUTO_INCREMENT -> IDENTITY                              │
│  └── Outputs: converted_schema.sql & schema_conversion_report.json                                │
└─────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 3: INITIAL BULK LOAD & CDC REPLICATION                             │
│  DataExtractor & DataLoader (extractor.py & loader.py)                                            │
│  ├── Parallel chunked extraction & batch loading into AlloyDB                                    │
│  ├── DatastreamCDCManager (datastream.py) establishes continuous GTID/Binlog CDC stream          │
│  └── BinlogReplicationTracker (replication.py) monitors replication lag in seconds              │
└─────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 4: VALIDATION & GO/NO-GO GATING                                   │
│  MigrationValidator & ChecksumEngine (validator.py & checksum.py)                                 │
│  ├── Computes table SHA256 checksums, row counts, sample comparisons, FK orphan checks            │
│  └── Outputs: migration_validation.json (Must pass 100% to proceed to cutover)                   │
└─────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                  │
                                 ┌────────────────┴────────────────┐
                                 │                                 │
                     Checklist Passed?                     Validation Failed?
                                 │                                 │
                                 ▼                                 ▼
┌─────────────────────────────────────────────────┐   ┌─────────────────────────────────────────────┐
│    PHASE 5A: PRODUCTION CUTOVER                 │   │    PHASE 5B: EMERGENCY ROLLBACK             │
│    CutoverOrchestrator (cutover.py)             │   │    RollbackEngine (rollback.py)             │
│    ├── Lock MySQL (App Maintenance Mode)        │   │    ├── Revert Connection String -> MySQL    │
│    ├── Final Delta Catch-up Sync                │   │    ├── Tear down CDC Datastream             │
│    ├── Switch App Connection -> AlloyDB         │   │    └── Drop partial target or restore PITR   │
│    └── Output: cutover_report.json              │   │    └── Output: rollback_plan.json           │
└─────────────────────────────────────────────────┘   └─────────────────────────────────────────────┘
```

---

## ⚙️ 2. Core Framework Components

| Module | Location | Primary Responsibility |
| --- | --- | --- |
| **Assessment Engine** | [`assessment.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/assessment.py) | Introspects MySQL metadata, detects unsupported features, calculates compatibility score %, and estimates migration effort. |
| **Schema Converter** | [`schema_converter.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/schema_converter.py) | Translates MySQL DDL definitions to ANSI PostgreSQL / AlloyDB DDL using [`datatype_mapping.yaml`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/config/migration/datatype_mapping.yaml). |
| **Extractor Engine** | [`extractor.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/extractor.py) | Chunked parallel data extraction from MySQL with retry backoff and checkpointing. |
| **Loader Engine** | [`loader.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/loader.py) | Optimized batch loading into AlloyDB with transaction retries and checkpoint tracking. |
| **Checksum Engine** | [`checksum.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/checksum.py) | Computes SHA256 / MD5 digest signatures per row block and table dataset. |
| **Validator Engine** | [`validator.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/validator.py) | Validates row counts, SHA256 checksums, sample record equivalence, and foreign key orphans. |
| **CDC Framework** | [`datastream.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/cdc/datastream.py) & [`replication.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/cdc/replication.py) | Configures Google Cloud Datastream CDC replication streams, tracks MySQL binlog positions and replication lag. |
| **Cutover Orchestrator** | [`cutover.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/cutover.py) | Manages pre-cutover checklist verification, application maintenance window, final delta sync, and application connection switchover. |
| **Rollback Engine** | [`rollback.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/rollback.py) | Executes emergency rollback, DNS reversion, and AlloyDB point-in-time snapshot recovery. |
| **Reporter Engine** | [`reporting.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/migration/reporting.py) | Consolidates all 6 JSON artifacts into unified executive markdown dashboards. |

---

## 📄 3. Deliverable JSON Reports

1. `migration_assessment.json`: Database inventory, schema metrics, and size details.
2. `compatibility_report.json`: Overall compatibility score %, estimated hours, and unsupported feature list.
3. `schema_conversion_report.json`: DDL conversion metrics (converted tables, columns, indexes, foreign keys).
4. `migration_validation.json`: Verification matrix containing row count comparisons, SHA256 checksum matches, and sample mismatch counts.
5. `cutover_report.json`: Production cutover execution log, checklist pass status, and timing timestamps.
6. `rollback_plan.json`: Formatted rollback execution plan and disaster recovery procedures.

---

## ⚡ 4. Performance & Tuning Recommendations

1. **Parallel Extraction**: Set `parallel_threads: 4` in `migration_config.yaml` for concurrent multi-table extraction.
2. **PostgreSQL Copy / Unlogged Tables**: Use `UNLOGGED` tables during initial bulk load, then convert to `LOGGED` prior to CDC activation to reduce WAL write overhead by 40%.
3. **Index Deferral**: Create primary keys before initial bulk load, but defer secondary indexes and foreign key constraints until bulk load completes to maximize write throughput.
4. **AlloyDB Columnar Engine**: Enable AlloyDB Columnar Engine (`google_columnar_engine.enabled = ON`) on read pool instances for high-throughput OLAP reporting queries post-migration.
