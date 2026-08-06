# Automated Backup & Restoration Validation Guide

This guide details the backup management and automated restore validation implemented in `BackupManager` and `RestoreValidator`.

---

## 💾 1. Backup Policies & Retention

| Target Resource | Backup Mechanism | Schedule / Strategy | Retention Period |
| --- | --- | --- | --- |
| **AlloyDB PostgreSQL** | Automated Instance Backups & PITR | Weekly Sunday 02:00 UTC | 4 weekly backups + 14-day PITR |
| **BigQuery Warehouse** | Table Snapshots (`gold_analytics_snapshots`) | Daily Snapshot | 30 Days retention |
| **Cloud Storage (GCS)** | Object Versioning | Real-time version history | Non-current version expiration (30d) |
| **Terraform State** | Versioned GCS State Bucket | Real-time on apply | State history retention enabled |

---

## 🧪 2. Automated Restoration Verification

`RestoreValidator` executes periodic automated restore simulations to confirm backup file integrity and measure restoration duration (`backup_validation.json`).
