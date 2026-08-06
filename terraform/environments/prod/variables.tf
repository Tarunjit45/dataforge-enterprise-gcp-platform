variable "project_id" {
  type        = string
  description = "Production GCP Project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "Production Deployment Region"
}

variable "alloydb_password" {
  type        = string
  description = "Initial AlloyDB Production Admin Password"
  sensitive   = true
}

variable "alert_email_address" {
  type        = string
  default     = "sre-alerts@enterprise.com"
  description = "P1 Alert Email Address"
}
