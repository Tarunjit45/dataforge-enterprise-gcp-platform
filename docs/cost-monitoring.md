# FinOps & GCP Cost Observability Guide

This guide details GCP cost tracking and estimation calculated by `CostObservabilityEngine`.

---

## 💰 1. Unit Pricing & Spend Models

| Service | Metric Unit | Unit Rate (USD) | Optimization Strategy |
| --- | --- | --- | --- |
| **BigQuery Analytics** | Terabyte (TB) Scanned | $6.25 / TB | Enforce partition pruning on `trip_date` & clustering keys |
| **Dataproc PySpark** | vCPU Hour | $0.0475 / vCPU-hr | Enable dynamic cluster auto-scaling & preemptible workers |
| **Cloud Storage (GCS)** | Gigabyte (GB) Month | $0.02 / GB-month | Configure GCS lifecycle rules to transition raw files to Nearline after 30 days |
| **AlloyDB PostgreSQL** | vCPU Hour | $0.088 / vCPU-hr | Scale down read pool nodes during off-peak hours |
| **Network Egress** | Gigabyte (GB) | $0.12 / GB | Keep cross-service traffic within `us-central1` private VPC |

---

## 📈 2. Cost Reports & Anomaly Detection

- `cost_report.json`: Formatted JSON artifact generated daily containing itemized service costs and estimated monthly spend.
- **Cost Anomaly Threshold**: Triggers `high_cost_anomaly` alert if estimated daily spend exceeds **$150.0 USD** (>150% baseline).
