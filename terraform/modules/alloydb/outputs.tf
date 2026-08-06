output "cluster_id" {
  value       = google_alloydb_cluster.cluster.id
  description = "AlloyDB Cluster ID"
}

output "primary_instance_id" {
  value       = google_alloydb_instance.primary.id
  description = "AlloyDB Primary Instance ID"
}

output "primary_ip_address" {
  value       = google_alloydb_instance.primary.ip_address
  description = "AlloyDB Primary Instance Private IP"
}

output "read_pool_ip_address" {
  value       = google_alloydb_instance.read_pool.ip_address
  description = "AlloyDB Read Pool Private Endpoint IP"
}
