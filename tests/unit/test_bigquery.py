"""Unit tests for BigQuery Data Warehouse loader engine."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.bigquery.loader import BigQueryLoader
from src.bigquery.schema_loader import load_bq_schema_from_json


@pytest.mark.unit
def test_load_bq_schema_from_json():
    """Verify loading JSON schema definitions for Star Schema tables."""
    schema = load_bq_schema_from_json("fact_trips")
    assert isinstance(schema, list)
    assert len(schema) > 0
    field_names = [f.name for f in schema]
    assert "tpep_pickup_datetime" in field_names
    assert "VendorID" in field_names


@pytest.mark.unit
def test_bigquery_loader_parquet_load():
    """Test BigQueryLoader load_parquet_from_gcs with mocked BigQuery client."""
    mock_client = MagicMock()
    mock_job = MagicMock()
    mock_client.load_table_from_uri.return_value = mock_job
    mock_table = MagicMock()
    mock_table.num_rows = 1500
    mock_client.get_table.return_value = mock_table

    loader = BigQueryLoader(bq_client=mock_client)
    loaded_rows = loader.load_parquet_from_gcs(
        gcs_uri="gs://test-bucket/path/*.parquet",
        dataset_id="test_dataset",
        table_id="fact_trips",
    )

    assert loaded_rows == 1500
    assert mock_client.load_table_from_uri.called


@pytest.mark.unit
def test_bigquery_loader_merge_upsert():
    """Test BigQueryLoader execute_merge_upsert with mocked BigQuery client."""
    mock_client = MagicMock()
    mock_job = MagicMock()
    mock_job.num_dml_affected_rows = 450
    mock_client.query.return_value = mock_job

    loader = BigQueryLoader(bq_client=mock_client)
    affected_rows = loader.execute_merge_upsert(
        sql_file_name="merge_fact_trips.sql",
        dataset_id="gold_analytics",
    )

    assert affected_rows == 450
    assert mock_client.query.called
