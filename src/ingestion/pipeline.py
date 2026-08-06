"""Enterprise Data Ingestion Pipeline Runner."""

from datetime import datetime, timezone
from typing import Any, Dict
from pathlib import Path
import time
import uuid
import json

try:
    from google.cloud import storage
except ImportError:
    storage = None  # Handled dynamically in _get_gcs_client when client is not injected

from src.common.config.settings import get_settings
from src.common.exceptions.base import CloudStorageError, PipelineError
from src.common.logging.logger import get_logger, set_correlation_id
from src.ingestion.base import BaseConnector, IngestionResult
from src.ingestion.metadata import MetadataGenerator

logger = get_logger(__name__)


class IngestionPipeline:
    """Reusable, multi-stage ingestion pipeline orchestrator."""

    def __init__(self, connector: BaseConnector, gcs_client: Any = None):
        self.connector = connector
        self.settings = get_settings()
        self.gcs_client = gcs_client

    def _get_gcs_client(self) -> Any:
        """Lazy-initialize GCS client if not injected."""
        if self.gcs_client is None:
            if storage is None:
                raise CloudStorageError(
                    "google-cloud-storage library is not installed and no gcs_client was injected."
                )
            self.gcs_client = storage.Client(project=self.settings.gcp_project_id)
        return self.gcs_client

    def _build_gcs_partition_path(self, target_date: datetime, filename: str) -> str:
        """Construct standard partition path: raw/<source>/<entity>/YYYY/MM/DD/<filename>"""
        date_path = target_date.strftime("%Y/%m/%d")
        return f"raw/{self.connector.source_name}/{self.connector.entity_name}/{date_path}/{filename}"

    def upload_to_gcs(self, bucket_name: str, destination_blob: str, local_path: Path) -> str:
        """Upload a local file to GCS.

        Args:
            bucket_name: Target bucket name (without gs:// prefix).
            destination_blob: Object key path.
            local_path: Local file path.

        Returns:
            str: Full GCS URI (gs://bucket/blob).
        """
        clean_bucket = bucket_name.replace("gs://", "")
        try:
            client = self._get_gcs_client()
            bucket = client.bucket(clean_bucket)
            blob = bucket.blob(destination_blob)
            blob.upload_from_filename(str(local_path))
            gcs_uri = f"gs://{clean_bucket}/{destination_blob}"
            logger.info(f"Successfully uploaded {local_path.name} to {gcs_uri}")
            return gcs_uri
        except Exception as e:
            raise CloudStorageError(f"Failed to upload {local_path} to GCS: {e}") from e

    def upload_json_to_gcs(self, bucket_name: str, destination_blob: str, json_data: dict) -> str:
        """Upload a dictionary payload as JSON to GCS.

        Args:
            bucket_name: Target bucket name.
            destination_blob: Object key path.
            json_data: Dictionary payload.

        Returns:
            str: Full GCS URI.
        """
        clean_bucket = bucket_name.replace("gs://", "")
        try:
            client = self._get_gcs_client()
            bucket = client.bucket(clean_bucket)
            blob = bucket.blob(destination_blob)
            blob.upload_from_string(json.dumps(json_data, indent=2), content_type="application/json")
            gcs_uri = f"gs://{clean_bucket}/{destination_blob}"
            logger.info(f"Uploaded JSON manifest/metadata to {gcs_uri}")
            return gcs_uri
        except Exception as e:
            raise CloudStorageError(f"Failed to upload JSON to GCS: {e}") from e

    def run(self, target_date: datetime, local_staging_dir: Path) -> IngestionResult:
        """Execute the end-to-end multi-stage ingestion pipeline.

        Args:
            target_date: Target date partition.
            local_staging_dir: Directory for temporary file staging.

        Returns:
            IngestionResult: Completed pipeline execution metadata result.
        """
        execution_id = str(uuid.uuid4())
        set_correlation_id(execution_id)
        start_time = time.time()

        logger.info(
            f"Starting Ingestion Pipeline | ExecutionID: {execution_id} | "
            f"Source: {self.connector.source_name} | Entity: {self.connector.entity_name} | "
            f"Date: {target_date.strftime('%Y-%m-%d')}"
        )

        try:
            # Stage 1: Fetch Payload
            payload = self.connector.fetch_payload(target_date, local_staging_dir)

            # Stage 2: Validate Payload
            self.connector.validate_payload(payload)

            # Stage 3: Create Metadata
            metadata = MetadataGenerator.create_metadata(payload, {"execution_id": execution_id})

            # Stage 4: Upload Raw Payload & Metadata to GCS Bronze Bucket
            raw_bucket = self.settings.raw_bucket or f"gs://{self.settings.gcp_project_id}-raw-bronze"
            payload_blob = self._build_gcs_partition_path(target_date, payload.local_file_path.name)
            raw_gcs_uri = self.upload_to_gcs(raw_bucket, payload_blob, payload.local_file_path)

            meta_blob = self._build_gcs_partition_path(target_date, "metadata.json")
            self.upload_json_to_gcs(raw_bucket, meta_blob, metadata)

            # Stage 5: Create & Upload Manifest
            manifest = MetadataGenerator.create_manifest(payload, raw_gcs_uri, execution_id, "SUCCESS")
            manifest_blob = self._build_gcs_partition_path(target_date, "manifest.json")
            manifest_gcs_uri = self.upload_json_to_gcs(raw_bucket, manifest_blob, manifest)

            duration = time.time() - start_time
            logger.info(
                f"Ingestion Pipeline Completed Successfully in {duration:.2f}s | "
                f"GCS Payload: {raw_gcs_uri}"
            )

            return IngestionResult(
                success=True,
                source_name=self.connector.source_name,
                entity_name=self.connector.entity_name,
                records_ingested=1,
                raw_gcs_uri=raw_gcs_uri,
                manifest_gcs_uri=manifest_gcs_uri,
                execution_duration_seconds=duration,
                metadata=metadata,
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Ingestion Pipeline Failed after {duration:.2f}s: {e}", exc_info=True)
            return IngestionResult(
                success=False,
                source_name=self.connector.source_name,
                entity_name=self.connector.entity_name,
                records_ingested=0,
                raw_gcs_uri="",
                manifest_gcs_uri="",
                execution_duration_seconds=duration,
                error_message=str(e),
            )
