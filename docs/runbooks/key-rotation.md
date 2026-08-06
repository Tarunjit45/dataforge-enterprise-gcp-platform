# Operational Runbook RB-106: Cloud KMS Key Rotation & Re-encryption

## Overview
Procedure for verifying automated 90-day Cloud KMS CryptoKey rotations and executing manual key re-encryption for CMEK storage buckets.

---

## Execution Steps

### 1. Trigger Manual Key Version Rotation
```bash
gcloud kms keys versions create \
    --key=cmek-storage-key \
    --keyring=data-platform-keyring \
    --location=us-central1 \
    --project=enterprise-data-prod-98765
```

### 2. Set Primary Key Version
```bash
gcloud kms keys set-primary-version cmek-storage-key \
    --version=2 \
    --keyring=data-platform-keyring \
    --location=us-central1 \
    --project=enterprise-data-prod-98765
```

Existing GCS objects remain readable via key version 1; new writes automatically encrypt using key version 2.
