# Enterprise GCP Data Platform Monitoring & Observability Architecture

The Enterprise Monitoring & Observability Platform provides centralized structured logging, custom metrics aggregation, OpenTelemetry distributed tracing, automated health pings, alert policy evaluations, SLA/SLO error budget tracking, Cloud Monitoring dashboards, and FinOps cost observability across the entire GCP Data Platform.

---

## 🏛 1. Observability Platform Architecture

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TELEMETRY PRODUCERS & ENGINE HOOKS                                │
│  Ingestion Engine │ PySpark ETL │ Quality Framework │ Gold Warehouse │ AlloyDB Migration │ CI/CD   │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           TelemetryManager (src/observability/telemetry.py)                       │
│  ├── TelemetryLogger (logging.py): JSON Formatter + Correlation/Execution/Batch/Trace IDs         │
│  ├── MetricsCollector (metrics.py): Gauge / Counter / Histogram Metrics Registry                  │
│  └── OpenTelemetryTracer (tracing.py): Span Context & Trace ID Propagation                        │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                ┌──────────────────────────────────┼──────────────────────────────────┐
                │                                  │                                  │
                ▼                                  ▼                                  ▼
┌───────────────────────────────┐  ┌───────────────────────────────┐  ┌───────────────────────────────┐
│     CloudLoggingExporter      │  │    CloudMonitoringExporter    │  │    OpenTelemetryExporter     │
│ (exporters/cloud_logging.py)  │  │(exporters/cloud_monitoring.py)│  │ (exporters/opentelemetry.py)  │
│ └── Google Cloud Logging API  │  │ └── Google Cloud Monitoring   │  │ └── GCP Cloud Trace / OTel    │
└───────────────────────────────┘  └───────────────────────────────┘  └───────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              ANALYSIS, ALERTING & FINOPS ENGINES                                  │
│  ├── ServiceHealthChecker (health_checks.py): GCS, Dataproc, BQ, AlloyDB, Datastream, IAM pings   │
│  ├── AlertEvaluator (alerting.py): Evaluates metric thresholds against alert_policies.yaml        │
│  ├── SLACalculator (sla.py): Availability %, Latency, Freshness, MTTR, & Error Budget burn rate   │
│  ├── CostObservabilityEngine (cost_monitor.py): FinOps daily and monthly spend calculations       │
│  └── DashboardGenerator (dashboards.py): Executive, Ops, ETL, Migration, Infra, Cost Dashboards   │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 OPERATIONAL REPORT ARTIFACTS                                      │
│  ├── health_report.json          ├── pipeline_metrics.json          ├── cost_report.json            │
│  ├── sla_report.json             └── dashboard_summary.json                                       │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 2. Core Observability Modules

| Module | File Location | Key Functionality |
| --- | --- | --- |
| **Structured Logger** | [`logging.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/observability/logging.py) | Emits Google Cloud Logging compliant JSON logs with mandatory `correlation_id`, `execution_id`, `batch_id`, `trace_id`, and error taxonomy. |
| **Metrics Collector** | [`metrics.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/observability/metrics.py) | Registers and aggregates platform counters, gauges, and histograms (`pipeline_duration`, `records_processed`, `records_rejected`, `dq_score`, `quarantine_rate`, `cdc_lag`). Outputs `pipeline_metrics.json`. |
| **OpenTelemetry Tracer** | [`tracing.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/observability/tracing.py) | Manages OTel span lifecycles, duration measurements, and distributed trace context propagation. |
| **Unified Telemetry** | [`telemetry.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/observability/telemetry.py) | Single facade wrapping logging, metrics, and tracing into context-aware execution blocks. |
| **Health Checks** | [`health_checks.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/observability/health_checks.py) | Automated health pings for GCS, Dataproc, BigQuery, AlloyDB, Datastream, IAM, and Terraform backend. Outputs `health_report.json`. |
| **Alerting Evaluator** | [`alerting.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/observability/alerting.py) | Evaluates metrics against rules in [`alert_policies.yaml`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/config/observability/alert_policies.yaml) and fires alert notifications. |
| **Dashboard Generator** | [`dashboards.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/observability/dashboards.py) | Generates Cloud Monitoring JSON specs for Executive, Ops, ETL, Migration, Infrastructure, and Cost dashboards. Outputs `dashboard_summary.json`. |
| **SLA / SLO Calculator** | [`sla.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/observability/sla.py) | Calculates Availability %, Data Freshness, Latency, MTTR, and Error Budget consumption. Outputs `sla_report.json`. |
| **Cost Monitor** | [`cost_monitor.py`](file:///D:/GCP%20PROJECTS/GCP%20Data%20Migration%20&%20ETL%20Pipeline/src/observability/cost_monitor.py) | Calculates FinOps cost breakdowns across BigQuery, Dataproc, GCS, AlloyDB, and Network Egress. Outputs `cost_report.json`. |
| **Exporters** | `exporters/` | Pluggable exporters for Cloud Monitoring, Cloud Logging, Prometheus Exposition format, and OpenTelemetry. |

---

## 📊 3. Output Operational Artifacts

1. `health_report.json`: Real-time health status pings across 7 critical GCP services.
2. `pipeline_metrics.json`: Aggregated counters, gauges, and histograms for active execution runs.
3. `cost_report.json`: FinOps cost breakdown and estimated monthly GCP spend.
4. `sla_report.json`: SLO compliance metrics, Availability %, Freshness SLA, and remaining Error Budget %.
5. `dashboard_summary.json`: Exported Cloud Monitoring JSON specs for all 6 operational dashboards.
