-- =============================================================================
-- Enterprise BigQuery Gold Warehouse: Create Fact Tables DDL Script
-- Project: {project_id} | Dataset: {dataset_id}
-- =============================================================================

-- -----------------------------------------------------------------------------
-- FACT_TAXI_TRIPS (Partitioned by trip_date, Clustered by Analytical Columns)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.FACT_TAXI_TRIPS`
(
    trip_key STRING OPTIONS(description="Surrogate primary key for trip record (MD5/SHA256 hash)"),
    trip_id STRING OPTIONS(description="Natural business key / transaction ID"),
    vendor_key INT64 OPTIONS(description="Surrogate foreign key referencing DIM_VENDOR"),
    payment_type_key INT64 OPTIONS(description="Surrogate foreign key referencing DIM_PAYMENT_TYPE"),
    rate_code_key INT64 OPTIONS(description="Surrogate foreign key referencing DIM_RATE_CODE"),
    pickup_location_key INT64 OPTIONS(description="Surrogate foreign key referencing DIM_LOCATION for pickup"),
    dropoff_location_key INT64 OPTIONS(description="Surrogate foreign key referencing DIM_LOCATION for dropoff"),
    customer_key INT64 OPTIONS(description="Surrogate foreign key referencing DIM_CUSTOMER"),
    pickup_date_key INT64 OPTIONS(description="Surrogate foreign key referencing DIM_DATE for pickup date (YYYYMMDD)"),
    dropoff_date_key INT64 OPTIONS(description="Surrogate foreign key referencing DIM_DATE for dropoff date (YYYYMMDD)"),
    trip_date DATE OPTIONS(description="Calendar pickup date (PARTITION KEY)"),
    pickup_datetime TIMESTAMP OPTIONS(description="Exact trip pickup timestamp"),
    dropoff_datetime TIMESTAMP OPTIONS(description="Exact trip dropoff timestamp"),
    passenger_count INT64 OPTIONS(description="Total passenger count"),
    trip_distance FLOAT64 OPTIONS(description="Trip distance in miles"),
    fare_amount NUMERIC OPTIONS(description="Base fare amount charged by meter"),
    extra_amount NUMERIC OPTIONS(description="Miscellaneous extras and surcharges"),
    mta_tax NUMERIC OPTIONS(description="MTA tax automatically triggered by meter"),
    tip_amount NUMERIC OPTIONS(description="Tip amount"),
    tolls_amount NUMERIC OPTIONS(description="Total tolls paid"),
    improvement_surcharge NUMERIC OPTIONS(description="Improvement surcharge assessed at flag drop"),
    total_amount NUMERIC OPTIONS(description="Total charged amount to passenger"),
    trip_duration_minutes FLOAT64 OPTIONS(description="Calculated duration in elapsed minutes"),
    tip_percentage FLOAT64 OPTIONS(description="Calculated tip ratio relative to fare"),
    average_speed_mph FLOAT64 OPTIONS(description="Calculated average speed in mph"),
    weekend_flag BOOL OPTIONS(description="Flag indicating weekend pickup"),
    peak_hour_flag BOOL OPTIONS(description="Flag indicating rush hour pickup"),
    
    -- Quality Lineage & Audit Columns
    load_timestamp TIMESTAMP OPTIONS(description="Audit timestamp when record was written to Gold"),
    batch_id STRING OPTIONS(description="ETL Batch execution identifier"),
    source_execution_id STRING OPTIONS(description="Phase 7 source pipeline execution ID"),
    source_manifest STRING OPTIONS(description="Phase 7 validated manifest path"),
    data_quality_score FLOAT64 OPTIONS(description="Phase 7 calculated Data Quality score percentage")
)
PARTITION BY trip_date
CLUSTER BY vendor_key, payment_type_key, pickup_location_key, rate_code_key
OPTIONS(
    description="Enterprise Gold Fact table containing validated NYC taxi trip records and business metrics",
    labels=[("layer", "gold"), ("type", "fact"), ("entity", "taxi_trips")],
    require_partition_filter=true
);
