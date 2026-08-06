# Operational Runbook RB-103: Platform Disaster Recovery

## Overview
Protocol for executing Disaster Recovery (DR) in the event of a total GCP regional outage or catastrophic data loss.

---

## Recovery Objectives
* **Recovery Point Objective (RPO)**: < 1 hour (AlloyDB point-in-time recovery & GCS bucket versioning).
* **Recovery Time Objective (RTO)**: < 4 hours (Automated Terraform multi-region deployment).

---

## Disaster Recovery Execution Steps

### 1. Provision Infrastructure in Backup Region (`us-east4`)
```bash
cd terraform/environments/prod
terraform apply -var="region=us-east4" -out="dr_region.tfplan"
```

### 2. Restore AlloyDB Transactional Database
```bash
gcloud alloydb clusters restore alloydb-dr-cluster \
    --region=us-east4 \
    --source-cluster=alloydb-cluster-prod \
    --source-region=us-central1 \
    --point-in-time="2026-08-05T20:00:00Z"
```

### 3. Re-point Storage Dual-Region Failover Buckets
Promote secondary dual-region GCS sync buckets to primary Bronze/Silver storage endpoints.
