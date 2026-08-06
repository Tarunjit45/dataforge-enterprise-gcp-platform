# System Configuration Reference Guide

Overview of system configuration settings and YAML control files.

---

## ⚙️ 1. Environment Variable Settings

System configuration is driven by `src/common/config/settings.py` (BaseSettings):

| Variable Name | Environment Default | Description |
| --- | --- | --- |
| `GCP_PROJECT_ID` | `my-gcp-project` | Target Google Cloud Platform Project ID |
| `GCP_REGION` | `us-central1` | Primary GCP compute and storage region |
| `ENVIRONMENT` | `dev` | Target environment (`dev`, `staging`, `prod`) |
| `LOG_LEVEL` | `INFO` | System logging verbosity level |

---

## 📄 2. Policy Configuration Files (`config/`)

- `config/quality_rules/rules.yaml`: Data quality assertion thresholds and quarantine rules.
- `config/migration/migration_config.yaml`: MySQL to AlloyDB table mappings and CDC options.
- `config/observability/`: Metrics, alert policies, Cloud Monitoring dashboards, SLOs, and logging format.
- `config/operations/`: IAM least privilege policies, backup schedules, DR failover rules, chaos experiments, and SLAs.
