# Operational Runbook RB-105: Secret Rotation Protocol

## Overview
Instructions for zero-downtime rotation of Database Passwords and Service Account credentials stored in Secret Manager.

---

## Execution Steps

### 1. Generate New AlloyDB Password Version
```bash
NEW_PASSWORD=$(openssl rand -base64 24)

gcloud secrets versions add alloydb-db-credentials \
    --data-file=<(echo -n "${NEW_PASSWORD}") \
    --project=enterprise-data-prod-98765
```

### 2. Update AlloyDB User Password
```bash
gcloud alloydb users update postgres \
    --cluster=alloydb-cluster-prod \
    --region=us-central1 \
    --password="${NEW_PASSWORD}"
```

### 3. Destroy Old Secret Version (After 24-hour Soak Period)
```bash
gcloud secrets versions destroy 1 --secret=alloydb-db-credentials --project=enterprise-data-prod-98765
```
