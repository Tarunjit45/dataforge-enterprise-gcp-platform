# Enterprise BigQuery Gold Warehouse & Analytics Layer Architecture

The Enterprise BigQuery Gold Warehouse provides an enterprise-scale, production-grade dimensional analytics platform built on Google Cloud BigQuery. It consumes validated, deduplicated, and enriched Silver datasets produced by the Phase 7 Data Quality & Governance Framework to deliver a high-performance Star Schema model optimized for executive BI dashboards, ad-hoc exploratory analytics, self-service reporting, and downstream machine learning workloads.

---

## 🏛 1. Warehouse Architecture

```
                               ┌────────────────────────────────────────┐
                               │   Phase 7 Data Quality Framework       │
                               │   (Valid Silver Datasets & Scores)     │
                               └──────────────────┬─────────────────────┘
                                                  │
                                                  ▼
                         ┌─────────────────────────────────────────────────┐
                         │   GoldWarehouseLoader (src/warehouse/loader.py)  │
                         │   - DQ Score Gatekeeper (Min 70% threshold)   │
                         │   - Lineage & Audit Metadata Tracker            │
                         └────────────────────────┬────────────────────────┘
                                                  │
                ┌─────────────────────────────────┴─────────────────────────────────┐
                ▼                                                                   ▼
┌───────────────────────────────┐                                   ┌───────────────────────────────┐
│     Dimension Loaders         │                                   │   Partition-Pruned MERGE Engine   │
│ (load_dimensions.sql)         │                                   │   (incremental_merge.sql)         │
│ ├── SCD Type 1 Updates        │                                   │ ├── Surrogate Key Resolution  │
│ └── SCD Type 2 History        │                                   │ └── Idempotent Fact Upserts   │
└───────────────┬───────────────┘                                   └───────────────┬───────────────┘
                │                                                                   │
                ▼                                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   BigQuery Gold Analytics Dataset                                 │
│                                                                                                   │
│  ┌──────────────┐   ┌─────────────────────────────────────────────────────────┐   ┌─────────────┐ │
│  │ DIM_CUSTOMER │   │                    FACT_TAXI_TRIPS                      │   │ DIM_VENDOR  │ │
│  └──────────────┘   │ ├── Partitioned by trip_date (DAY)                     │   └─────────────┘ │
│  ┌──────────────┐   │ └── Clustered by (vendor_key, payment_type_key,        │   ┌─────────────┐ │
│  │ DIM_LOCATION │◄──┤                    pickup_location_key, rate_code_key) ├──►│  DIM_DATE   │ │
│  └──────────────┘   └─────────────────────────────────────────────────────────┘   └─────────────┘ │
│  ┌──────────────┐                                                                 ┌─────────────┐ │
│  │DIM_RATE_CODE │                                                                 │DIM_PAYMENT_ │ │
│  └──────────────┘                                                                 │    TYPE     │ │
│                                                                                   └─────────────┘ │
└───────────────────────────────────────────────┬───────────────────────────────────────────────────┘
                                                │
                                                ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Analytics & Data Mart Layer                                       │
│ ├── Analytical Views: vw_revenue_summary, vw_daily_trip_summary, vw_monthly_revenue, etc.       │
│ └── Materialized Data Marts: mv_executive_summary_mart, mv_geographic_demand_mart                 │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 2. Star Schema & Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    FACT_TAXI_TRIPS {
        string trip_key PK
        string trip_id
        int64 vendor_key FK
        int64 payment_type_key FK
        int64 rate_code_key FK
        int64 pickup_location_key FK
        int64 dropoff_location_key FK
        int64 customer_key FK
        int64 pickup_date_key FK
        int64 dropoff_date_key FK
        date trip_date "PARTITION KEY"
        timestamp pickup_datetime
        timestamp dropoff_datetime
        int64 passenger_count
        float64 trip_distance
        numeric fare_amount
        numeric extra_amount
        numeric mta_tax
        numeric tip_amount
        numeric tolls_amount
        numeric improvement_surcharge
        numeric total_amount
        float64 trip_duration_minutes
        float64 tip_percentage
        float64 average_speed_mph
        bool weekend_flag
        bool peak_hour_flag
        timestamp load_timestamp
        string batch_id
        string source_execution_id
        string source_manifest
        float64 data_quality_score
    }

    DIM_DATE {
        int64 date_key PK "YYYYMMDD"
        date full_date
        int64 day_of_week
        string day_name
        int64 day_of_month
        int64 day_of_year
        int64 week_of_year
        int64 month
        string month_name
        int64 quarter
        int64 year
        bool is_weekend
        bool is_holiday
    }

    DIM_VENDOR {
        int64 vendor_key PK
        int64 vendor_id BK
        string vendor_name
        string contact_email
        string service_tier
        timestamp effective_from
        timestamp effective_to
        bool is_current
    }

    DIM_PAYMENT_TYPE {
        int64 payment_type_key PK
        int64 payment_type_id BK
        string payment_type_name
        bool is_electronic
        timestamp effective_from
        timestamp effective_to
        bool is_current
    }

    DIM_LOCATION {
        int64 location_key PK
        int64 location_id BK
        string borough
        string zone
        string service_zone
        float64 latitude
        float64 longitude
        timestamp effective_from
        timestamp effective_to
        bool is_current
    }

    DIM_RATE_CODE {
        int64 rate_code_key PK
        int64 rate_code_id BK
        string rate_code_name
        string description
        timestamp effective_from
        timestamp effective_to
        bool is_current
    }

    DIM_CUSTOMER {
        int64 customer_key PK
        string customer_id BK
        string first_name
        string last_name
        string email
        string customer_segment
        timestamp effective_from
        timestamp effective_to
        bool is_current
    }

    FACT_TAXI_TRIPS }|--|| DIM_DATE : "pickup_date_key"
    FACT_TAXI_TRIPS }|--|| DIM_DATE : "dropoff_date_key"
    FACT_TAXI_TRIPS }|--|| DIM_VENDOR : "vendor_key"
    FACT_TAXI_TRIPS }|--|| DIM_PAYMENT_TYPE : "payment_type_key"
    FACT_TAXI_TRIPS }|--|| DIM_LOCATION : "pickup_location_key"
    FACT_TAXI_TRIPS }|--|| DIM_LOCATION : "dropoff_location_key"
    FACT_TAXI_TRIPS }|--|| DIM_RATE_CODE : "rate_code_key"
    FACT_TAXI_TRIPS }|--|| DIM_CUSTOMER : "customer_key"
```

---

## ⚡ 3. Partitioning & Clustering Strategy

### Partitioning Strategy
- **Table**: `FACT_TAXI_TRIPS`
- **Partition Column**: `trip_date` (DATE)
- **Granularity**: Daily (`DAY`)
- **Enforcement**: `require_partition_filter = true` prevents accidental full-table scans across multi-terabyte BigQuery datasets.

### Clustering Strategy
- **Cluster Columns**: `(vendor_key, payment_type_key, pickup_location_key, rate_code_key)`
- **Rationale**: Filters on technology provider, payment mode, pickup zone, and fare type represent over 90% of business query predicates. Clustering physically sorts data within each daily partition block, reducing bytes scanned and execution latency.

---

## 🔄 4. Idempotent Incremental MERGE & SCD Strategy

### Incremental MERGE Loading
Idempotent MERGE operations execute against `FACT_TAXI_TRIPS` joining on `T.trip_key = S.trip_key AND T.trip_date = S.trip_date`.
Including `trip_date` in the MERGE join predicate forces BigQuery to prune partitions dynamically, limiting DML operations exclusively to active partitions.

### Slowly Changing Dimensions (SCD)
Dimensions support hybrid SCD Type 1 & Type 2 tracking:
- **Type 1 (Overwrite)**: Applied for non-historical correction attributes (e.g. description updates).
- **Type 2 (Versioned History)**: Maintains historical state transitions tracked via:
  - `effective_from`: Timestamp when dimension record became active.
  - `effective_to`: Timestamp when dimension record was superseded (NULL for active record).
  - `is_current`: Boolean flag (`TRUE` for active version).

---

## 📊 5. Data Marts & Analytical Views

1. **`vw_revenue_summary`**: Aggregates gross fare revenue, tip totals, tolls, and average tip percentages by year, month, and vendor.
2. **`vw_daily_trip_summary`**: Provides daily operational volume, passenger throughput, average trip duration, and total fare receipts.
3. **`vw_monthly_revenue`**: Computes month-over-month (MoM) revenue growth using window LAG functions.
4. **`vw_vendor_performance`**: Analyzes fleet utilization, total completed trips, average fleet speeds, and data quality scores.
5. **`vw_payment_analysis`**: Evaluates digital vs. cash payment distributions, tip behavior, and transaction volume shares.
6. **`vw_peak_hour_analysis`**: Tracks hourly traffic congestion, rush hour speed reductions, and fare yields.
7. **`vw_geographic_demand`**: Maps top origin-destination corridors across NYC boroughs and zones.
8. **`vw_passenger_trends`**: Evaluates rider group sizes and fare yields.
9. **`mv_executive_summary_mart`**: Partitioned materialized view pre-aggregating core financial KPIs.
10. **`mv_geographic_demand_mart`**: Materialized view optimizing geographic corridor analytics.

---

## 🛡 6. Phase 7 Quality Framework Integration

Only Silver records meeting or exceeding the Phase 7 Data Quality score threshold ($\ge 70.0\%$, Grade C+) are permitted to enter the Gold Warehouse.
Lineage audit attributes (`load_timestamp`, `batch_id`, `source_execution_id`, `source_manifest`, `data_quality_score`) are populated alongside every record in `FACT_TAXI_TRIPS`.

---

## 🧪 7. Testing & Quality Assurance Strategy

Automated unit tests in `tests/unit/test_warehouse.py` validate:
- Star schema relationship integrity and foreign key definitions.
- BigQuery daily partition parameters and partition metadata inspection.
- Clustering column limit constraints (Max 4 columns).
- Idempotent MERGE upsert logic and Data Quality score gatekeeper rejections.
- SQL DDL, DML, and view template syntax formatting.

---

## 💰 8. Performance & Cost Optimization Recommendations

1. **Partition Pruning**: Always include `WHERE trip_date BETWEEN ... AND ...` in analytical queries to eliminate unneeded partitions.
2. **Materialized Views**: Query `mv_executive_summary_mart` for high-level dashboards; BigQuery automatically maintains incremental refresh at zero compute overhead.
3. **Table Expiration**: Configure table/partition expiration policies (`retention_days = 1095` / 3 years) for automated cold data management.
4. **Column Projection**: Select explicit columns (`SELECT trip_date, vendor_key, total_amount`) instead of `SELECT *` to minimize bytes scanned per slot.
5. **Slot Commitment & Reservations**: Utilize BigQuery Editions (Standard/Enterprise) with auto-scaling slots for predictable query SLAs.
