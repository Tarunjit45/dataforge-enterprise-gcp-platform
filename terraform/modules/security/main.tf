# Security Module: KMS Keyring, Crypto Keys, and Secret Manager Secrets

resource "google_kms_key_ring" "keyring" {
  name     = var.keyring_name
  location = var.region
  project  = var.project_id
}

resource "google_kms_crypto_key" "storage_key" {
  name            = "cmek-storage-key"
  key_ring        = google_kms_key_ring.keyring.id
  rotation_period = var.key_rotation_period

  lifecycle {
    prevent_destroy = false
  }
}

resource "google_kms_crypto_key" "bigquery_key" {
  name            = "cmek-bigquery-key"
  key_ring        = google_kms_key_ring.keyring.id
  rotation_period = var.key_rotation_period

  lifecycle {
    prevent_destroy = false
  }
}

resource "google_secret_manager_secret" "db_credentials" {
  secret_id = "alloydb-db-credentials"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = local.common_labels
}
