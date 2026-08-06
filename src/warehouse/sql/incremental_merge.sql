-- =============================================================================
-- Enterprise BigQuery Gold Warehouse: Idempotent Incremental MERGE Script
-- Project: {project_id} | Dataset: {dataset_id}
-- Partition Pruned MERGE on FACT_TAXI_TRIPS
-- =============================================================================

MERGE `{project_id}.{dataset_id}.FACT_TAXI_TRIPS` T
USING (
    SELECT
        TO_HEX(MD5(CONCAT(
            COALESCE(CAST(S.VendorID AS STRING), ''), '_',
            COALESCE(CAST(S.tpep_pickup_datetime AS STRING), ''), '_',
            COALESCE(CAST(S.PULocationID AS STRING), ''), '_',
            COALESCE(CAST(S.DOLocationID AS STRING), '')
        ))) AS trip_key,
        COALESCE(CAST(S.Trip_Id AS STRING), TO_HEX(MD5(CONCAT(CAST(S.VendorID AS STRING), CAST(S.tpep_pickup_datetime AS STRING))))) AS trip_id,
        COALESCE(V.vendor_key, -1) AS vendor_key,
        COALESCE(P.payment_type_key, -1) AS payment_type_key,
        COALESCE(R.rate_code_key, -1) AS rate_code_key,
        COALESCE(PL.location_key, -1) AS pickup_location_key,
        COALESCE(DL.location_key, -1) AS dropoff_location_key,
        COALESCE(C.customer_key, -1) AS customer_key,
        COALESCE(CAST(FORMAT_DATE('%Y%m%d', DATE(S.tpep_pickup_datetime)) AS INT64), -1) AS pickup_date_key,
        COALESCE(CAST(FORMAT_DATE('%Y%m%d', DATE(S.tpep_dropoff_datetime)) AS INT64), -1) AS dropoff_date_key,
        DATE(S.tpep_pickup_datetime) AS trip_date,
        S.tpep_pickup_datetime AS pickup_datetime,
        S.tpep_dropoff_datetime AS dropoff_datetime,
        CAST(S.passenger_count AS INT64) AS passenger_count,
        CAST(S.trip_distance AS FLOAT64) AS trip_distance,
        CAST(S.fare_amount AS NUMERIC) AS fare_amount,
        CAST(S.extra AS NUMERIC) AS extra_amount,
        CAST(S.mta_tax AS NUMERIC) AS mta_tax,
        CAST(S.tip_amount AS NUMERIC) AS tip_amount,
        CAST(S.tolls_amount AS NUMERIC) AS tolls_amount,
        CAST(S.improvement_surcharge AS NUMERIC) AS improvement_surcharge,
        CAST(S.total_amount AS NUMERIC) AS total_amount,
        CAST(S.trip_duration_minutes AS FLOAT64) AS trip_duration_minutes,
        CAST(S.tip_percentage AS FLOAT64) AS tip_percentage,
        CAST(S.average_speed_mph AS FLOAT64) AS average_speed_mph,
        CAST(S.weekend_flag AS BOOL) AS weekend_flag,
        CAST(S.peak_hour_flag AS BOOL) AS peak_hour_flag,
        CURRENT_TIMESTAMP() AS load_timestamp,
        '{batch_id}' AS batch_id,
        '{source_execution_id}' AS source_execution_id,
        '{source_manifest}' AS source_manifest,
        CAST({data_quality_score} AS FLOAT64) AS data_quality_score
    FROM `{project_id}.{staged_dataset}.staged_silver_trips` S
    LEFT JOIN `{project_id}.{dataset_id}.DIM_VENDOR` V
        ON S.VendorID = V.vendor_id AND V.is_current = TRUE
    LEFT JOIN `{project_id}.{dataset_id}.DIM_PAYMENT_TYPE` P
        ON S.payment_type = P.payment_type_id AND P.is_current = TRUE
    LEFT JOIN `{project_id}.{dataset_id}.DIM_RATE_CODE` R
        ON S.RatecodeID = R.rate_code_id AND R.is_current = TRUE
    LEFT JOIN `{project_id}.{dataset_id}.DIM_LOCATION` PL
        ON S.PULocationID = PL.location_id AND PL.is_current = TRUE
    LEFT JOIN `{project_id}.{dataset_id}.DIM_LOCATION` DL
        ON S.DOLocationID = DL.location_id AND DL.is_current = TRUE
    LEFT JOIN `{project_id}.{dataset_id}.DIM_CUSTOMER` C
        ON S.customer_id = C.customer_id AND C.is_current = TRUE
) S
ON T.trip_key = S.trip_key AND T.trip_date = S.trip_date
WHEN MATCHED THEN
    UPDATE SET
        T.passenger_count = S.passenger_count,
        T.trip_distance = S.trip_distance,
        T.fare_amount = S.fare_amount,
        T.extra_amount = S.extra_amount,
        T.mta_tax = S.mta_tax,
        T.tip_amount = S.tip_amount,
        T.tolls_amount = S.tolls_amount,
        T.improvement_surcharge = S.improvement_surcharge,
        T.total_amount = S.total_amount,
        T.trip_duration_minutes = S.trip_duration_minutes,
        T.tip_percentage = S.tip_percentage,
        T.average_speed_mph = S.average_speed_mph,
        T.load_timestamp = S.load_timestamp,
        T.batch_id = S.batch_id,
        T.data_quality_score = S.data_quality_score
WHEN NOT MATCHED THEN
    INSERT (
        trip_key, trip_id, vendor_key, payment_type_key, rate_code_key,
        pickup_location_key, dropoff_location_key, customer_key,
        pickup_date_key, dropoff_date_key, trip_date, pickup_datetime,
        dropoff_datetime, passenger_count, trip_distance, fare_amount,
        extra_amount, mta_tax, tip_amount, tolls_amount, improvement_surcharge,
        total_amount, trip_duration_minutes, tip_percentage, average_speed_mph,
        weekend_flag, peak_hour_flag, load_timestamp, batch_id,
        source_execution_id, source_manifest, data_quality_score
    )
    VALUES (
        S.trip_key, S.trip_id, S.vendor_key, S.payment_type_key, S.rate_code_key,
        S.pickup_location_key, S.dropoff_location_key, S.customer_key,
        S.pickup_date_key, S.dropoff_date_key, S.trip_date, S.pickup_datetime,
        S.dropoff_datetime, S.passenger_count, S.trip_distance, S.fare_amount,
        S.extra_amount, S.mta_tax, S.tip_amount, S.tolls_amount, S.improvement_surcharge,
        S.total_amount, S.trip_duration_minutes, S.tip_percentage, S.average_speed_mph,
        S.weekend_flag, S.peak_hour_flag, S.load_timestamp, S.batch_id,
        S.source_execution_id, S.source_manifest, S.data_quality_score
    );
