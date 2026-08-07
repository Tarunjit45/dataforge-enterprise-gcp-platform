"""Enterprise BigQuery Clustering Manager."""

from typing import Any, Dict, List, Optional

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

from src.common.config.settings import get_settings
from src.common.exceptions.base import ConfigurationError, PipelineError
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


class ClusteringManager:
    """Manages BigQuery table clustering strategies, column ordering, and reclustering operations."""

    MAX_CLUSTERING_COLUMNS = 4

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

    def validate_cluster_columns(self, cluster_columns: List[str]) -> List[str]:
        """Validate BigQuery cluster column requirements.

        Args:
            cluster_columns: List of column names to cluster by.

        Returns:
            List[str]: Validated list of cluster columns.

        Raises:
            ConfigurationError: If cluster column count exceeds BigQuery limit (4).
        """
        if not cluster_columns:
            raise ConfigurationError("Clustering column list cannot be empty.")
        if len(cluster_columns) > self.MAX_CLUSTERING_COLUMNS:
            raise ConfigurationError(
                f"BigQuery supports maximum {self.MAX_CLUSTERING_COLUMNS} cluster columns. Got {len(cluster_columns)}."
            )
        logger.info(f"Validated {len(cluster_columns)} cluster columns: {cluster_columns}")
        return cluster_columns

    def get_clustering_spec(self, cluster_columns: List[str]) -> Dict[str, Any]:
        """Generate BigQuery clustering specification dictionary.

        Args:
            cluster_columns: List of columns to cluster table by.

        Returns:
            Dict[str, Any]: BigQuery cluster specification object.
        """
        validated_cols = self.validate_cluster_columns(cluster_columns)
        return {"fields": validated_cols}

    def recluster_table(self, dataset_id: str, table_id: str, cluster_columns: List[str]) -> bool:
        """Execute table reclustering / reorganization query in BigQuery.

        In BigQuery, running a `MERGE` or `CREATE OR REPLACE TABLE ... AS SELECT * FROM ...` reclusters the data.

        Args:
            dataset_id: BigQuery dataset ID.
            table_id: Target table ID.
            cluster_columns: Desired cluster columns.

        Returns:
            bool: True if reclustering operation completed successfully.
        """
        validated_cols = self.validate_cluster_columns(cluster_columns)
        client = self._get_client()
        full_table_id = f"{self.settings.gcp_project_id}.{dataset_id}.{table_id}"
        cluster_str = ", ".join(validated_cols)

        sql = f"""
            CREATE OR REPLACE TABLE `{full_table_id}`
            CLUSTER BY {cluster_str}
            AS SELECT * FROM `{full_table_id}`
        """
        try:
            logger.info(f"Reclustering BigQuery table {full_table_id} by ({cluster_str})...")
            query_job = client.query(sql)
            query_job.result()
            logger.info(f"Successfully reclustered table {full_table_id}.")
            return True
        except Exception as e:
            logger.error(f"Failed to recluster table {full_table_id}: {e}")
            return False
