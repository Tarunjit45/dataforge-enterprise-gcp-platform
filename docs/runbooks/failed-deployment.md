# Operational Runbook RB-104: Failed Deployment Triage

## Overview
Diagnostic procedures when a Terraform execution fails midway due to API quotas, IAM permissions, or network locks.

---

## Triage Protocol

1. **Unlock State File**:
   If a deployment failure leaves the Terraform backend locked:
   ```bash
   terraform force-unlock <LOCK_ID>
   ```

2. **Isolate Failed Resource**:
   Identify the failing resource address from the CLI error log (e.g. `module.alloydb.google_alloydb_instance.primary`).

3. **Re-run Target Refresh**:
   ```bash
   terraform refresh
   terraform plan -target=module.alloydb
   ```
