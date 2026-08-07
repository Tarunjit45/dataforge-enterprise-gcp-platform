"""MySQL to AlloyDB Schema Conversion Engine."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from src.common.config.settings import get_settings
from src.common.exceptions.base import ConfigurationError, PipelineError
from src.common.logging.logger import get_logger
from src.migration.metadata import ColumnMetadata, DatabaseInventory, TableSchema

logger = get_logger(__name__)


class SchemaConverter:
    """Automated MySQL to PostgreSQL / AlloyDB Schema DDL Conversion Engine."""

    DEFAULT_DATA_TYPE_MAPPINGS = {
        "tinyint(1)": "BOOLEAN",
        "tinyint": "SMALLINT",
        "smallint": "SMALLINT",
        "mediumint": "INTEGER",
        "int": "INTEGER",
        "integer": "INTEGER",
        "bigint": "BIGINT",
        "decimal": "NUMERIC",
        "numeric": "NUMERIC",
        "float": "REAL",
        "double": "DOUBLE PRECISION",
        "datetime": "TIMESTAMP WITHOUT TIME ZONE",
        "timestamp": "TIMESTAMP WITH TIME ZONE",
        "date": "DATE",
        "time": "TIME WITHOUT TIME ZONE",
        "varchar": "VARCHAR",
        "char": "CHAR",
        "text": "TEXT",
        "tinytext": "TEXT",
        "mediumtext": "TEXT",
        "longtext": "TEXT",
        "blob": "BYTEA",
        "mediumblob": "BYTEA",
        "longblob": "BYTEA",
        "json": "JSONB",
    }

    def __init__(self, mapping_config_path: Optional[str] = None):
        self.settings = get_settings()
        self.type_mappings = dict(self.DEFAULT_DATA_TYPE_MAPPINGS)
        self._load_datatype_mappings(mapping_config_path)

    def _load_datatype_mappings(self, mapping_config_path: Optional[str]) -> None:
        """Load external data type mapping YAML configuration if available."""
        if mapping_config_path is None:
            root_dir = Path(__file__).resolve().parents[2]
            yaml_path = root_dir / "config" / "migration" / "datatype_mapping.yaml"
        else:
            yaml_path = Path(mapping_config_path)

        if yaml_path.exists():
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "data_type_mappings" in data:
                        for k, v in data["data_type_mappings"].items():
                            if isinstance(v, dict) and "target" in v:
                                self.type_mappings[k.lower()] = v["target"]
            except Exception as e:
                logger.warning(
                    f"Could not parse datatype_mapping.yaml ({e}). Using built-in mappings."
                )

    def convert_column_type(self, raw_type: str, full_type: str = "") -> str:
        """Convert MySQL data type string to PostgreSQL / AlloyDB equivalent.

        Args:
            raw_type: MySQL data type name (e.g. 'int', 'varchar', 'tinyint').
            full_type: Complete MySQL type declaration (e.g. 'tinyint(1)', 'varchar(255)').

        Returns:
            str: PostgreSQL / AlloyDB data type declaration.
        """
        full_lower = full_type.strip().lower()
        base_type = raw_type.strip().lower()

        if full_lower == "tinyint(1)":
            return "BOOLEAN"

        if full_lower.startswith("varchar"):
            return full_lower.upper()

        if full_lower.startswith("decimal") or full_lower.startswith("numeric"):
            return full_lower.upper()

        return self.type_mappings.get(base_type, self.type_mappings.get(full_lower, "VARCHAR(255)"))

    def generate_alloydb_ddl(
        self,
        inventory: DatabaseInventory,
        target_schema: str = "public",
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate PostgreSQL / AlloyDB compatible DDL scripts from MySQL inventory.

        Args:
            inventory: Source MySQL DatabaseInventory model.
            target_schema: Target PostgreSQL schema name.

        Returns:
            Tuple[str, Dict[str, Any]]: Generated SQL DDL string and conversion report dictionary.
        """
        logger.info(f"Generating AlloyDB DDL DDL scripts for {len(inventory.tables)} tables...")
        ddl_statements: List[str] = [
            f"-- =============================================================================",
            f"-- Auto-Generated AlloyDB / PostgreSQL DDL Script",
            f"-- Source Database: {inventory.database_name}",
            f"-- Target Schema: {target_schema}",
            f"-- =============================================================================",
            f'CREATE SCHEMA IF NOT EXISTS "{target_schema}";',
            "",
        ]

        converted_tables = 0
        converted_columns = 0
        converted_indexes = 0
        converted_fks = 0

        for table_name, table in inventory.tables.items():
            lines: List[str] = [f'CREATE TABLE IF NOT EXISTS "{target_schema}"."{table_name}" (']
            col_defs: List[str] = []
            pk_cols: List[str] = []

            for col in table.columns:
                converted_columns += 1
                col_type = self.convert_column_type(col.data_type, col.full_type)
                nullable = "" if col.is_nullable else " NOT NULL"

                identity_str = ""
                if col.is_auto_increment:
                    identity_str = " GENERATED ALWAYS AS IDENTITY"

                default_str = ""
                if col.default_value is not None and not col.is_auto_increment:
                    def_val = col.default_value
                    if def_val.upper() in ("CURRENT_TIMESTAMP", "NOW()"):
                        def_val = "CURRENT_TIMESTAMP"
                    elif not def_val.startswith("'") and not def_val.isnumeric():
                        def_val = f"'{def_val}'"
                    default_str = f" DEFAULT {def_val}"

                col_defs.append(f'    "{col.name}" {col_type}{identity_str}{nullable}{default_str}')

                if col.is_primary_key:
                    pk_cols.append(f'"{col.name}"')

            if pk_cols:
                pk_str = ", ".join(pk_cols)
                col_defs.append(f"    PRIMARY KEY ({pk_str})")

            lines.append(",\n".join(col_defs))
            lines.append(");")
            lines.append("")

            ddl_statements.append("\n".join(lines))
            converted_tables += 1

            # Indexes DDL
            for idx in table.indexes:
                if idx.index_name.upper() == "PRIMARY":
                    continue
                converted_indexes += 1
                unique_str = "UNIQUE " if idx.is_unique else ""
                idx_cols = ", ".join([f'"{c}"' for c in idx.columns])
                idx_ddl = f'CREATE {unique_str}INDEX IF NOT EXISTS "{idx.index_name}" ON "{target_schema}"."{table_name}" ({idx_cols});'
                ddl_statements.append(idx_ddl)

            if table.indexes:
                ddl_statements.append("")

            # Foreign Keys DDL
            for fk in table.foreign_keys:
                converted_fks += 1
                fk_ddl = (
                    f'ALTER TABLE "{target_schema}"."{table_name}" '
                    f'ADD CONSTRAINT "{fk.constraint_name}" '
                    f'FOREIGN KEY ("{fk.source_column}") '
                    f'REFERENCES "{target_schema}"."{fk.target_table}" ("{fk.target_column}");'
                )
                ddl_statements.append(fk_ddl)

            if table.foreign_keys:
                ddl_statements.append("")

        full_sql = "\n".join(ddl_statements)

        conversion_report = {
            "database_name": inventory.database_name,
            "target_schema": target_schema,
            "converted_tables_count": converted_tables,
            "converted_columns_count": converted_columns,
            "converted_indexes_count": converted_indexes,
            "converted_foreign_keys_count": converted_fks,
            "status": "SUCCESS",
        }

        logger.info(
            f"Successfully converted schema. Tables: {converted_tables}, Columns: {converted_columns}, "
            f"Indexes: {converted_indexes}, FKs: {converted_fks}."
        )
        return full_sql, conversion_report

    def save_conversion_output(
        self,
        full_sql: str,
        conversion_report: Dict[str, Any],
        output_dir: str = ".",
    ) -> Dict[str, str]:
        """Save schema_conversion_report.json and converted_schema.sql.

        Args:
            full_sql: Generated AlloyDB DDL string.
            conversion_report: Conversion report metrics dictionary.
            output_dir: Target output directory path.

        Returns:
            Dict[str, str]: File paths of generated DDL and report files.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        sql_file = out_path / "converted_schema.sql"
        report_file = out_path / "schema_conversion_report.json"

        with open(sql_file, "w", encoding="utf-8") as f:
            f.write(full_sql)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(conversion_report, f, indent=2)

        logger.info(
            f"Saved conversion DDL to '{sql_file.resolve()}' and report to '{report_file.resolve()}'."
        )
        return {
            "converted_sql": str(sql_file.resolve()),
            "conversion_report_json": str(report_file.resolve()),
        }
