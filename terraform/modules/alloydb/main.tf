# AlloyDB Module: Cluster, Primary Instance, Read Pool Instance, Private Network Peering & Backups

resource "google_alloydb_cluster" "cluster" {
  cluster_id = "alloydb-cluster-${var.environment}"
  location   = var.region
  project    = var.project_id

  network_config {
    network = var.vpc_id
  }

  initial_user {
    password = var.initial_user_password
  }

  automated_backup_policy {
    location = var.region
    weekly_schedule {
      days_of_week = ["SUNDAY"]
      start_times {
        hours   = 2
        minutes = 0
      }
    }
    quantity_based_expiry {
      retention_count = 4
    }
  }

  labels = local.common_labels
}

resource "google_alloydb_instance" "primary" {
  cluster       = google_alloydb_cluster.cluster.name
  instance_id   = "alloydb-primary-${var.environment}"
  instance_type = "PRIMARY"

  cpu_count = var.cpu_count

  database_flags = {
    "password_encryption" = "scram-sha-256"
  }

  labels = local.common_labels
}

resource "google_alloydb_instance" "read_pool" {
  cluster       = google_alloydb_cluster.cluster.name
  instance_id   = "alloydb-read-pool-${var.environment}"
  instance_type = "READ_POOL"

  cpu_count = var.cpu_count

  read_pool_config {
    node_count = var.read_pool_node_count
  }

  labels = local.common_labels

  depends_on = [google_alloydb_instance.primary]
}
