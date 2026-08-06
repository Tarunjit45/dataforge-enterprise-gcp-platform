# Operational Runbook RB-101: Initial Infrastructure Deployment

## Overview
Standard Operating Procedure (SOP) for deploying the GCP Data Platform landing zone infrastructure via Terraform across target GCP environments (`dev`, `prod`).

---

## Prerequisites
* Authenticated `gcloud` session with `roles/resourcemanager.projectIamAdmin` and `roles/owner` or targeted admin roles on project.
* Terraform CLI 1.7.0+ installed.
* Remote GCS State Storage bucket pre-created.

---

## Execution Steps

### Step 1: Pre-Flight Check
```bash
gcloud config set project enterprise-data-prod-98765
gcloud auth application-default login
```

### Step 2: Initialize & Validate Terraform
```bash
cd terraform/environments/prod
terraform init
terraform fmt -check
terraform validate
```

### Step 3: Terraform Execution Plan
```bash
terraform plan -var-file="terraform.tfvars" -out="prod.tfplan"
```
* **Verify**: Confirm resource additions match expected modules (8 modules, 0 unexpected deletions).

### Step 4: Infrastructure Application
```bash
terraform apply "prod.tfplan"
```

### Step 5: Post-Deployment Smoke Verification
```bash
bash scripts/validate_infrastructure.sh enterprise-data-prod-98765 us-central1
bash scripts/run_smoke_tests.sh enterprise-data-prod-98765 us-central1
```
