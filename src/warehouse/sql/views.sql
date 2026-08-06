-- =============================================================================
-- Enterprise BigQuery Gold Warehouse: Analytical View Definitions
-- Project: {project_id} | Dataset: {dataset_id}
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Revenue Summary View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_revenue_summary` AS
SELECT
    D.year,
    D.quarter,
    D.month_name,
    V.vendor_name,
    COUNT(F.trip_key) AS total_trips,
    SUM(F.fare_amount) AS gross_fare_revenue,
    SUM(F.tip_amount) AS total_tips,
    SUM(F.tolls_amount) AS total_tolls,
    SUM(F.total_amount) AS net_total_revenue,
    ROUND(AVG(F.fare_amount), 2) AS avg_fare_per_trip,
    ROUND(AVG(F.tip_percentage), 2) AS avg_tip_percentage
FROM `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` F
JOIN `{project_id}.{dataset_id}.DIM_DATE` D ON F.pickup_date_key = D.date_key
JOIN `{project_id}.{dataset_id}.DIM_VENDOR` V ON F.vendor_key = V.vendor_key
GROUP BY D.year, D.quarter, D.month, D.month_name, V.vendor_name;

-- -----------------------------------------------------------------------------
-- 2. Daily Trip Summary View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_daily_trip_summary` AS
SELECT
    F.trip_date,
    D.day_name,
    D.is_weekend,
    COUNT(F.trip_key) AS trip_count,
    SUM(F.passenger_count) AS total_passengers,
    ROUND(SUM(F.trip_distance), 2) AS total_distance_miles,
    ROUND(AVG(F.trip_duration_minutes), 2) AS avg_duration_minutes,
    SUM(F.total_amount) AS total_revenue
FROM `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` F
JOIN `{project_id}.{dataset_id}.DIM_DATE` D ON F.pickup_date_key = D.date_key
GROUP BY F.trip_date, D.day_name, D.is_weekend;

-- -----------------------------------------------------------------------------
-- 3. Monthly Revenue View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_monthly_revenue` AS
SELECT
    D.year,
    D.month,
    D.month_name,
    COUNT(F.trip_key) AS monthly_trip_count,
    SUM(F.fare_amount) AS monthly_fare_amount,
    SUM(F.total_amount) AS monthly_total_revenue,
    LAG(SUM(F.total_amount)) OVER (ORDER BY D.year, D.month) AS prior_month_revenue,
    ROUND(SAFE_DIVIDE(
        SUM(F.total_amount) - LAG(SUM(F.total_amount)) OVER (ORDER BY D.year, D.month),
        LAG(SUM(F.total_amount)) OVER (ORDER BY D.year, D.month)
    ) * 100, 2) AS mom_growth_percentage
FROM `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` F
JOIN `{project_id}.{dataset_id}.DIM_DATE` D ON F.pickup_date_key = D.date_key
GROUP BY D.year, D.month, D.month_name;

-- -----------------------------------------------------------------------------
-- 4. Vendor Performance View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_vendor_performance` AS
SELECT
    V.vendor_id,
    V.vendor_name,
    V.service_tier,
    COUNT(F.trip_key) AS total_completed_trips,
    ROUND(SUM(F.trip_distance), 2) AS total_fleet_miles,
    SUM(F.total_amount) AS total_revenue_generated,
    ROUND(AVG(F.average_speed_mph), 2) AS avg_fleet_speed_mph,
    ROUND(AVG(F.data_quality_score), 2) AS avg_data_quality_score
FROM `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` F
JOIN `{project_id}.{dataset_id}.DIM_VENDOR` V ON F.vendor_key = V.vendor_key
GROUP BY V.vendor_id, V.vendor_name, V.service_tier;

-- -----------------------------------------------------------------------------
-- 5. Payment Analysis View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_payment_analysis` AS
SELECT
    P.payment_type_name,
    P.is_electronic,
    COUNT(F.trip_key) AS transaction_count,
    SUM(F.total_amount) AS total_volume,
    SUM(F.tip_amount) AS total_tips,
    ROUND(AVG(F.tip_percentage), 2) AS average_tip_rate,
    ROUND(SAFE_DIVIDE(COUNT(F.trip_key), SUM(COUNT(F.trip_key)) OVER ()) * 100, 2) AS payment_share_pct
FROM `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` F
JOIN `{project_id}.{dataset_id}.DIM_PAYMENT_TYPE` P ON F.payment_type_key = P.payment_type_key
GROUP BY P.payment_type_name, P.is_electronic;

-- -----------------------------------------------------------------------------
-- 6. Peak Hour Analysis View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_peak_hour_analysis` AS
SELECT
    EXTRACT(HOUR FROM F.pickup_datetime) AS hour_of_day,
    F.peak_hour_flag,
    F.weekend_flag,
    COUNT(F.trip_key) AS hourly_trips,
    ROUND(AVG(F.trip_duration_minutes), 2) AS avg_duration,
    ROUND(AVG(F.average_speed_mph), 2) AS avg_speed_mph,
    SUM(F.total_amount) AS total_hourly_revenue
FROM `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` F
GROUP BY hour_of_day, F.peak_hour_flag, F.weekend_flag;

-- -----------------------------------------------------------------------------
-- 7. Geographic Demand View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_geographic_demand` AS
SELECT
    PL.borough AS pickup_borough,
    PL.zone AS pickup_zone,
    DL.borough AS dropoff_borough,
    DL.zone AS dropoff_zone,
    COUNT(F.trip_key) AS route_trip_count,
    ROUND(AVG(F.trip_distance), 2) AS avg_route_distance,
    ROUND(AVG(F.fare_amount), 2) AS avg_route_fare
FROM `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` F
JOIN `{project_id}.{dataset_id}.DIM_LOCATION` PL ON F.pickup_location_key = PL.location_key
JOIN `{project_id}.{dataset_id}.DIM_LOCATION` DL ON F.dropoff_location_key = DL.location_key
GROUP BY PL.borough, PL.zone, DL.borough, DL.zone;

-- -----------------------------------------------------------------------------
-- 8. Passenger Trends View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.vw_passenger_trends` AS
SELECT
    COALESCE(F.passenger_count, 1) AS passenger_count,
    COUNT(F.trip_key) AS trip_frequency,
    ROUND(AVG(F.trip_distance), 2) AS avg_distance,
    ROUND(AVG(F.total_amount), 2) AS avg_total_amount,
    ROUND(AVG(F.tip_amount), 2) AS avg_tip_amount
FROM `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` F
GROUP BY COALESCE(F.passenger_count, 1);
