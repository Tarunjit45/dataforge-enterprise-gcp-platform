# BigQuery Module: Staging, Cleansed, Analytics, and Monitoring Datasets

resource "google_bigquery_dataset" "raw_staging" {
  dataset_id                 = "${var.environment}_raw_staging"
  friendly_name              = "Raw Staging Ingestion Layer"
  description                = "Raw landing dataset for incoming batch staged data"
  location                   = var.location
  project                    = var.project_id
  delete_contents_on_destroy = false

  dynamic "default_encryption_configuration" {
    for_each = var.kms_crypto_key_id != null ? [var.kms_crypto_key_id] : []
    content {
      kms_key_name = default_encryption_configuration.value
    }
  }

  labels = local.common_labels
}

resource "google_bigquery_dataset" "silver_cleansed" {
  dataset_id                 = "${var.environment}_silver_cleansed"
  friendly_name              = "Silver Cleansed Transformation Layer"
  description                = "Cleansed, deduplicated intermediate datastores"
  location                   = var.location
  project                    = var.project_id
  delete_contents_on_destroy = false

  dynamic "default_encryption_configuration" {
    for_each = var.kms_crypto_key_id != null ? [var.kms_crypto_key_id] : []
    content {
      kms_key_name = default_encryption_configuration.value
    }
  }

  labels = local.common_labels
}

resource "google_bigquery_dataset" "gold_analytics" {
  dataset_id                 = "${var.environment}_gold_analytics"
  friendly_name              = "Gold Analytics Enterprise Warehouse"
  description                = "Curated analytical datamarts (Star Schema)"
  location                   = var.location
  project                    = var.project_id
  delete_contents_on_destroy = false

  dynamic "default_encryption_configuration" {
    for_each = var.kms_crypto_key_id != null ? [var.kms_crypto_key_id] : []
    content {
      kms_key_name = default_encryption_configuration.value
    }
  }

  labels = local.common_labels
}

resource "google_bigquery_dataset" "monitoring_telemetry" {
  dataset_id                 = "${var.environment}_monitoring_telemetry"
  friendly_name              = "Platform Telemetry & Audit Logs"
  description                = "Pipeline performance metrics, audit logs, and data quality check results"
  location                   = var.location
  project                    = var.project_id
  delete_contents_on_destroy = false

  dynamic "default_encryption_configuration" {
    for_each = var.kms_crypto_key_id != null ? [var.kms_crypto_key_id] : []
    content {
      kms_key_name = default_encryption_configuration.value
    }
  }

  labels = local.common_labels
}
