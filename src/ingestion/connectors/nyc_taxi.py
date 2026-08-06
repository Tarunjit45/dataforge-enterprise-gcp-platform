"""NYC Taxi dataset ingestion connector implementation."""

from datetime import datetime
from pathlib import Path

from src.common.logging.logger import get_logger
from src.ingestion.base import IngestionPayload
from src.ingestion.connectors.http import HTTPConnector

logger = get_logger(__name__)


class NYCTaxiConnector(HTTPConnector):
    """Connector for downloading public NYC TLC Yellow Taxi trip datasets."""

    DEFAULT_BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        super().__init__(
            source_name="nyc_tlc",
            entity_name="yellow_taxi",
            base_url=base_url,
        )

    def build_download_url(self, target_date: datetime) -> str:
        """Construct public S3/CloudFront URL for target date month payload.

        Args:
            target_date: Target extraction date.

        Returns:
            str: Full download URL.
        """
        year_month = target_date.strftime("%Y-%m")
        file_name = f"yellow_tripdata_{year_month}.parquet"
        return f"{self.base_url}/{file_name}"

    def fetch_payload(self, target_date: datetime, output_dir: Path) -> IngestionPayload:
        """Download NYC Taxi Parquet payload for target year/month.

        Args:
            target_date: Extraction partition date.
            output_dir: Staging destination directory.

        Returns:
            IngestionPayload: Downloaded payload metadata.
        """
        url = self.build_download_url(target_date)
        file_name = f"yellow_tripdata_{target_date.strftime('%Y_%m')}.parquet"
        local_path = output_dir / file_name

        self.download_url_to_file(url, local_path)

        file_size = local_path.stat().st_size
        checksum = self.calculate_sha256(local_path)

        logger.info(
            f"Successfully staged NYC Taxi dataset: {file_name} "
            f"Size: {file_size} bytes, SHA256: {checksum[:8]}..."
        )

        return IngestionPayload(
            source_name=self.source_name,
            entity_name=self.entity_name,
            local_file_path=local_path,
            content_type="application/x-parquet",
            file_size_bytes=file_size,
            sha256_checksum=checksum,
        )
