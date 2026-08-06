variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP Deployment Region"
  default     = "us-central1"
}

variable "vpc_name" {
  type        = string
  description = "VPC Network Name"
  default     = "vpc-data-platform"
}

variable "subnet_cidr" {
  type        = string
  description = "CIDR block for private subnet"
  default     = "10.0.0.0/20"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, test, prod)"
  default     = "dev"
}
