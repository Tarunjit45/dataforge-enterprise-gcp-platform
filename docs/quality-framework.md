# Enterprise Data Quality & Governance Framework

The Enterprise Data Quality & Governance Framework is an independent, configuration-driven platform for asserting data quality rules, computing multi-dimensional quality scores, detecting schema drift, generating statistical profiles, and isolating invalid records into Quarantine storage without halting primary ETL pipelines.

---

## 🏛 Framework Architecture

```
[ Input PySpark DataFrame ]
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ DataQualityEngine (engine.py)                               │
│ ├── 1. Execute Assertion Rules (rules/)                     │
│ ├── 2. Profile Statistical Metrics (profiler.py)            │
│ ├── 3. Calculate Weighted DQ Score (scorer.py)             │
│ └── 4. Detect Schema Drift (schema/schema_drift_detector)   │
└────────────┬──────────────────────────────┬─────────────────┘
             │                              │
             ▼                              ▼
┌───────────────────────────┐  ┌───────────────────────────────┐
│ QuarantineRouter           │  │ QualityReporter               │
│ ├── Valid -> Gold         │  │ Generates 5 JSON Reports:     │
│ └── Invalid -> Quarantine │  │ - quality_report.json         │
└───────────────────────────┘  │ - profiling_report.json       │
                               │ - schema_drift_report.json    │
                               │ - quality_score.json          │
                               │ - execution_summary.json      │
                               └───────────────────────────────┘
```

---

## ⚙️ Configuration-Driven Design (`config/quality_rules/nyc_taxi.yaml`)

```yaml
dataset_name: nyc_taxi
version: "1.0"

rules:
  VendorID:
    not_null: true
    allowed_values: [1, 2]

  passenger_count:
    min: 1
    max: 8

  trip_distance:
    min: 0.01
    max: 500.0

  payment_type:
    allowed_values: [1, 2, 3, 4, 5, 6]
```

---

## 📊 Quality Scoring Model (`QualityScore`)

Scores are computed across 3 dimensions:
1. **Completeness (35%)**: `100.0 - Average_Null_Percentage`
2. **Uniqueness (25%)**: `100.0 - Duplicate_Row_Percentage`
3. **Validity (40%)**: `(Passed_Rules / Total_Rules) * 100.0`

**Grade Classification**:
* Grade A: $\ge 90.0\%$
* Grade B: $80.0\% - 89.9\%$
* Grade C: $70.0\% - 79.9\%$
* Grade F: $< 70.0\%$

---

## 🛑 Quarantine Routing

Failed records are captured with lineage metadata columns:
* `_failed_rule`
* `_error_code`
* `_quarantined_at_utc`
* `_execution_id`

Stored to GCS Quarantine Bucket: `gs://<project_id>-quarantine/`
