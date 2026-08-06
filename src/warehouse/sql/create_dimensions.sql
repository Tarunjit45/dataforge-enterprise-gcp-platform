-- =============================================================================
-- Enterprise BigQuery Gold Warehouse: Create Dimension DDL Scripts
-- Project: {project_id} | Dataset: {dataset_id}
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. DIM_DATE (Calendar Dimension)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.DIM_DATE`
(
    date_key INT64 OPTIONS(description="Surrogate key formatted as YYYYMMDD"),
    full_date DATE OPTIONS(description="Full calendar date"),
    day_of_week INT64 OPTIONS(description="Day of week (1=Sunday, 7=Saturday)"),
    day_name STRING OPTIONS(description="Day of week name"),
    day_of_month INT64 OPTIONS(description="Day of month (1-31)"),
    day_of_year INT64 OPTIONS(description="Day of year (1-366)"),
    week_of_year INT64 OPTIONS(description="ISO week number of year (1-53)"),
    month INT64 OPTIONS(description="Month number (1-12)"),
    month_name STRING OPTIONS(description="Month name"),
    quarter INT64 OPTIONS(description="Calendar quarter (1-4)"),
    year INT64 OPTIONS(description="Four-digit calendar year"),
    is_weekend BOOL OPTIONS(description="Flag indicating weekend day"),
    is_holiday BOOL OPTIONS(description="Flag indicating public holiday")
)
OPTIONS(
    description="Calendar dimension table providing standardized date attributes for temporal analytics",
    labels=[("layer", "gold"), ("type", "dimension"), ("entity", "date")]
);

-- -----------------------------------------------------------------------------
-- 2. DIM_VENDOR (SCD Type 2 Technology Provider Dimension)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.DIM_VENDOR`
(
    vendor_key INT64 OPTIONS(description="Surrogate primary key for vendor"),
    vendor_id INT64 OPTIONS(description="TLC technology provider business key"),
    vendor_name STRING OPTIONS(description="Full business name of vendor"),
    contact_email STRING OPTIONS(description="Vendor technical contact email"),
    service_tier STRING OPTIONS(description="Vendor SLA service tier (Gold, Silver, Bronze)"),
    effective_from TIMESTAMP OPTIONS(description="SCD Type 2 effective start timestamp"),
    effective_to TIMESTAMP OPTIONS(description="SCD Type 2 effective end timestamp"),
    is_current BOOL OPTIONS(description="SCD Type 2 active record flag")
)
OPTIONS(
    description="Vendor dimension storing TLC technology provider details with SCD Type 2 tracking",
    labels=[("layer", "gold"), ("type", "dimension"), ("entity", "vendor")]
);

-- -----------------------------------------------------------------------------
-- 3. DIM_PAYMENT_TYPE (SCD Type 2 Payment Method Dimension)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.DIM_PAYMENT_TYPE`
(
    payment_type_key INT64 OPTIONS(description="Surrogate primary key for payment type"),
    payment_type_id INT64 OPTIONS(description="Payment type business key"),
    payment_type_name STRING OPTIONS(description="Human-readable payment type description"),
    is_electronic BOOL OPTIONS(description="Flag indicating digital/electronic settlement"),
    effective_from TIMESTAMP OPTIONS(description="SCD Type 2 effective start timestamp"),
    effective_to TIMESTAMP OPTIONS(description="SCD Type 2 effective end timestamp"),
    is_current BOOL OPTIONS(description="SCD Type 2 active record flag")
)
OPTIONS(
    description="Payment Type dimension with SCD Type 2 tracking for transaction methods",
    labels=[("layer", "gold"), ("type", "dimension"), ("entity", "payment_type")]
);

-- -----------------------------------------------------------------------------
-- 4. DIM_LOCATION (SCD Type 2 Geographic Zone Dimension)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.DIM_LOCATION`
(
    location_key INT64 OPTIONS(description="Surrogate primary key for location"),
    location_id INT64 OPTIONS(description="TLC location zone business key"),
    borough STRING OPTIONS(description="NYC borough"),
    zone STRING OPTIONS(description="TLC neighborhood / location zone name"),
    service_zone STRING OPTIONS(description="TLC service zone designation"),
    latitude FLOAT64 OPTIONS(description="Centroid latitude coordinate"),
    longitude FLOAT64 OPTIONS(description="Centroid longitude coordinate"),
    effective_from TIMESTAMP OPTIONS(description="SCD Type 2 effective start timestamp"),
    effective_to TIMESTAMP OPTIONS(description="SCD Type 2 effective end timestamp"),
    is_current BOOL OPTIONS(description="SCD Type 2 active record flag")
)
OPTIONS(
    description="Geographic Location dimension mapping TLC zones and boroughs with SCD Type 2 tracking",
    labels=[("layer", "gold"), ("type", "dimension"), ("entity", "location")]
);

-- -----------------------------------------------------------------------------
-- 5. DIM_RATE_CODE (SCD Type 2 Fare Rate Code Dimension)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.DIM_RATE_CODE`
(
    rate_code_key INT64 OPTIONS(description="Surrogate primary key for rate code"),
    rate_code_id INT64 OPTIONS(description="Rate code business key"),
    rate_code_name STRING OPTIONS(description="Rate code tier name"),
    description STRING OPTIONS(description="Detailed policy description"),
    effective_from TIMESTAMP OPTIONS(description="SCD Type 2 effective start timestamp"),
    effective_to TIMESTAMP OPTIONS(description="SCD Type 2 effective end timestamp"),
    is_current BOOL OPTIONS(description="SCD Type 2 active record flag")
)
OPTIONS(
    description="Rate Code dimension detailing tariff types with SCD Type 2 tracking",
    labels=[("layer", "gold"), ("type", "dimension"), ("entity", "rate_code")]
);

-- -----------------------------------------------------------------------------
-- 6. DIM_CUSTOMER (SCD Type 2 Customer Profile Dimension)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset_id}.DIM_CUSTOMER`
(
    customer_key INT64 OPTIONS(description="Surrogate primary key for customer"),
    customer_id STRING OPTIONS(description="Natural business key for customer"),
    first_name STRING OPTIONS(description="Customer first name"),
    last_name STRING OPTIONS(description="Customer last name"),
    email STRING OPTIONS(description="Customer contact email"),
    customer_segment STRING OPTIONS(description="Customer tier or behavioral segment"),
    effective_from TIMESTAMP OPTIONS(description="SCD Type 2 effective start timestamp"),
    effective_to TIMESTAMP OPTIONS(description="SCD Type 2 effective end timestamp"),
    is_current BOOL OPTIONS(description="SCD Type 2 active record flag")
)
OPTIONS(
    description="Customer dimension tracking rider profiles with SCD Type 2 versioning",
    labels=[("layer", "gold"), ("type", "dimension"), ("entity", "customer")]
);
