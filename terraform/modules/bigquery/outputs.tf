output "raw_staging_dataset_id" {
  value       = google_bigquery_dataset.raw_staging.dataset_id
  description = "Raw Staging Dataset ID"
}

output "silver_cleansed_dataset_id" {
  value       = google_bigquery_dataset.silver_cleansed.dataset_id
  description = "Silver Cleansed Dataset ID"
}

output "gold_analytics_dataset_id" {
  value       = google_bigquery_dataset.gold_analytics.dataset_id
  description = "Gold Analytics Dataset ID"
}

output "monitoring_telemetry_dataset_id" {
  value       = google_bigquery_dataset.monitoring_telemetry.dataset_id
  description = "Monitoring Telemetry Dataset ID"
}
