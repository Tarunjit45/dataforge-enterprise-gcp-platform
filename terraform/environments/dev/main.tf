# Terraform Development Environment Root Module Orchestration

terraform {
  required_version = ">= 1.7.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.25.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "security" {
  source      = "../../modules/security"
  project_id  = var.project_id
  region      = var.region
  environment = "dev"
}

module "networking" {
  source      = "../../modules/networking"
  project_id  = var.project_id
  region      = var.region
  environment = "dev"
}

module "iam" {
  source      = "../../modules/iam"
  project_id  = var.project_id
  environment = "dev"
}

module "storage" {
  source            = "../../modules/storage"
  project_id        = var.project_id
  region            = var.region
  kms_crypto_key_id = module.security.storage_crypto_key_id
  environment       = "dev"
}

module "bigquery" {
  source            = "../../modules/bigquery"
  project_id        = var.project_id
  location          = "US"
  kms_crypto_key_id = module.security.bigquery_crypto_key_id
  environment       = "dev"
}

module "dataproc" {
  source              = "../../modules/dataproc"
  project_id          = var.project_id
  region              = var.region
  subnet_name         = module.networking.subnet_name
  staging_bucket_name = module.storage.gold_bucket_name
  dataproc_sa_email   = module.iam.dataproc_sa_email
  environment         = "dev"
}

module "alloydb" {
  source                = "../../modules/alloydb"
  project_id            = var.project_id
  region                = var.region
  vpc_id                = module.networking.vpc_id
  initial_user_password = var.alloydb_password
  environment           = "dev"
}

module "monitoring" {
  source           = "../../modules/monitoring"
  project_id       = var.project_id
  logs_bucket_name = module.storage.logs_bucket_name
  environment      = "dev"
}
