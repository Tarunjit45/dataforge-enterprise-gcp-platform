-- BigQuery DDL: Create Partitioned and Clustered Gold Star Schema Datamarts

-- 1. FACT_SALES
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.fact_sales` (
  Sales_Id STRING NOT NULL,
  Order_Timestamp TIMESTAMP NOT NULL,
  Date_Key INT64 NOT NULL,
  SK_Customer_Id STRING NOT NULL,
  SK_Product_Id STRING NOT NULL,
  Store_Id STRING NOT NULL,
  Quantity_Sold INT64 NOT NULL,
  Total_Sales_Amount NUMERIC NOT NULL,
  Tax_Amount NUMERIC,
  Discount_Amount NUMERIC
)
PARTITION BY DATE(Order_Timestamp)
CLUSTER BY Store_Id, SK_Customer_Id;

-- 2. FACT_TRIPS (NYC Taxi Domain)
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.fact_trips` (
  Trip_Id STRING NOT NULL,
  VendorID INT64 NOT NULL,
  tpep_pickup_datetime TIMESTAMP NOT NULL,
  tpep_dropoff_datetime TIMESTAMP NOT NULL,
  passenger_count INT64,
  trip_distance FLOAT64 NOT NULL,
  RatecodeID INT64,
  PULocationID INT64,
  DOLocationID INT64,
  payment_type INT64 NOT NULL,
  fare_amount FLOAT64 NOT NULL,
  tip_amount FLOAT64,
  total_amount FLOAT64 NOT NULL,
  trip_duration_minutes FLOAT64,
  tip_percentage FLOAT64,
  average_speed_mph FLOAT64,
  weekend_flag BOOLEAN,
  peak_hour_flag BOOLEAN
)
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID, payment_type;

-- 3. DIM_CUSTOMERS (SCD Type 2)
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.dim_customers` (
  SK_Customer_Id STRING NOT NULL,
  NK_Customer_Number STRING NOT NULL,
  First_Name STRING,
  Last_Name STRING,
  Email STRING,
  Customer_Segment STRING,
  Effective_Start_Date TIMESTAMP NOT NULL,
  Effective_End_Date TIMESTAMP,
  Is_Current_Flag BOOLEAN NOT NULL
)
CLUSTER BY NK_Customer_Number, Is_Current_Flag;
