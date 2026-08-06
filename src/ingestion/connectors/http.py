"""HTTP/REST API base connector implementation."""

from datetime import datetime
from pathlib import Path
import urllib.request

from src.common.exceptions.base import ValidationError
from src.common.logging.logger import get_logger
from src.common.utils.retry_utils import retry_on_exception
from src.ingestion.base import BaseConnector, IngestionPayload

logger = get_logger(__name__)


class HTTPConnector(BaseConnector):
    """Base connector for fetching raw payloads over HTTP/HTTPS with retry logic."""

    def __init__(self, source_name: str, entity_name: str, base_url: str):
        super().__init__(source_name, entity_name)
        self.base_url = base_url.rstrip("/")

    @retry_on_exception(max_retries=3, backoff_factor=2.0, allowed_exceptions=(Exception,))
    def download_url_to_file(self, url: str, target_path: Path) -> Path:
        """Download remote URL payload to a local target file path.

        Args:
            url: Remote URL.
            target_path: Local output file path.

        Returns:
            Path: Downloaded file path.
        """
        logger.info(f"Downloading payload from URL: {url} -> {target_path}")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, target_path)
        return target_path

    def fetch_payload(self, target_date: datetime, output_dir: Path) -> IngestionPayload:
        """Fetch payload implementation (override in subclasses)."""
        raise NotImplementedError("Subclasses must implement fetch_payload()")

    def validate_payload(self, payload: IngestionPayload) -> bool:
        """Validate basic payload parameters."""
        if not payload.local_file_path.exists():
            raise ValidationError(f"Payload file does not exist: {payload.local_file_path}")
        if payload.file_size_bytes <= 0:
            raise ValidationError(f"Payload file is empty: {payload.local_file_path}")
        return True
