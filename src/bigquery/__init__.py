"""BigQuery Data Warehouse & Data Modeling package."""

from src.bigquery.client import get_bigquery_client
from src.bigquery.loader import BigQueryLoader
from src.bigquery.schema_loader import load_bq_schema_from_json

__all__ = [
    "get_bigquery_client",
    "load_bq_schema_from_json",
    "BigQueryLoader",
]
