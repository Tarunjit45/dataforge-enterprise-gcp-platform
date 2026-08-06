-- =============================================================================
-- PostgreSQL / AlloyDB Target Inspection & Validation SQL Script
-- =============================================================================

-- 1. Target Schema & Table Inventory
SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = '{schema_name}'
ORDER BY table_name;

-- 2. Target Column Inventory & Data Types
SELECT
    table_name,
    column_name,
    ordinal_position,
    column_default,
    is_nullable,
    data_type,
    character_maximum_length,
    numeric_precision,
    numeric_scale
FROM information_schema.columns
WHERE table_schema = '{schema_name}'
ORDER BY table_name, ordinal_position;

-- 3. Target Foreign Key Constraints Verification
SELECT
    tc.table_name AS source_table,
    kcu.column_name AS source_column,
    tc.constraint_name,
    ccu.table_name AS target_table,
    ccu.column_name AS target_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
  ON tc.constraint_name = ccu.constraint_name
  AND tc.table_schema = ccu.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = '{schema_name}'
ORDER BY tc.table_name;

-- 4. Target Identity / Sequence Status
SELECT
    sequence_name,
    start_value,
    minimum_value,
    maximum_value,
    increment
FROM information_schema.sequences
WHERE sequence_schema = '{schema_name}';
