variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP Region for KMS Keyring"
  default     = "us-central1"
}

variable "keyring_name" {
  type        = string
  description = "KMS Keyring Name"
  default     = "data-platform-keyring"
}

variable "key_rotation_period" {
  type        = string
  description = "Rotation period for KMS crypto keys (e.g. 7776000s = 90 days)"
  default     = "7776000s"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, test, prod)"
  default     = "dev"
}
