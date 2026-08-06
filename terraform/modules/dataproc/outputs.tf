output "workflow_template_id" {
  value       = google_dataproc_workflow_template.ephemeral_template.id
  description = "Dataproc Workflow Template ID"
}

output "autoscaling_policy_id" {
  value       = google_dataproc_autoscaling_policy.ephemeral_policy.id
  description = "Dataproc Autoscaling Policy ID"
}
