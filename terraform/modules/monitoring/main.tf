# Monitoring Module: Log Sinks, Alert Policies, Notification Channels, and Dashboard Placeholders

resource "google_monitoring_notification_channel" "email_channel" {
  display_name = "Enterprise Data Engineering Email Alert Channel"
  type         = "email"
  project      = var.project_id

  labels = {
    email_address = var.alert_email_address
  }
}

resource "google_monitoring_alert_policy" "dataproc_failure_alert" {
  display_name = "P1 Critical - Dataproc Job Execution Failure (${var.environment})"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "Dataproc Failed Jobs Count"
    condition_threshold {
      filter          = "resource.type = \"cloud_dataproc_cluster\" AND metric.type = \"dataproc.googleapis.com/job/failed_count\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      aggregations {
        alignment_period = "60s"
        per_series_aligner = "ALIGN_COUNT"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email_channel.name
  ]

  user_labels = local.common_labels
}

resource "google_logging_project_sink" "audit_sink" {
  name        = "data-platform-audit-sink-${var.environment}"
  destination = "storage.googleapis.com/${var.logs_bucket_name}"
  project     = var.project_id
  filter      = "resource.type = (gcs_bucket OR bigquery_dataset OR dataproc_cluster)"

  unique_writer_identity = true
}

resource "google_monitoring_dashboard" "platform_dashboard" {
  project        = var.project_id
  dashboard_json = <<EOF
{
  "displayName": "Platform Operational Telemetry (${var.environment})",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "Dataproc Batch Execution Duration",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"dataproc.googleapis.com/job/duration\""
                }
              }
            }
          ]
        }
      }
    ]
  }
}
EOF
}
