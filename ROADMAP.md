# Platform Engineering Roadmap

This document outlines upcoming planned features and architectural enhancements for the Enterprise GCP Data Platform.

---

## 🚀 Q3 2026 - Real-Time Streaming & Event-Driven Architecture
- [ ] Integration of Apache Kafka / GCP Pub/Sub for real-time streaming ingestion into Bronze layer.
- [ ] PySpark Structured Streaming jobs for sub-second Silver data updates.
- [ ] Real-time Data Quality assertions on streaming event streams.

---

## ⚡ Q4 2026 - Apache Iceberg & Open Table Formats
- [ ] Migration of GCS Silver storage format from Apache Parquet to Apache Iceberg.
- [ ] Time-travel query support on GCS lakehouse tables.
- [ ] Automated compaction and maintenance jobs for Iceberg tables.

---

## 🤖 Q1 2027 - MLOps & Feature Store Integration
- [ ] Integration of GCP Vertex AI Feature Store backed by BigQuery Gold tables.
- [ ] Automated feature drift detection in PySpark ETL pipelines.
- [ ] Automated ML model retraining triggers based on Gold warehouse updates.
