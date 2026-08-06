# Enterprise PySpark ETL Engine Architecture

The Enterprise PySpark ETL Engine transforms raw Bronze staged datasets into cleansed, deduplicated, enriched Silver datasets stored in partitioned Parquet format on GCS.

---

## 🏛 ETL Engine Architecture

```
[ manifest.json ] ──► BronzeReader ──► Raw DataFrame
                                            │
                                            ▼ SchemaValidator
                                     Validated DataFrame
                                            │
                                            ▼ Generic Cleaning (cleaning.py)
                                     - filter_null_keys()
                                     - normalize_timestamps()
                                     - deduplicate_records()
                                            │
                                            ▼ Business Transformations (nyc_taxi.py)
                                     - pickup_hour, pickup_day, pickup_month
                                     - trip_duration_minutes
                                     - tip_percentage
                                     - average_speed_mph
                                     - weekend_flag, peak_hour_flag
                                            │
                                            ▼ SilverWriter & ETLMetrics
                                     Partitioned Snappy Parquet:
                                     gs://<processed_bucket>/<entity>/pickup_month=MM/
```

---

## ⚡ Performance Optimization Strategy

1. **Manifest-Driven Ingestion**: Reads exclusively from GCS objects registered in `manifest.json`, avoiding costly recursive directory scans.
2. **Column Pruning & Predicate Pushdown**: Only selects columns required downstream prior to applying transformations.
3. **Partitioning**: Silver outputs are partitioned by `pickup_month` to optimize downstream BigQuery load slot usage and query elimination.
4. **Snappy Compression**: All Parquet writes utilize Snappy compression (`option("compression", "snappy")`) for optimal I/O throughput.
5. **Dataproc Dynamic Shuffle**: Configures Kryo serialization and dynamic shuffle partitions (200 partitions for Dataproc managed clusters vs. 4 for local dev).

---

## 📊 Sample Telemetry Metrics Model (`ETLMetrics`)

```json
{
  "execution_id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "source_name": "nyc_tlc",
  "entity_name": "yellow_taxi",
  "records_read": 3000000,
  "records_written": 2985000,
  "invalid_records": 12000,
  "duplicate_records": 3000,
  "partition_count": 12,
  "processing_duration_seconds": 45.2,
  "timestamp_utc": "2026-08-05T23:33:00.000000+00:00"
}
```
