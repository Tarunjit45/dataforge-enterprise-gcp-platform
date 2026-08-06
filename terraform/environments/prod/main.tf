# Terraform Production Environment Root Module Orchestration

terraform {
  required_version = ">= 1.7.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.42.0"
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
  environment = "prod"
}

module "networking" {
  source      = "../../modules/networking"
  project_id  = var.project_id
  region      = var.region
  environment = "prod"
}

module "iam" {
  source      = "../../modules/iam"
  project_id  = var.project_id
  environment = "prod"
}

module "storage" {
  source            = "../../modules/storage"
  project_id        = var.project_id
  region            = var.region
  kms_crypto_key_id = module.security.storage_crypto_key_id
  environment       = "prod"
}

module "bigquery" {
  source            = "../../modules/bigquery"
  project_id        = var.project_id
  location          = "US"
  kms_crypto_key_id = module.security.bigquery_crypto_key_id
  environment       = "prod"
}

module "dataproc" {
  source              = "../../modules/dataproc"
  project_id          = var.project_id
  region              = var.region
  subnet_name         = module.networking.subnet_name
  staging_bucket_name = module.storage.gold_bucket_name
  dataproc_sa_email   = module.iam.dataproc_sa_email
  master_machine_type = "n2-standard-8"
  worker_machine_type = "n2-standard-8"
  environment         = "prod"
}

module "alloydb" {
  source                = "../../modules/alloydb"
  project_id            = var.project_id
  region                = var.region
  vpc_id                = module.networking.vpc_id
  initial_user_password = var.alloydb_password
  cpu_count             = 8
  read_pool_node_count  = 2
  environment           = "prod"
}

module "monitoring" {
  source              = "../../modules/monitoring"
  project_id          = var.project_id
  logs_bucket_name    = module.storage.logs_bucket_name
  alert_email_address = var.alert_email_address
  environment         = "prod"
}
