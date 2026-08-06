output "alert_policy_id" {
  value       = google_monitoring_alert_policy.dataproc_failure_alert.id
  description = "Monitoring Alert Policy ID"
}

output "notification_channel_id" {
  value       = google_monitoring_notification_channel.email_channel.id
  description = "Notification Channel ID"
}

output "audit_sink_writer_identity" {
  value       = google_logging_project_sink.audit_sink.writer_identity
  description = "Log Sink Writer Identity Service Account"
}
