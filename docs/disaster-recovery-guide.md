# Multi-Region Disaster Recovery (DR) & Failover Guide

This guide details multi-region disaster recovery failover procedures (`us-central1` $\rightarrow$ `us-east4`) and RPO/RTO validation implemented in `DisasterRecoveryEngine`.

---

## 🌐 1. RPO & RTO SLA Targets

- **Recovery Point Objective (RPO)**: **< 5.0 Minutes** (Maximum allowable data loss window)
- **Recovery Time Objective (RTO)**: **< 15.0 Minutes** (Maximum allowable service outage window)

---

## 🔄 2. Multi-Region Failover Strategy

| Resource | Failover Strategy | Target Region |
| --- | --- | --- |
| **AlloyDB PostgreSQL** | Cross-region read pool promotion | `us-east4` |
| **BigQuery Gold Warehouse** | Cross-region dataset replication | `us-east4` |
| **Cloud Storage** | Dual-region bucket configuration (`NAM4`) | Multi-region |
| **Dataproc PySpark** | Ephemeral cluster recreation via Terraform | `us-east4` |
