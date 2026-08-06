output "keyring_id" {
  value       = google_kms_key_ring.keyring.id
  description = "KMS Keyring ID"
}

output "storage_crypto_key_id" {
  value       = google_kms_crypto_key.storage_key.id
  description = "Storage CMEK Crypto Key ID"
}

output "bigquery_crypto_key_id" {
  value       = google_kms_crypto_key.bigquery_key.id
  description = "BigQuery CMEK Crypto Key ID"
}

output "db_credentials_secret_id" {
  value       = google_secret_manager_secret.db_credentials.id
  description = "Secret Manager AlloyDB Secret ID"
}
