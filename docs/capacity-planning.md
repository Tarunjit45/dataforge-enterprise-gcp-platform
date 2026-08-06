# Multi-Year Capacity Planning & Resource Growth Guide

This guide details 1-year and 3-year capacity growth projections calculated by `CapacityPlanningEngine`.

---

## 📈 1. Multi-Year Growth Projections

Assumed baseline: **1.5 TB / month** initial ingestion with an estimated **8% monthly growth rate**.

| Resource Category | Baseline (Current) | 1-Year Projection | 3-Year Projection |
| --- | --- | --- | --- |
| **Monthly Ingestion Volume** | 1.5 TB / mo | **3.78 TB / mo** | **23.99 TB / mo** |
| **Total Cumulative GCS Storage** | 1.5 TB | **31.75 TB** | **604.55 TB** |
| **Dataproc Compute (vCPU-hrs)** | 120.0 hrs / mo | **302.4 hrs / mo** | **1,919.2 hrs / mo** |
| **BigQuery Recommended Slots** | 500 slots | **740 slots** | **1,220 slots** |
| **AlloyDB Read Pool Nodes** | 1 node | **2 nodes** | **4 nodes** |
| **Network Egress Volume** | 50.0 GB / mo | **126.0 GB / mo** | **799.7 GB / mo** |
