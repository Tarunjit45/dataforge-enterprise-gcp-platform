# Operational Runbook RB-102: Infrastructure Rollback Procedure

## Overview
Procedure for rolling back breaking infrastructure modifications or restoring state to a previous known-good git commit.

---

## Rollback Execution Steps

### Scenario A: Minor Resource Drift Rollback
If a recent `terraform apply` introduced unwanted state drift:

```bash
cd terraform/environments/prod
git checkout HEAD~1 terraform/environments/prod/
terraform init
terraform plan -out="rollback.tfplan"
terraform apply "rollback.tfplan"
```

### Scenario B: Complete Module State Restore
If state file corruption or destructive changes occurred:

```bash
# 1. Retrieve historical state file version from GCS backend versioning
gcloud storage ls --all-versions gs://enterprise-prod-tfstate/terraform/state/default.tfstate

# 2. Restore prior state version
gcloud storage cp gs://enterprise-prod-tfstate/terraform/state/default.tfstate#<VERSION_ID> local_state.tfstate
terraform state push local_state.tfstate
```
