-- =============================================================================
-- Enterprise BigQuery Gold Warehouse: Load Dimensions Script (SCD Support)
-- Project: {project_id} | Dataset: {dataset_id}
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Seed DIM_DATE Calendar Dimension (10-Year Range Seed)
-- -----------------------------------------------------------------------------
INSERT INTO `{project_id}.{dataset_id}.DIM_DATE` (
    date_key, full_date, day_of_week, day_name, day_of_month, day_of_year,
    week_of_year, month, month_name, quarter, year, is_weekend, is_holiday
)
SELECT
    CAST(FORMAT_DATE('%Y%m%d', d) AS INT64) AS date_key,
    d AS full_date,
    EXTRACT(DAYOFWEEK FROM d) AS day_of_week,
    FORMAT_DATE('%A', d) AS day_name,
    EXTRACT(DAY FROM d) AS day_of_month,
    EXTRACT(DAYOFYEAR FROM d) AS day_of_year,
    EXTRACT(ISOWEEK FROM d) AS week_of_year,
    EXTRACT(MONTH FROM d) AS month,
    FORMAT_DATE('%B', d) AS month_name,
    EXTRACT(QUARTER FROM d) AS quarter,
    EXTRACT(YEAR FROM d) AS year,
    CASE WHEN EXTRACT(DAYOFWEEK FROM d) IN (1, 7) THEN TRUE ELSE FALSE END AS is_weekend,
    CASE WHEN FORMAT_DATE('%m-%d', d) IN ('01-01', '07-04', '11-25', '12-25') THEN TRUE ELSE FALSE END AS is_holiday
FROM UNNEST(GENERATE_DATE_ARRAY('2020-01-01', '2030-12-31', INTERVAL 1 DAY)) AS d
WHERE NOT EXISTS (
    SELECT 1 FROM `{project_id}.{dataset_id}.DIM_DATE` WHERE date_key = CAST(FORMAT_DATE('%Y%m%d', d) AS INT64)
);

-- Seed Unknown Date Record (-1)
INSERT INTO `{project_id}.{dataset_id}.DIM_DATE` (
    date_key, full_date, day_of_week, day_name, day_of_month, day_of_year,
    week_of_year, month, month_name, quarter, year, is_weekend, is_holiday
)
SELECT -1, DATE('1900-01-01'), 1, 'Unknown', 1, 1, 1, 1, 'Unknown', 1, 1900, FALSE, FALSE
WHERE NOT EXISTS (SELECT 1 FROM `{project_id}.{dataset_id}.DIM_DATE` WHERE date_key = -1);

-- -----------------------------------------------------------------------------
-- 2. MERGE DIM_VENDOR (SCD Type 2 Load)
-- -----------------------------------------------------------------------------
MERGE `{project_id}.{dataset_id}.DIM_VENDOR` T
USING (
    SELECT 1 AS vendor_id, 'Creative Mobile Technologies, LLC' AS vendor_name, 'support@cmt.com' AS contact_email, 'Gold' AS service_tier
    UNION ALL
    SELECT 2 AS vendor_id, 'VeriFone Inc.' AS vendor_name, 'contact@verifone.com' AS contact_email, 'Gold' AS service_tier
    UNION ALL
    SELECT -1 AS vendor_id, 'Unknown Vendor' AS vendor_name, 'n/a' AS contact_email, 'Bronze' AS service_tier
) S
ON T.vendor_id = S.vendor_id AND T.is_current = TRUE
WHEN MATCHED AND (T.vendor_name != S.vendor_name OR T.contact_email != S.contact_email OR T.service_tier != S.service_tier) THEN
    UPDATE SET effective_to = CURRENT_TIMESTAMP(), is_current = FALSE
WHEN NOT MATCHED THEN
    INSERT (vendor_key, vendor_id, vendor_name, contact_email, service_tier, effective_from, effective_to, is_current)
    VALUES (S.vendor_id, S.vendor_id, S.vendor_name, S.contact_email, S.service_tier, CURRENT_TIMESTAMP(), NULL, TRUE);

-- Insert new active version for expired SCD2 records
INSERT INTO `{project_id}.{dataset_id}.DIM_VENDOR` (
    vendor_key, vendor_id, vendor_name, contact_email, service_tier, effective_from, effective_to, is_current
)
SELECT
    S.vendor_id, S.vendor_id, S.vendor_name, S.contact_email, S.service_tier, CURRENT_TIMESTAMP(), NULL, TRUE
FROM (
    SELECT 1 AS vendor_id, 'Creative Mobile Technologies, LLC' AS vendor_name, 'support@cmt.com' AS contact_email, 'Gold' AS service_tier
    UNION ALL
    SELECT 2 AS vendor_id, 'VeriFone Inc.' AS vendor_name, 'contact@verifone.com' AS contact_email, 'Gold' AS service_tier
) S
JOIN `{project_id}.{dataset_id}.DIM_VENDOR` T ON T.vendor_id = S.vendor_id
WHERE T.is_current = FALSE AND NOT EXISTS (
    SELECT 1 FROM `{project_id}.{dataset_id}.DIM_VENDOR` C WHERE C.vendor_id = S.vendor_id AND C.is_current = TRUE
);

-- -----------------------------------------------------------------------------
-- 3. MERGE DIM_PAYMENT_TYPE (SCD Type 1/2 Load)
-- -----------------------------------------------------------------------------
MERGE `{project_id}.{dataset_id}.DIM_PAYMENT_TYPE` T
USING (
    SELECT 1 AS payment_type_id, 'Credit card' AS payment_type_name, TRUE AS is_electronic
    UNION ALL SELECT 2, 'Cash', FALSE
    UNION ALL SELECT 3, 'No charge', FALSE
    UNION ALL SELECT 4, 'Dispute', FALSE
    UNION ALL SELECT 5, 'Unknown', FALSE
    UNION ALL SELECT 6, 'Voided trip', FALSE
    UNION ALL SELECT -1, 'Unknown / Unspecified', FALSE
) S
ON T.payment_type_id = S.payment_type_id AND T.is_current = TRUE
WHEN MATCHED AND (T.payment_type_name != S.payment_type_name OR T.is_electronic != S.is_electronic) THEN
    UPDATE SET payment_type_name = S.payment_type_name, is_electronic = S.is_electronic
WHEN NOT MATCHED THEN
    INSERT (payment_type_key, payment_type_id, payment_type_name, is_electronic, effective_from, effective_to, is_current)
    VALUES (S.payment_type_id, S.payment_type_id, S.payment_type_name, S.is_electronic, CURRENT_TIMESTAMP(), NULL, TRUE);

-- -----------------------------------------------------------------------------
-- 4. MERGE DIM_RATE_CODE (SCD Type 1/2 Load)
-- -----------------------------------------------------------------------------
MERGE `{project_id}.{dataset_id}.DIM_RATE_CODE` T
USING (
    SELECT 1 AS rate_code_id, 'Standard rate' AS rate_code_name, 'Standard meter rate' AS description
    UNION ALL SELECT 2, 'JFK', 'JFK Airport flat rate'
    UNION ALL SELECT 3, 'Newark', 'Newark Airport rate'
    UNION ALL SELECT 4, 'Nassau or Westchester', 'Out of town rate'
    UNION ALL SELECT 5, 'Negotiated fare', 'Negotiated rate'
    UNION ALL SELECT 6, 'Group ride', 'Group ride flat rate'
    UNION ALL SELECT -1, 'Unknown Rate', 'Unspecified rate code'
) S
ON T.rate_code_id = S.rate_code_id AND T.is_current = TRUE
WHEN MATCHED AND (T.rate_code_name != S.rate_code_name OR T.description != S.description) THEN
    UPDATE SET rate_code_name = S.rate_code_name, description = S.description
WHEN NOT MATCHED THEN
    INSERT (rate_code_key, rate_code_id, rate_code_name, description, effective_from, effective_to, is_current)
    VALUES (S.rate_code_id, S.rate_code_id, S.rate_code_name, S.description, CURRENT_TIMESTAMP(), NULL, TRUE);

-- -----------------------------------------------------------------------------
-- 5. Seed DIM_LOCATION Unknown Record
-- -----------------------------------------------------------------------------
MERGE `{project_id}.{dataset_id}.DIM_LOCATION` T
USING (
    SELECT -1 AS location_id, 'Unknown' AS borough, 'Unknown Zone' AS zone, 'Unknown' AS service_zone, 0.0 AS latitude, 0.0 AS longitude
) S
ON T.location_id = S.location_id AND T.is_current = TRUE
WHEN NOT MATCHED THEN
    INSERT (location_key, location_id, borough, zone, service_zone, latitude, longitude, effective_from, effective_to, is_current)
    VALUES (S.location_id, S.location_id, S.borough, S.zone, S.service_zone, S.latitude, S.longitude, CURRENT_TIMESTAMP(), NULL, TRUE);

-- -----------------------------------------------------------------------------
-- 6. Seed DIM_CUSTOMER Unknown Record
-- -----------------------------------------------------------------------------
MERGE `{project_id}.{dataset_id}.DIM_CUSTOMER` T
USING (
    SELECT -1 AS customer_key, 'CUST_UNKNOWN' AS customer_id, 'Guest' AS first_name, 'Rider' AS last_name, 'guest@taxi.nyc' AS email, 'Standard' AS customer_segment
) S
ON T.customer_id = S.customer_id AND T.is_current = TRUE
WHEN NOT MATCHED THEN
    INSERT (customer_key, customer_id, first_name, last_name, email, customer_segment, effective_from, effective_to, is_current)
    VALUES (S.customer_key, S.customer_id, S.first_name, S.last_name, S.email, S.customer_segment, CURRENT_TIMESTAMP(), NULL, TRUE);
