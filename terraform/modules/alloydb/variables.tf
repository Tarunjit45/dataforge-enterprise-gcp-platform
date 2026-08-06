variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP Deployment Region"
  default     = "us-central1"
}

variable "vpc_id" {
  type        = string
  description = "Private VPC Network ID for AlloyDB peering"
}

variable "initial_user_password" {
  type        = string
  description = "Password for postgres admin user"
  sensitive   = true
}

variable "cpu_count" {
  type        = number
  description = "CPU core allocation per instance"
  default     = 4
}

variable "read_pool_node_count" {
  type        = number
  description = "Number of nodes in high availability read pool"
  default     = 2
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, test, prod)"
  default     = "dev"
}
