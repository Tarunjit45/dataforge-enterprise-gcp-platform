"""BigQuery JSON schema contract loader utility."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

try:
    from google.cloud import bigquery

    SchemaFieldClass = bigquery.SchemaField
except ImportError:

    @dataclass
    class SchemaFieldFallback:
        name: str
        field_type: str
        mode: str = "NULLABLE"
        description: str = ""

    SchemaFieldClass = SchemaFieldFallback

from src.common.exceptions.base import ConfigurationError
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


def load_bq_schema_from_json(schema_name: str) -> List[Any]:
    """Load BigQuery SchemaField definitions from JSON contract file.

    Args:
        schema_name: Schema file name (e.g. 'fact_trips' or 'dim_customers').

    Returns:
        List[Any]: Parsed BigQuery schema fields.

    Raises:
        ConfigurationError: If schema file is missing or invalid.
    """
    root_dir = Path(__file__).resolve().parents[2]
    schema_file = root_dir / "config" / "bq_schemas" / f"{schema_name}.json"

    if not schema_file.exists():
        raise ConfigurationError(f"BigQuery JSON schema definition missing: {schema_file}")

    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            raw_fields = json.load(f)

        schema_fields = [
            SchemaFieldClass(
                name=field["name"],
                field_type=field["type"],
                mode=field.get("mode", "NULLABLE"),
                description=field.get("description", ""),
            )
            for field in raw_fields
        ]
        logger.info(
            f"Successfully loaded BigQuery schema '{schema_name}' ({len(schema_fields)} fields)."
        )
        return schema_fields
    except Exception as e:
        raise ConfigurationError(f"Failed to parse BigQuery schema JSON {schema_file}: {e}") from e
