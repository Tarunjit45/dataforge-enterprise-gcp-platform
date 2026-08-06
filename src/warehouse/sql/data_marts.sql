-- =============================================================================
-- Enterprise BigQuery Gold Warehouse: Data Mart Materialized Views / Tables
-- Project: {project_id} | Dataset: {dataset_id}
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Executive Revenue & Operational Summary Data Mart
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS `{project_id}.{dataset_id}.mv_executive_summary_mart`
PARTITION BY trip_date
CLUSTER BY vendor_key
AS SELECT
    F.trip_date,
    F.vendor_key,
    F.payment_type_key,
    F.rate_code_key,
    COUNT(F.trip_key) AS daily_trips,
    SUM(F.passenger_count) AS total_passengers,
    SUM(F.fare_amount) AS total_fare,
    SUM(F.tip_amount) AS total_tips,
    SUM(F.tolls_amount) AS total_tolls,
    SUM(F.total_amount) AS gross_revenue
FROM `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` F
GROUP BY
    F.trip_date,
    F.vendor_key,
    F.payment_type_key,
    F.rate_code_key;

-- -----------------------------------------------------------------------------
-- 2. Geographic Corridor & Zone Demand Data Mart
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS `{project_id}.{dataset_id}.mv_geographic_demand_mart`
PARTITION BY trip_date
CLUSTER BY pickup_location_key, dropoff_location_key
AS SELECT
    F.trip_date,
    F.pickup_location_key,
    F.dropoff_location_key,
    COUNT(F.trip_key) AS total_trips,
    SUM(F.trip_distance) AS total_distance,
    SUM(F.fare_amount) AS total_fare_revenue
FROM `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` F
GROUP BY
    F.trip_date,
    F.pickup_location_key,
    F.dropoff_location_key;
