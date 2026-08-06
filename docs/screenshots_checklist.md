# Operational Console Screenshots Checklist

This checklist tracks required visual console assets to be captured from live GCP production environments for documentation and architecture reviews.

---

## 📸 Production Screenshots Checklist

- [ ] **1. Google Cloud Storage (GCS)**:
  - Bucket listing showing `raw_bronze`, `processed_silver`, `quarantine`, and `terraform_state` buckets.
  - Object details showing lifecycle rules and object versioning status.

- [ ] **2. BigQuery Datasets & Star Schema Tables**:
  - `gold_analytics` dataset schema tree showing `dim_customer`, `dim_vendor`, `dim_location`, `dim_payment_type`, `dim_date`, `dim_rate_code`, and `fact_trip`.
  - Table details showing daily partitioning on `trip_date` and clustering keys.

- [ ] **3. AlloyDB for PostgreSQL Cluster**:
  - AlloyDB cluster overview page showing primary instance and read pool nodes.
  - Continuous Datastream CDC replication status.

- [ ] **4. Dataproc PySpark Cluster**:
  - Active Dataproc cluster details page showing worker node count, dynamic shuffle service, and preemptible instances.
  - Job execution history showing PySpark batch job completion.

- [ ] **5. Google Cloud Monitoring**:
  - Metric Explorer showing `custom.googleapis.com/pipeline_duration_seconds` and `quarantine_rate_percent`.
  - Alert Policy configuration page showing active rules (`pipeline_failure`, `high_cdc_lag`).

- [ ] **6. Google Cloud Logging**:
  - Log Explorer view displaying structured JSON log records with `correlation_id`, `execution_id`, and `trace_id`.

- [ ] **7. GitHub Actions CI/CD Workflows**:
  - Actions tab showing successful 15-stage CI/CD pipeline execution (`ci.yml`, `cd.yml`).
  - Workload Identity keyless authentication step logs.

- [ ] **8. Terraform Infrastructure Apply**:
  - Execution summary showing `Apply complete! Resources: 18 added, 0 changed, 0 destroyed.`

- [ ] **9. Cloud Monitoring Operational Dashboards**:
  - Executive Dashboard displaying Availability SLO %, Freshness SLA, and estimated monthly spend.
  - Operations & Incident Response Dashboard displaying active system health scorecard.
