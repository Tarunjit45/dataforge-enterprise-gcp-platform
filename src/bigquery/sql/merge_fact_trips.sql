-- BigQuery DML: Idempotent MERGE Upsert for FACT_TRIPS

MERGE INTO `{project_id}.{dataset_id}.fact_trips` T
USING `{project_id}.{dataset_id}.stg_fact_trips` S
ON T.tpep_pickup_datetime = S.tpep_pickup_datetime
   AND T.VendorID = S.VendorID
   AND T.Trip_Id = S.Trip_Id

WHEN MATCHED THEN
  UPDATE SET
    T.tpep_dropoff_datetime = S.tpep_dropoff_datetime,
    T.passenger_count = S.passenger_count,
    T.trip_distance = S.trip_distance,
    T.RatecodeID = S.RatecodeID,
    T.PULocationID = S.PULocationID,
    T.DOLocationID = S.DOLocationID,
    T.payment_type = S.payment_type,
    T.fare_amount = S.fare_amount,
    T.tip_amount = S.tip_amount,
    T.total_amount = S.total_amount,
    T.trip_duration_minutes = S.trip_duration_minutes,
    T.tip_percentage = S.tip_percentage,
    T.average_speed_mph = S.average_speed_mph,
    T.weekend_flag = S.weekend_flag,
    T.peak_hour_flag = S.peak_hour_flag

WHEN NOT MATCHED THEN
  INSERT (
    Trip_Id, VendorID, tpep_pickup_datetime, tpep_dropoff_datetime,
    passenger_count, trip_distance, RatecodeID, PULocationID, DOLocationID,
    payment_type, fare_amount, tip_amount, total_amount,
    trip_duration_minutes, tip_percentage, average_speed_mph,
    weekend_flag, peak_hour_flag
  )
  VALUES (
    S.Trip_Id, S.VendorID, S.tpep_pickup_datetime, S.tpep_dropoff_datetime,
    S.passenger_count, S.trip_distance, S.RatecodeID, S.PULocationID, S.DOLocationID,
    S.payment_type, S.fare_amount, S.tip_amount, S.total_amount,
    S.trip_duration_minutes, S.tip_percentage, S.average_speed_mph,
    S.weekend_flag, S.peak_hour_flag
  );
