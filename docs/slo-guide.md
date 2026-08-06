# Service Level Objectives (SLO) & Error Budget Guide

This guide details the SLO metrics, target thresholds, and Error Budget management calculated by `SLACalculator`.

---

## 🎯 1. Target Service Level Objectives

| SLO Name | Target (%) | Window | Metric Description |
| --- | --- | --- | --- |
| **Platform System Availability** | **99.9%** | 30 Days | Successful pipeline run availability |
| **ETL Processing Latency** | **95.0%** | 7 Days | 95% of Silver batch loads complete within 5 minutes |
| **Gold Data Freshness SLA** | **99.0%** | 30 Days | Gold warehouse updated within 60 minutes of raw arrival |
| **Pipeline Job Success Rate** | **99.5%** | 30 Days | Percentage of pipeline runs completed without unhandled exceptions |
| **Recovery Time Objective (MTTR)** | **< 15.0 mins** | N/A | Target recovery time objective for pipeline failures or cutover rollbacks |

---

## 💸 2. Error Budget Management

For a **99.9% Availability SLO** over a 30-day window, the total allowable downtime / failure budget is **0.1%** (~43 minutes per month).

- **1-Hour Burn Rate Threshold (14.4x)**: Consumes 2% of monthly budget in 1 hour. Fires `CRITICAL` alert to On-Call SREs.
- **6-Hour Burn Rate Threshold (6.0x)**: Consumes 5% of monthly budget in 6 hours. Fires `HIGH` alert to Data Engineering team.
