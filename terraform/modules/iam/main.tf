# IAM Module: Service Accounts and Least-Privilege IAM Bindings

resource "google_service_account" "dataproc_sa" {
  account_id   = "sa-dataproc-etl"
  display_name = "Dataproc Ephemeral Cluster Service Account"
  project      = var.project_id
}

resource "google_service_account" "bigquery_sa" {
  account_id   = "sa-bigquery-loader"
  display_name = "BigQuery Warehouse Loader Service Account"
  project      = var.project_id
}

resource "google_service_account" "storage_sa" {
  account_id   = "sa-gcs-runner"
  display_name = "Cloud Storage Ingestion Service Account"
  project      = var.project_id
}

resource "google_service_account" "github_sa" {
  account_id   = "sa-github-actions"
  display_name = "GitHub Actions CI/CD Deployer Service Account"
  project      = var.project_id
}

resource "google_service_account" "monitoring_sa" {
  account_id   = "sa-monitoring-emitter"
  display_name = "Cloud Telemetry Emitter Service Account"
  project      = var.project_id
}

resource "google_service_account" "migration_sa" {
  account_id   = "sa-database-migration"
  display_name = "MySQL to AlloyDB Migration Service Account"
  project      = var.project_id
}

# Role Bindings - Dataproc
resource "google_project_iam_member" "dataproc_worker" {
  project = var.project_id
  role    = "roles/dataproc.worker"
  member  = "serviceAccount:${google_service_account.dataproc_sa.email}"
}

# Role Bindings - BigQuery
resource "google_project_iam_member" "bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.bigquery_sa.email}"
}

resource "google_project_iam_member" "bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.bigquery_sa.email}"
}

# Role Bindings - Storage
resource "google_project_iam_member" "storage_user" {
  project = var.project_id
  role    = "roles/storage.objectUser"
  member  = "serviceAccount:${google_service_account.storage_sa.email}"
}

# Role Bindings - Monitoring
resource "google_project_iam_member" "monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.monitoring_sa.email}"
}

resource "google_project_iam_member" "logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.monitoring_sa.email}"
}

# Role Bindings - Migration
resource "google_project_iam_member" "migration_admin" {
  project = var.project_id
  role    = "roles/datastream.admin"
  member  = "serviceAccount:${google_service_account.migration_sa.email}"
}
