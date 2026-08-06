# Storage Terraform Module

Provisions Cloud Storage buckets for multi-tier data processing (Bronze, Silver, Gold, Quarantine, Logs) with CMEK, versioning, Uniform Bucket Level Access, and storage class lifecycle policies.

## Buckets Provisioned
* `<project_id>-raw-bronze`: Raw landing zone (Nearline migration after 30 days).
* `<project_id>-processed-silver`: Cleansed staging zone.
* `<project_id>-gold-artifacts`: Curated assets and PySpark script repository.
* `<project_id>-quarantine`: Quarantined non-compliant records (Auto-delete after 180 days).
* `<project_id>-platform-logs`: Platform operational log bucket (Coldline migration after 90 days).
