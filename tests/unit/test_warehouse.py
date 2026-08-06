"""Unit tests for Enterprise BigQuery Gold Warehouse & Analytics Layer (Phase 8)."""

from pathlib import Path
from unittest.mock import MagicMock
import pytest

from src.common.exceptions.base import ConfigurationError, QualityCheckError
from src.warehouse.clustering import ClusteringManager
from src.warehouse.loader import GoldWarehouseLoader
from src.warehouse.models.metadata import WarehouseLoadMetadata
from src.warehouse.models.star_schema import SCDType, get_star_schema_definition
from src.warehouse.partition_manager import PartitionManager


@pytest.mark.unit
def test_star_schema_definition():
    """Verify Star Schema model definitions and foreign key relationships."""
    schema = get_star_schema_definition()
    assert "dimensions" in schema
    assert "facts" in schema
    dims = schema["dimensions"]
    facts = schema["facts"]

    assert "DIM_DATE" in dims
    assert "DIM_VENDOR" in dims
    assert "DIM_PAYMENT_TYPE" in dims
    assert "DIM_LOCATION" in dims
    assert "DIM_RATE_CODE" in dims
    assert "DIM_CUSTOMER" in dims
    assert "FACT_TAXI_TRIPS" in facts

    assert dims["DIM_VENDOR"].scd_type == SCDType.TYPE_2
    assert dims["DIM_PAYMENT_TYPE"].scd_type == SCDType.TYPE_2

    fact = facts["FACT_TAXI_TRIPS"]
    assert fact.partition_column == "trip_date"
    assert "vendor_key" in fact.cluster_columns
    assert fact.foreign_keys["vendor_key"] == "DIM_VENDOR"


@pytest.mark.unit
def test_warehouse_metadata_model():
    """Verify WarehouseLoadMetadata creation and dictionary serialization."""
    metadata = WarehouseLoadMetadata(
        batch_id="batch_20260806_001",
        source_execution_id="exec_999",
        source_manifest="gs://processed/manifest.json",
        data_quality_score=95.5,
        records_read=5000,
        records_inserted=5000,
    )

    data_dict = metadata.to_dict()
    assert data_dict["batch_id"] == "batch_20260806_001"
    assert data_dict["data_quality_score"] == 95.5
    assert data_dict["records_read"] == 5000
    assert "load_timestamp" in data_dict


@pytest.mark.unit
def test_partition_manager():
    """Verify PartitionManager configuration and partition listing."""
    mock_client = MagicMock()
    mock_row = MagicMock()
    mock_row.partition_id = "20260806"
    mock_row.total_rows = 10000
    mock_row.total_logical_bytes = 500000
    mock_row.last_modified_time = "2026-08-06 12:00:00"
    mock_client.query.return_value.result.return_value = [mock_row]

    pm = PartitionManager(bq_client=mock_client)

    # Test daily partition config
    config = pm.configure_daily_partitioning("gold_analytics", "FACT_TAXI_TRIPS", "trip_date")
    assert config["field"] == "trip_date"
    assert config["require_partition_filter"] is True

    # Test partition listing
    partitions = pm.list_partitions("gold_analytics", "FACT_TAXI_TRIPS")
    assert len(partitions) == 1
    assert partitions[0]["partition_id"] == "20260806"

    # Test drop partition
    success = pm.drop_partition("gold_analytics", "FACT_TAXI_TRIPS", "20260806")
    assert success is True


@pytest.mark.unit
def test_clustering_manager():
    """Verify ClusteringManager validation and spec generation."""
    mock_client = MagicMock()
    cm = ClusteringManager(bq_client=mock_client)

    # Test valid cluster columns
    valid_cols = ["vendor_key", "payment_type_key", "pickup_location_key", "rate_code_key"]
    spec = cm.get_clustering_spec(valid_cols)
    assert spec["fields"] == valid_cols

    # Test exceeding max cluster columns (5 cols should raise ConfigurationError)
    invalid_cols = valid_cols + ["extra_col"]
    with pytest.raises(ConfigurationError):
        cm.validate_cluster_columns(invalid_cols)

    # Test reclustering call
    recluster_status = cm.recluster_table("gold_analytics", "FACT_TAXI_TRIPS", valid_cols)
    assert recluster_status is True


@pytest.mark.unit
def test_gold_warehouse_loader_incremental_merge():
    """Test GoldWarehouseLoader load_incremental_fact with valid DQ score."""
    mock_client = MagicMock()
    mock_job = MagicMock()
    mock_job.num_dml_affected_rows = 2500
    mock_client.query.return_value = mock_job

    loader = GoldWarehouseLoader(bq_client=mock_client)
    metadata = loader.load_incremental_fact(
        batch_id="batch_100",
        source_execution_id="exec_100",
        source_manifest="gs://processed/manifest.json",
        data_quality_score=92.0,
        dataset_id="gold_analytics",
    )

    assert metadata.batch_id == "batch_100"
    assert metadata.records_inserted == 2500
    assert mock_client.query.called


@pytest.mark.unit
def test_gold_warehouse_loader_dq_rejection():
    """Test GoldWarehouseLoader load_incremental_fact rejecting batch below DQ threshold."""
    mock_client = MagicMock()
    loader = GoldWarehouseLoader(bq_client=mock_client)

    with pytest.raises(QualityCheckError, match="Data Quality score 65.00% is below Gold Warehouse threshold"):
        loader.load_incremental_fact(
            batch_id="batch_fail",
            source_execution_id="exec_fail",
            source_manifest="gs://processed/manifest.json",
            data_quality_score=65.0,  # Below 70.0% threshold
            dataset_id="gold_analytics",
        )


@pytest.mark.unit
def test_sql_templates_validity():
    """Verify all Phase 8 warehouse SQL script templates exist and format cleanly."""
    sql_dir = Path(__file__).resolve().parents[2] / "src" / "warehouse" / "sql"
    sql_files = [
        "create_dimensions.sql",
        "create_fact_tables.sql",
        "load_dimensions.sql",
        "load_fact_tables.sql",
        "incremental_merge.sql",
        "views.sql",
        "data_marts.sql",
    ]

    for sql_file in sql_files:
        filepath = sql_dir / sql_file
        assert filepath.exists(), f"SQL template missing: {filepath}"
        content = filepath.read_text(encoding="utf-8")
        assert len(content) > 0

        # Formatter validation test with dummy variables
        formatted = content.format(
            project_id="test-project",
            dataset_id="gold_analytics",
            staged_dataset="silver_staged",
            batch_id="test_batch",
            source_execution_id="test_exec",
            source_manifest="gs://test/manifest.json",
            data_quality_score=95.0,
            kms_key_name="projects/test/locations/us/keyRings/ring/cryptoKeys/key",
        )
        assert "test-project" in formatted
