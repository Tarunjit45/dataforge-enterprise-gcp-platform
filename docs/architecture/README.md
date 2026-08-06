# System Architecture Blueprint

This directory houses the formal technical design documents for the Enterprise GCP Data Platform.

## Core System Architecture

Refer to the primary architectural specification for detailed requirements:
* **GCP Services**: GCS Data Lake, Ephemeral Dataproc PySpark, BigQuery Data Warehouse, AlloyDB for PostgreSQL.
* **Migration Target**: Legacy MySQL to AlloyDB via CDC and initial bulk copy.
* **Data Pipelines**: Raw Bronze landing $\rightarrow$ Silver PySpark cleansing & quality assertions $\rightarrow$ Gold BigQuery Star Schema.
* **Governance**: Automated Quarantine router for non-compliant records.

For the baseline technical design specification, see `technical_design_document.md`.
