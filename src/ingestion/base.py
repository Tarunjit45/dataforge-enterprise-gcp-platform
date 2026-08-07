"""Abstract base connector and ingestion result models."""

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class IngestionPayload:
    """Model representing a downloaded raw payload staged locally."""

    source_name: str
    entity_name: str
    local_file_path: Path
    content_type: str
    file_size_bytes: int
    sha256_checksum: str
    download_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class IngestionResult:
    """Model representing the final result of an ingestion pipeline run."""

    success: bool
    source_name: str
    entity_name: str
    records_ingested: int
    raw_gcs_uri: str
    manifest_gcs_uri: str
    execution_duration_seconds: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseConnector(ABC):
    """Abstract Base Class for all enterprise data ingestion connectors."""

    def __init__(self, source_name: str, entity_name: str):
        self.source_name = source_name
        self.entity_name = entity_name

    @abstractmethod
    def fetch_payload(self, target_date: datetime, output_dir: Path) -> IngestionPayload:
        """Fetch raw payload from external source and save locally.

        Args:
            target_date: Date partition for data extraction.
            output_dir: Local staging directory.

        Returns:
            IngestionPayload: Downloaded payload object.
        """
        pass

    @abstractmethod
    def validate_payload(self, payload: IngestionPayload) -> bool:
        """Validate payload integrity, header format, and file size.

        Args:
            payload: Downloaded payload to validate.

        Returns:
            bool: True if payload is valid.
        """
        pass

    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        """Calculate SHA256 checksum of a file.

        Args:
            file_path: Local file path.

        Returns:
            str: Hexadecimal SHA256 checksum string.
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
