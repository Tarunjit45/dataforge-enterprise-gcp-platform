variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP Deployment Region"
  default     = "us-central1"
}

variable "subnet_name" {
  type        = string
  description = "VPC Subnet Name for Dataproc nodes"
}

variable "staging_bucket_name" {
  type        = string
  description = "GCS Staging Bucket Name for Dataproc"
}

variable "dataproc_sa_email" {
  type        = string
  description = "Service Account email for Dataproc cluster"
}

variable "master_machine_type" {
  type        = string
  default     = "n2-standard-4"
  description = "Machine type for Dataproc Master node"
}

variable "worker_machine_type" {
  type        = string
  default     = "n2-standard-4"
  description = "Machine type for Dataproc Worker nodes"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, test, prod)"
  default     = "dev"
}
