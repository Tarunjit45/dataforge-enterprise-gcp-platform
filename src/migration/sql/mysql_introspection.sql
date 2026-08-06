-- =============================================================================
-- MySQL Database Introspection & Schema Discovery SQL Script
-- =============================================================================

-- 1. Table & View Inventory
SELECT
    TABLE_SCHEMA AS schema_name,
    TABLE_NAME AS table_name,
    TABLE_TYPE AS table_type,
    ENGINE AS storage_engine,
    TABLE_ROWS AS estimated_rows,
    DATA_LENGTH + INDEX_LENGTH AS total_size_bytes,
    AUTO_INCREMENT AS current_auto_increment
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = '{database_name}'
ORDER BY TABLE_NAME;

-- 2. Detailed Column Inventory
SELECT
    TABLE_NAME AS table_name,
    COLUMN_NAME AS column_name,
    ORDINAL_POSITION AS position,
    COLUMN_DEFAULT AS default_value,
    IS_NULLABLE AS is_nullable,
    DATA_TYPE AS data_type,
    COLUMN_TYPE AS full_column_type,
    CHARACTER_MAXIMUM_LENGTH AS char_max_length,
    NUMERIC_PRECISION AS numeric_precision,
    NUMERIC_SCALE AS numeric_scale,
    EXTRA AS extra_attributes
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = '{database_name}'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- 3. Primary & Foreign Key Constraints Inventory
SELECT
    TABLE_NAME AS table_name,
    CONSTRAINT_NAME AS constraint_name,
    CONSTRAINT_TYPE AS constraint_type
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = '{database_name}'
ORDER BY TABLE_NAME, CONSTRAINT_NAME;

-- 4. Foreign Key Relationships Detailed
SELECT
    KCU.TABLE_NAME AS source_table,
    KCU.COLUMN_NAME AS source_column,
    KCU.CONSTRAINT_NAME AS constraint_name,
    KCU.REFERENCED_TABLE_NAME AS target_table,
    KCU.REFERENCED_COLUMN_NAME AS target_column
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE KCU
JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS RC
  ON KCU.CONSTRAINT_NAME = RC.CONSTRAINT_NAME
  AND KCU.CONSTRAINT_SCHEMA = RC.CONSTRAINT_SCHEMA
WHERE KCU.CONSTRAINT_SCHEMA = '{database_name}'
ORDER BY KCU.TABLE_NAME;

-- 5. Index Details Inventory
SELECT
    TABLE_NAME AS table_name,
    INDEX_NAME AS index_name,
    NON_UNIQUE AS non_unique,
    COLUMN_NAME AS column_name,
    SEQ_IN_INDEX AS sequence_in_index,
    INDEX_TYPE AS index_type
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = '{database_name}'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
