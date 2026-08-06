# Storage Module: Cloud Storage Buckets (Bronze, Silver, Gold, Quarantine, Logs)

resource "google_storage_bucket" "bronze_landing" {
  name                        = "${var.project_id}-raw-bronze"
  location                    = var.region
  project                     = var.project_id
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  encryption {
    default_kms_key_name = var.kms_crypto_key_id
  }

  labels = local.common_labels
}

resource "google_storage_bucket" "silver_processed" {
  name                        = "${var.project_id}-processed-silver"
  location                    = var.region
  project                     = var.project_id
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = var.kms_crypto_key_id
  }

  labels = local.common_labels
}

resource "google_storage_bucket" "gold_artifacts" {
  name                        = "${var.project_id}-gold-artifacts"
  location                    = var.region
  project                     = var.project_id
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = var.kms_crypto_key_id
  }

  labels = local.common_labels
}

resource "google_storage_bucket" "quarantine" {
  name                        = "${var.project_id}-quarantine"
  location                    = var.region
  project                     = var.project_id
  force_destroy               = false
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 180
    }
    action {
      type = "Delete"
    }
  }

  encryption {
    default_kms_key_name = var.kms_crypto_key_id
  }

  labels = local.common_labels
}

resource "google_storage_bucket" "logs" {
  name                        = "${var.project_id}-platform-logs"
  location                    = var.region
  project                     = var.project_id
  force_destroy               = false
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  encryption {
    default_kms_key_name = var.kms_crypto_key_id
  }

  labels = local.common_labels
}
