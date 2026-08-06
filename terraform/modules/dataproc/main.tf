# Dataproc Module: Ephemeral Spark Workflow Template, Autoscaling Policy & Private Cluster Config

resource "google_dataproc_autoscaling_policy" "ephemeral_policy" {
  policy_id = "dataproc-ephemeral-autoscaling-${var.environment}"
  location  = var.region
  project   = var.project_id

  basic_algorithm {
    yarn_config {
      graceful_decommission_timeout = "600s"
      scale_up_factor               = 0.5
      scale_down_factor             = 0.5

      scale_up_min_worker_fraction   = 0.0
      scale_down_min_worker_fraction = 0.0
    }
  }

  worker_config {
    min_instances = 2
    max_instances = 10
  }

  secondary_worker_config {
    min_instances = 0
    max_instances = 50
  }
}

resource "google_dataproc_workflow_template" "ephemeral_template" {
  name     = "ephemeral-pyspark-job-${var.environment}"
  location = var.region
  project  = var.project_id

  placement {
    managed_cluster {
      cluster_name = "ephemeral-spark-${var.environment}"

      config {
        staging_bucket = var.staging_bucket_name

        gcmd_compute_targeted_service_accounts = [
          var.dataproc_sa_email
        ]

        gce_cluster_config {
          zone                   = "${var.region}-a"
          subnetwork             = var.subnet_name
          internal_ip_only       = true
          service_account        = var.dataproc_sa_email
          service_account_scopes = [
            "https://www.googleapis.com/auth/cloud-platform"
          ]

          tags = ["dataproc-internal"]
        }

        master_config {
          num_instances = 1
          machine_type  = var.master_machine_type
          disk_config {
            boot_disk_type    = "pd-standard"
            boot_disk_size_gb = 100
          }
        }

        worker_config {
          num_instances = 2
          machine_type  = var.worker_machine_type
          disk_config {
            boot_disk_type    = "pd-standard"
            boot_disk_size_gb = 100
          }
        }

        secondary_worker_config {
          num_instances = 2
        }

        autoscaling_config {
          policy = google_dataproc_autoscaling_policy.ephemeral_policy.id
        }

        software_config {
          image_version = "2.1-debian11"
          override_properties = {
            "dataproc:dataproc.logging.stackdriver.enable" = "true"
          }
        }
      }

      labels = local.common_labels
    }
  }
}
