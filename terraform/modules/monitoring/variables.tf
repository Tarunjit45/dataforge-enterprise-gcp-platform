variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "alert_email_address" {
  type        = string
  description = "Email address for P1 failure alert notifications"
  default     = "data-alerts@enterprise.com"
}

variable "logs_bucket_name" {
  type        = string
  description = "GCS bucket name for long-term audit log sink"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, test, prod)"
  default     = "dev"
}
