variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "location" {
  type        = string
  description = "BigQuery Dataset Location"
  default     = "US"
}

variable "kms_crypto_key_id" {
  type        = string
  description = "Cloud KMS Key ID for CMEK encryption"
  default     = null
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, test, prod)"
  default     = "dev"
}
