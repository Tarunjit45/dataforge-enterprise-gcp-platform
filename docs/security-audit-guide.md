# IAM Security & Service Account Audit Guide

This guide details the least privilege IAM audit policies, primitive role restrictions, and Workload Identity validation implemented in `IAMAuditEngine` and `SecurityPostureEngine`.

---

## 🔒 1. Disallowed Primitive Roles

Primitive roles grant overly broad permissions across entire projects and are **strictly prohibited**:
- `roles/owner` ❌
- `roles/editor` ❌
- `roles/viewer` ❌

All service accounts must utilize fine-grained IAM roles (e.g. `roles/dataproc.worker`, `roles/bigquery.dataEditor`, `roles/alloydb.client`).

---

## 🔑 2. Workload Identity & Keyless Authentication

Service accounts used in GitHub Actions CI/CD pipelines authenticate using **Google Cloud Workload Identity Federation** rather than static `.json` keyfiles.

- **Pool**: `github-actions-pool`
- **Provider**: `github-actions-provider`
- **Attribute Mapping**: `google.subject=assertion.sub, attribute.repository=assertion.repository`
