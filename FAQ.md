# Frequently Asked Questions (FAQ)

### 1. What dataset is used for the sample pipeline execution?
The platform utilizes the NYC Yellow Taxi Trip Records dataset (or synthetic equivalent conforming to the NYC TLC schema), consisting of pickup/dropoff timestamps, trip distances, fare amounts, payment types, and rate codes.

### 2. Does this platform require long-lived GCP service account keys?
No. All CI/CD and deployment workflows authenticate via **Google Workload Identity Federation**, using short-lived OAuth 2.0 tokens without static key files.

### 3. How does the Data Quality Framework isolate corrupted records?
Records failing critical validation rules (e.g. negative fare amounts, invalid location IDs) are automatically isolated into the GCS Quarantine bucket (`gs://<bucket>/quarantine/`) with attached rule failure metadata (`_failed_rule`, `_failed_timestamp`).

### 4. What PostgreSQL compatibility does AlloyDB provide?
AlloyDB for PostgreSQL is 100% compatible with PostgreSQL 14/15, delivering up to 4x faster performance for transactional workloads and 100x faster analytical queries compared to standard PostgreSQL.

### 5. What unit testing framework is used?
The project uses `pytest` along with `pytest-cov`. All unit tests run locally without active GCP credentials by mocking cloud API clients.
