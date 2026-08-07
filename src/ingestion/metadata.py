"""Ingestion metadata and manifest generation helpers."""

import json
from datetime import datetime, timezone
from typing import Any, Dict

from src.ingestion.base import IngestionPayload


class MetadataGenerator:
    """Helper class for generating standardized metadata and manifest payloads."""

    @staticmethod
    def create_metadata(
        payload: IngestionPayload, extra_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate standardized ingestion metadata dictionary.

        Args:
            payload: Downloaded raw payload model.
            extra_context: Optional dictionary of additional context attributes.

        Returns:
            Dict[str, Any]: JSON-serializable metadata object.
        """
        metadata = {
            "source_name": payload.source_name,
            "entity_name": payload.entity_name,
            "file_name": payload.local_file_path.name,
            "file_size_bytes": payload.file_size_bytes,
            "sha256_checksum": payload.sha256_checksum,
            "content_type": payload.content_type,
            "ingested_at_utc": payload.download_timestamp,
            "schema_version": "1.0",
        }
        if extra_context:
            metadata["context"] = extra_context
        return metadata

    @staticmethod
    def create_manifest(
        payload: IngestionPayload,
        gcs_raw_uri: str,
        execution_id: str,
        status: str = "SUCCESS",
    ) -> Dict[str, Any]:
        """Generate standardized batch manifest dictionary.

        Args:
            payload: Downloaded raw payload model.
            gcs_raw_uri: Target GCS destination URI.
            execution_id: Unique pipeline execution identifier.
            status: Ingestion status ('SUCCESS', 'FAILED').

        Returns:
            Dict[str, Any]: JSON-serializable manifest object.
        """
        return {
            "manifest_version": "1.0",
            "execution_id": execution_id,
            "status": status,
            "source": payload.source_name,
            "entity": payload.entity_name,
            "gcs_payload_uri": gcs_raw_uri,
            "checksum_sha256": payload.sha256_checksum,
            "payload_bytes": payload.file_size_bytes,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
