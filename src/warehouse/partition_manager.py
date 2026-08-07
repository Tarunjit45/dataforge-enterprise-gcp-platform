"""Enterprise BigQuery Partition Manager."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

from src.common.config.settings import get_settings
from src.common.exceptions.base import PipelineError
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


class PartitionManager:
    """Manages BigQuery table partitioning strategies, expiration policies, and partition metadata."""

    def __init__(self, bq_client: Any = None):
        self.settings = get_settings()
        self.bq_client = bq_client

    def _get_client(self) -> Any:
        """Lazy-initialize BigQuery client."""
        if self.bq_client is None:
            if bigquery is None:
                raise PipelineError(
                    "google-cloud-bigquery is not installed and no bq_client injected."
                )
            self.bq_client = bigquery.Client(project=self.settings.gcp_project_id)
        return self.bq_client

    def configure_daily_partitioning(
        self,
        dataset_id: str,
        table_id: str,
        partition_field: str = "trip_date",
        expiration_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get or update BigQuery partition configuration object.

        Args:
            dataset_id: Target dataset ID.
            table_id: Target table ID.
            partition_field: Table field to partition on (must be DATE or TIMESTAMP).
            expiration_ms: Optional partition expiration in milliseconds.

        Returns:
            Dict[str, Any]: Partition configuration details.
        """
        partition_config = {
            "type": "DAY",
            "field": partition_field,
            "expiration_ms": expiration_ms,
            "require_partition_filter": True,
        }
        logger.info(
            f"Configured daily partitioning for {dataset_id}.{table_id} on field '{partition_field}' "
            f"(require_partition_filter=True)."
        )
        return partition_config

    def set_table_expiration(self, dataset_id: str, table_id: str, retention_days: int) -> bool:
        """Set default table/partition expiration policy on BigQuery table.

        Args:
            dataset_id: BigQuery dataset ID.
            table_id: Target table ID.
            retention_days: Table retention window in days.

        Returns:
            bool: True if expiration was set successfully.
        """
        client = self._get_client()
        full_table_id = f"{self.settings.gcp_project_id}.{dataset_id}.{table_id}"
        expiration_time = datetime.now(timezone.utc) + timedelta(days=retention_days)

        try:
            table = client.get_table(full_table_id)
            table.expires = expiration_time
            client.update_table(table, ["expires"])
            logger.info(
                f"Set table expiration for {full_table_id} to {expiration_time.isoformat()}"
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to set table expiration on {full_table_id}: {e}")
            return False

    def list_partitions(self, dataset_id: str, table_id: str) -> List[Dict[str, Any]]:
        """Retrieve partition metadata from BigQuery INFORMATION_SCHEMA.PARTITIONS.

        Args:
            dataset_id: BigQuery dataset ID.
            table_id: Target table ID.

        Returns:
            List[Dict[str, Any]]: List of active partition metrics.
        """
        client = self._get_client()
        query = f"""
            SELECT
                partition_id,
                total_rows,
                total_logical_bytes,
                last_modified_time
            FROM `{self.settings.gcp_project_id}.{dataset_id}.INFORMATION_SCHEMA.PARTITIONS`
            WHERE table_name = '{table_id}'
            ORDER BY partition_id DESC
        """
        try:
            query_job = client.query(query)
            results = query_job.result()
            partitions = [
                {
                    "partition_id": row.partition_id,
                    "total_rows": row.total_rows,
                    "total_bytes": row.total_logical_bytes,
                    "last_modified": str(row.last_modified_time),
                }
                for row in results
            ]
            logger.info(f"Retrieved {len(partitions)} partitions for {dataset_id}.{table_id}.")
            return partitions
        except Exception as e:
            logger.error(
                f"Error querying INFORMATION_SCHEMA.PARTITIONS for {dataset_id}.{table_id}: {e}"
            )
            return []

    def drop_partition(self, dataset_id: str, table_id: str, partition_id: str) -> bool:
        """Drop a specific partition from a partitioned BigQuery table.

        Args:
            dataset_id: BigQuery dataset ID.
            table_id: Target table ID.
            partition_id: Partition ID string (e.g., '20260805').

        Returns:
            bool: True if partition drop executed successfully.
        """
        client = self._get_client()
        sql = f"""
            DELETE FROM `{self.settings.gcp_project_id}.{dataset_id}.{table_id}`
            WHERE _PARTITIONDATE = PARSE_DATE('%Y%m%d', '{partition_id}')
        """
        try:
            logger.info(f"Dropping partition '{partition_id}' from {dataset_id}.{table_id}...")
            query_job = client.query(sql)
            query_job.result()
            return True
        except Exception as e:
            logger.error(f"Failed to drop partition '{partition_id}': {e}")
            return False
