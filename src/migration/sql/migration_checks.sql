-- =============================================================================
-- Migration Quality & Verification Checks SQL Script
-- =============================================================================

-- 1. Table Row Count Verification Template
-- Source Query (MySQL)
SELECT COUNT(*) AS row_count FROM `{table_name}`;

-- Target Query (Alloydb / PostgreSQL)
SELECT COUNT(*) AS row_count FROM "{schema_name}"."{table_name}";

-- 2. Null Value Distribution Check Template
SELECT
    COUNT(*) AS total_rows,
    COUNT("{column_name}") AS non_null_rows,
    COUNT(*) - COUNT("{column_name}") AS null_rows
FROM "{schema_name}"."{table_name}";

-- 3. Foreign Key Orphan Check Template
SELECT COUNT(*) AS orphan_count
FROM "{schema_name}"."{child_table}" C
LEFT JOIN "{schema_name}"."{parent_table}" P
  ON C."{child_column}" = P."{parent_column}"
WHERE P."{parent_column}" IS NULL
  AND C."{child_column}" IS NOT NULL;
