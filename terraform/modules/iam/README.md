# IAM Terraform Module

Provisions dedicated Service Accounts and least-privilege IAM bindings for Dataproc, BigQuery, Storage, GitHub Actions OIDC, Monitoring, and Migration.

## Service Accounts
* `sa-dataproc-etl`: Dedicated worker for Dataproc Spark execution.
* `sa-bigquery-loader`: Dedicated loader for BigQuery warehouse writes.
* `sa-gcs-runner`: Dedicated Cloud Storage file reader/writer.
* `sa-github-actions`: Keyless CI/CD deployer via Workload Identity Federation.
* `sa-monitoring-emitter`: Custom telemetry emitter.
* `sa-database-migration`: Database Migration Service worker.
