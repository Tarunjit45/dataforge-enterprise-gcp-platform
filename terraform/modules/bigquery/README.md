# BigQuery Terraform Module

Provisions serverless BigQuery datasets (`raw_staging`, `silver_cleansed`, `gold_analytics`, `monitoring_telemetry`) with optional CMEK encryption and environment tagging.

## Datasets Provisioned
* `<environment>_raw_staging`: Ingestion staging layer.
* `<environment>_silver_cleansed`: Intermediate deduplicated datastore.
* `<environment>_gold_analytics`: Curated analytical datamarts (Star Schema).
* `<environment>_monitoring_telemetry`: Operational audit logs and telemetry data.
