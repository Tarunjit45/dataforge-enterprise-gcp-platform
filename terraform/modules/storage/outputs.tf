output "bronze_bucket_name" {
  value       = google_storage_bucket.bronze_landing.name
  description = "Bronze Raw Landing Bucket Name"
}

output "silver_bucket_name" {
  value       = google_storage_bucket.silver_processed.name
  description = "Silver Processed Bucket Name"
}

output "gold_bucket_name" {
  value       = google_storage_bucket.gold_artifacts.name
  description = "Gold Artifact Bucket Name"
}

output "quarantine_bucket_name" {
  value       = google_storage_bucket.quarantine.name
  description = "Quarantine Bucket Name"
}

output "logs_bucket_name" {
  value       = google_storage_bucket.logs.name
  description = "Logs Storage Bucket Name"
}
