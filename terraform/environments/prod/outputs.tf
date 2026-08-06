output "vpc_id" {
  value       = module.networking.vpc_id
  description = "VPC ID"
}

output "bronze_bucket_name" {
  value       = module.storage.bronze_bucket_name
  description = "Bronze Bucket Name"
}

output "gold_analytics_dataset_id" {
  value       = module.bigquery.gold_analytics_dataset_id
  description = "BigQuery Gold Analytics Dataset ID"
}

output "dataproc_workflow_template_id" {
  value       = module.dataproc.workflow_template_id
  description = "Dataproc Workflow Template ID"
}

output "alloydb_primary_ip" {
  value       = module.alloydb.primary_ip_address
  description = "AlloyDB Primary Private IP"
}
