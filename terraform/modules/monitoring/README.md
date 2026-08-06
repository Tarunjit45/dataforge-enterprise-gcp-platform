# Monitoring Terraform Module

Provisions Cloud Monitoring alert policies, notification channels, Cloud Logging audit sinks, and operational dashboards.

## Resources
* `google_monitoring_notification_channel.email_channel`: Email alert channel.
* `google_monitoring_alert_policy.dataproc_failure_alert`: P1 Critical alert policy for Dataproc execution failure.
* `google_logging_project_sink.audit_sink`: Cloud Audit Log export to GCS storage sink.
* `google_monitoring_dashboard.platform_dashboard`: Custom telemetry dashboard.
