output "vpc_id" {
  value       = google_compute_network.vpc.id
  description = "VPC Network ID"
}

output "vpc_name" {
  value       = google_compute_network.vpc.name
  description = "VPC Network Name"
}

output "subnet_id" {
  value       = google_compute_subnetwork.private_subnet.id
  description = "Private Subnet ID"
}

output "subnet_name" {
  value       = google_compute_subnetwork.private_subnet.name
  description = "Private Subnet Name"
}
