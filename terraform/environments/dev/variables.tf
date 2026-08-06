variable "project_id" {
  type        = string
  description = "Development GCP Project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "Development Deployment Region"
}

variable "alloydb_password" {
  type        = string
  description = "Initial AlloyDB Admin Password"
  sensitive   = true
}
