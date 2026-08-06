# Production Cutover Operational Runbook (MySQL → AlloyDB)

This operational runbook provides step-by-step instructions for executing a zero-downtime / minimal-downtime production cutover from MySQL to Google Cloud AlloyDB using `CutoverOrchestrator`.

---

## 📋 Pre-Cutover Requirements & Gatekeeping

Before initiating cutover, verify that:
1. `migration_validation.json` status is **100% PASSED** across all migrated tables.
2. Datastream CDC continuous replication lag is **$\le 5$ seconds**.
3. AlloyDB Primary Instance and Read Pool instances are healthy.
4. Application deployment team is ready to trigger connection string switchover.

---

## 🚀 Execution Steps

### Step 1: Pre-Cutover Verification Checklist
Run automated checklist verification:
```python
from src.migration.cutover import CutoverOrchestrator

orchestrator = CutoverOrchestrator(max_allowable_lag_seconds=5.0)
checklist = orchestrator.execute_pre_cutover_checklist(validation_results, replication_lag_seconds=1.2)
```

### Step 2: Enable Maintenance Mode & Flush Source Buffer
- Put application into Maintenance / Read-Only mode to prevent new MySQL writes.
- Wait for Datastream CDC binlog replication lag to reach **0.0 seconds**.

### Step 3: Execute Cutover Switchover
```python
status = orchestrator.execute_cutover(validation_results, replication_lag_seconds=0.0)
```

### Step 4: Validate Target AlloyDB Traffic & Sign-off
- Verify active application connections against AlloyDB Primary endpoint.
- Inspect application health metrics and query latency logs.
- Generate `cutover_report.json` and publish executive summary.
