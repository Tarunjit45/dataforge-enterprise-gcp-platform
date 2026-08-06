# Enterprise Data Ingestion Framework

The Enterprise Data Ingestion Framework provides an extensible, connector-driven architecture for fetching external datasets, validating raw payloads, generating standardized metadata & manifest JSON files, and staging payload assets to the GCP Cloud Storage Bronze Landing Zone.

---

## 🏛 Framework Architecture & Sequence

```
[ External Source (HTTP / API) ]
              │
              ▼ 1. fetch_payload()
┌───────────────────────────────────────────────────────────┐
│ Connector (e.g. NYCTaxiConnector)                        │
└─────────────┬─────────────────────────────────────────────┘
              │ 2. validate_payload() & SHA256 Checksum
              ▼
┌───────────────────────────────────────────────────────────┐
│ IngestionPipeline Engine                                  │
│ ├── 3. Generate Metadata (MetadataGenerator)             │
│ ├── 4. Upload Raw Payload to GCS Bronze Bucket            │
│ ├── 5. Upload metadata.json to GCS                        │
│ └── 6. Generate & Upload manifest.json to GCS             │
└─────────────┬─────────────────────────────────────────────┘
              │
              ▼
┌───────────────────────────────────────────────────────────┐
│ GCS BRONZE LANDING BUCKET                                 │
│ path: raw/<source>/<entity>/YYYY/MM/DD/                   │
│ ├── payload.parquet                                       │
│ ├── metadata.json                                         │
│ └── manifest.json                                         │
└───────────────────────────────────────────────────────────┘
```

---

## 🔌 Connector Hierarchy

* `BaseConnector` (`src/ingestion/base.py`): Abstract Base Class defining `fetch_payload()`, `validate_payload()`, and SHA256 checksum calculation.
* `HTTPConnector` (`src/ingestion/connectors/http.py`): Reusable base connector for fetching files over HTTP/HTTPS with automatic retry handling (`@retry_on_exception`).
* `NYCTaxiConnector` (`src/ingestion/connectors/nyc_taxi.py`): Concrete connector for downloading NYC TLC Yellow Taxi trip datasets.

---

## 📄 Metadata & Manifest Specifications

### `metadata.json`
```json
{
  "source_name": "nyc_tlc",
  "entity_name": "yellow_taxi",
  "file_name": "yellow_tripdata_2024_01.parquet",
  "file_size_bytes": 48320112,
  "sha256_checksum": "a8f3b2c...5d9",
  "content_type": "application/x-parquet",
  "ingested_at_utc": "2026-08-05T23:30:00.000000+00:00",
  "schema_version": "1.0"
}
```

### `manifest.json`
```json
{
  "manifest_version": "1.0",
  "execution_id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "status": "SUCCESS",
  "source": "nyc_tlc",
  "entity": "yellow_taxi",
  "gcs_payload_uri": "gs://enterprise-dev-raw-bronze/raw/nyc_tlc/yellow_taxi/2024/01/01/yellow_tripdata_2024_01.parquet",
  "checksum_sha256": "a8f3b2c...5d9",
  "payload_bytes": 48320112,
  "timestamp_utc": "2026-08-05T23:30:01.000000+00:00"
}
```

---

## 🚀 Adding a New Connector

To create a new ingestion source connector:
1. Inherit from `BaseConnector` or `HTTPConnector` under `src/ingestion/connectors/`.
2. Implement `fetch_payload(target_date, output_dir)` and `validate_payload(payload)`.
3. Export your connector class in `src/ingestion/connectors/__init__.py`.
