"""Unit tests for Enterprise Data Ingestion Framework."""

from datetime import datetime, timezone
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.common.exceptions.base import ValidationError
from src.ingestion.base import BaseConnector, IngestionPayload
from src.ingestion.connectors.http import HTTPConnector
from src.ingestion.connectors.nyc_taxi import NYCTaxiConnector
from src.ingestion.metadata import MetadataGenerator
from src.ingestion.pipeline import IngestionPipeline


@pytest.mark.unit
def test_sha256_calculation(tmp_path: Path):
    """Verify SHA256 calculation logic."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello data platform", encoding="utf-8")

    checksum = BaseConnector.calculate_sha256(test_file)
    assert isinstance(checksum, str)
    assert len(checksum) == 64


@pytest.mark.unit
def test_nyc_taxi_connector_url_building():
    """Verify NYC Taxi URL construction."""
    connector = NYCTaxiConnector()
    target_date = datetime(2024, 1, 15)

    url = connector.build_download_url(target_date)
    assert url == "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"


@pytest.mark.unit
def test_metadata_and_manifest_creation(tmp_path: Path):
    """Verify metadata and manifest generation structure."""
    file_path = tmp_path / "sample.parquet"
    file_path.write_bytes(b"mock bytes")

    payload = IngestionPayload(
        source_name="nyc_tlc",
        entity_name="yellow_taxi",
        local_file_path=file_path,
        content_type="application/x-parquet",
        file_size_bytes=10,
        sha256_checksum="mocksha256",
    )

    metadata = MetadataGenerator.create_metadata(payload, {"test": True})
    assert metadata["source_name"] == "nyc_tlc"
    assert metadata["file_size_bytes"] == 10
    assert metadata["context"]["test"] is True

    manifest = MetadataGenerator.create_manifest(payload, "gs://raw-bucket/blob", "exec-123", "SUCCESS")
    assert manifest["execution_id"] == "exec-123"
    assert manifest["status"] == "SUCCESS"
    assert manifest["gcs_payload_uri"] == "gs://raw-bucket/blob"


@pytest.mark.unit
def test_ingestion_pipeline_run_success(tmp_path: Path):
    """Test full IngestionPipeline execution with mocked GCS client."""
    mock_file = tmp_path / "yellow_tripdata_2024_01.parquet"
    mock_file.write_bytes(b"dummy parquet binary data")

    mock_connector = NYCTaxiConnector()
    mock_connector.fetch_payload = MagicMock(
        return_value=IngestionPayload(
            source_name="nyc_tlc",
            entity_name="yellow_taxi",
            local_file_path=mock_file,
            content_type="application/x-parquet",
            file_size_bytes=25,
            sha256_checksum="mockchecksum123",
        )
    )

    mock_gcs = MagicMock()
    pipeline = IngestionPipeline(connector=mock_connector, gcs_client=mock_gcs)

    result = pipeline.run(target_date=datetime(2024, 1, 1), local_staging_dir=tmp_path)

    assert result.success is True
    assert result.source_name == "nyc_tlc"
    assert result.entity_name == "yellow_taxi"
    assert "gs://" in result.raw_gcs_uri
    assert mock_gcs.bucket.called
