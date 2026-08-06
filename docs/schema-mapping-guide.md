# MySQL to AlloyDB for PostgreSQL Schema & Data Type Mapping Guide

This guide details the automated translation rules applied by `SchemaConverter` when converting MySQL relational schemas to Google Cloud AlloyDB for PostgreSQL.

---

## 🔀 1. Data Type Mapping Reference Table

| MySQL Source Data Type | AlloyDB / PostgreSQL Target Type | Notes / Handling |
| --- | --- | --- |
| `TINYINT(1)` | `BOOLEAN` | Converted to Boolean true/false when flag enabled |
| `TINYINT` | `SMALLINT` | 8-bit integer mapped to 16-bit SMALLINT |
| `SMALLINT` | `SMALLINT` | Direct 16-bit integer mapping |
| `MEDIUMINT` | `INTEGER` | 24-bit integer mapped to 32-bit INTEGER |
| `INT`, `INTEGER` | `INTEGER` | Direct 32-bit integer mapping |
| `BIGINT` | `BIGINT` | Direct 64-bit integer mapping |
| `DECIMAL(p,s)` | `NUMERIC(p,s)` | Exact precision numeric type |
| `FLOAT` | `REAL` | 32-bit single-precision floating point |
| `DOUBLE` | `DOUBLE PRECISION` | 64-bit double-precision floating point |
| `VARCHAR(n)` | `VARCHAR(n)` | Character string |
| `TEXT`, `MEDIUMTEXT`, `LONGTEXT` | `TEXT` | Variable-length character text |
| `DATETIME` | `TIMESTAMP WITHOUT TIME ZONE` | Exact timestamp without timezone |
| `TIMESTAMP` | `TIMESTAMP WITH TIME ZONE` | UTC timezone-aware timestamp |
| `DATE` | `DATE` | Calendar date |
| `TIME` | `TIME WITHOUT TIME ZONE` | Time of day |
| `BLOB`, `LONGBLOB` | `BYTEA` | Binary byte array |
| `JSON` | `JSONB` | Converted to binary JSONB for index performance |

---

## ⚙️ 2. Structural Object Translation Rules

### Primary Keys & Auto Increment
- MySQL `AUTO_INCREMENT` columns translate directly to ANSI SQL standard `GENERATED ALWAYS AS IDENTITY` sequence columns in AlloyDB:
  ```sql
  -- MySQL Source
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY

  -- AlloyDB Target
  "id" INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY
  ```

### Indexes & Uniqueness
- MySQL indexes (`BTREE`) map to standard PostgreSQL indexes:
  ```sql
  CREATE INDEX IF NOT EXISTS "idx_cust_email" ON "public"."customers" ("email");
  ```
- MySQL `FULLTEXT` indexes are identified during assessment and converted to PostgreSQL `tsvector` / GIN indexes.

### Foreign Keys & Integrity Constraints
- Foreign keys are applied via `ALTER TABLE ... ADD CONSTRAINT` after table creation:
  ```sql
  ALTER TABLE "public"."trips" ADD CONSTRAINT "fk_trips_vendor"
  FOREIGN KEY ("vendor_id") REFERENCES "public"."vendors" ("id");
  ```
