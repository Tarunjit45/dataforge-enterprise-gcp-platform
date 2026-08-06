# Production Infrastructure & Pipeline Deployment Guide

This guide describes how to deploy the Enterprise GCP Data Platform across `dev`, `staging`, and `prod` environments.

---

## 🏗 1. Automated Deployment via GitHub Actions

The platform uses GitHub Actions CD pipeline ([`.github/workflows/cd.yml`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/.github/workflows/cd.yml)):

```
Push to main ──► Workload Identity Auth ──► Terraform Apply ──► App Deploy ──► Smoke Tests ──► Success / Auto-Rollback
```

---

## 🛠 2. Manual CLI Deployment via Terraform & Scripts

### Initialize & Deploy Environment Infrastructure
```bash
cd terraform/environments/dev
terraform init
terraform apply -var-file=terraform.tfvars -auto-approve
```

### Deploy Pipelines & Application Packages
```bash
bash scripts/deploy.sh dev
```

### Execute Post-Deployment Smoke Tests
```bash
bash scripts/smoke_tests.sh dev my-gcp-project us-central1
```
