output "dataproc_sa_email" {
  value       = google_service_account.dataproc_sa.email
  description = "Dataproc Service Account Email"
}

output "bigquery_sa_email" {
  value       = google_service_account.bigquery_sa.email
  description = "BigQuery Service Account Email"
}

output "storage_sa_email" {
  value       = google_service_account.storage_sa.email
  description = "Cloud Storage Service Account Email"
}

output "github_sa_email" {
  value       = google_service_account.github_sa.email
  description = "GitHub Actions Service Account Email"
}

output "monitoring_sa_email" {
  value       = google_service_account.monitoring_sa.email
  description = "Monitoring Service Account Email"
}

output "migration_sa_email" {
  value       = google_service_account.migration_sa.email
  description = "Migration Service Account Email"
}
