# Security Terraform Module

Provisions Cloud KMS Keyring, Customer-Managed Encryption Keys (CMEK), and Secret Manager secrets.

## Resources
* `google_kms_key_ring.keyring`: KMS Keyring.
* `google_kms_crypto_key.storage_key`: CMEK key for Cloud Storage.
* `google_kms_crypto_key.bigquery_key`: CMEK key for BigQuery.
* `google_secret_manager_secret.db_credentials`: Secret Manager container for database credentials.
