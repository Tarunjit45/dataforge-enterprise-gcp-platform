variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP Deployment Region"
  default     = "us-central1"
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
