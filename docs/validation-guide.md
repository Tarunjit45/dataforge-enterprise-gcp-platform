# Enterprise Infrastructure Validation & Operational Verification Guide

This guide details the post-deployment verification procedures and automated acceptance criteria for the GCP Data Platform landing zone.

## Automated Verification Tools

1. **Resource Existence & State Verification**:
   ```bash
   bash scripts/validate_infrastructure.sh <PROJECT_ID> <REGION>
   ```
2. **Infrastructure Smoke Tests**:
   ```bash
   bash scripts/run_smoke_tests.sh <PROJECT_ID> <REGION>
   ```

## Functional Component Verification Matrix

* **Networking**: Verify Private Google Access is enabled on `vpc-data-platform-subnet-us-central1` and zero external public IPs on Dataproc/AlloyDB.
* **Storage**: Verify versioning enabled on `raw-bronze`, `processed-silver`, `gold-artifacts` buckets and CMEK key bindings.
* **BigQuery**: Verify dataset creation for `raw_staging`, `silver_cleansed`, `gold_analytics`, `monitoring_telemetry`.
* **AlloyDB**: Verify Primary R/W instance and Read Pool HA endpoints.
* **Monitoring**: Verify Cloud Audit Log sink destination pointing to `platform-logs` bucket.
* **Database Migration**: Verify MySQL → AlloyDB data equivalence using `MigrationValidator` and `ChecksumEngine` (100% row count match, SHA256 checksum match, 0 foreign key orphans).
