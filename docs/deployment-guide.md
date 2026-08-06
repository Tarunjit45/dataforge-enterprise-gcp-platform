# Deployment & Infrastructure Guide

## Infrastructure as Code (Terraform) Workflow

Infrastructure is managed declaratively via Terraform under `terraform/environments/`.

### Deployment Lifecycle
1. **Pull Request Validation**: GitHub Actions runs `terraform fmt -check` and `terraform validate`.
2. **Terraform Plan**: CI authenticates to GCP via Workload Identity Federation (WIF) OIDC and executes `terraform plan`.
3. **Approval & Apply**: Merging to `main` executes `terraform apply` for production environments.

### Local Terraform Validation

```bash
cd terraform/environments/dev
terraform init -backend=false
terraform validate
```
