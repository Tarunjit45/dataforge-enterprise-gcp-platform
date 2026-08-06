#!/usr/bin/env bash
set -euo pipefail

echo "==> Running Terraform Formatting Check..."
terraform fmt -check -recursive terraform/

echo "==> Validating Dev Environment..."
(cd terraform/environments/dev && terraform init -backend=false && terraform validate)

echo "==> Validating Prod Environment..."
(cd terraform/environments/prod && terraform init -backend=false && terraform validate)

echo "==> Terraform validation completed successfully."
