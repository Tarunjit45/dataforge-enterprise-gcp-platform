# Emergency Migration Rollback Operational Runbook

This runbook outlines emergency recovery procedures when a migration cutover or validation fails using `RollbackEngine`.

---

## 🚨 Rollback Trigger Criteria

Rollback must be triggered immediately if any of the following conditions occur:
1. `migration_validation.json` fails row count or SHA256 checksum checks during pre-cutover gating.
2. Application query errors spike > 1% immediately following connection switchover.
3. Severe unexpected query latency regressions (> 5x baseline) occur on AlloyDB.

---

## 🔄 Emergency Rollback Execution Sequence

### Step 1: Revert Application Connections back to MySQL
Update application configuration or DNS endpoints to point traffic back to original MySQL master database:
```python
from src.migration.rollback import RollbackEngine

rollback = RollbackEngine()
plan = rollback.generate_rollback_plan(
    trigger_reason="High error rate post-cutover",
    target_tables=["customers", "vendors", "locations", "trips"]
)
rollback.execute_rollback(plan)
```

### Step 2: Teardown Datastream CDC Stream
Pause and delete Google Cloud Datastream stream to halt replication:
```bash
gcloud datastream streams stop ds-mysql-to-alloydb --location=us-central1
```

### Step 3: Target Cleanup or Point-In-Time Restoration
- If target AlloyDB cluster was corrupted, restore cluster from pre-migration backup snapshot (`pre_migration_snap_dev`).
- Inspect `rollback_plan.json` artifact for full incident audit details.
