"""Enterprise BigQuery Data Warehouse Loader Engine."""

from pathlib import Path
from typing import Any, List, Optional

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None  # Handled gracefully if client is injected or mock

from src.bigquery.schema_loader import load_bq_schema_from_json
from src.common.config.settings import get_settings
from src.common.exceptions.base import CloudStorageError, PipelineError
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


class BigQueryLoader:
    """Enterprise BigQuery Loader executing Parquet loads and idempotent MERGE queries."""

    def __init__(self, bq_client: Any = None):
        self.settings = get_settings()
        self.bq_client = bq_client

    def _get_client(self) -> Any:
        """Lazy-initialize BigQuery client."""
        if self.bq_client is None:
            if bigquery is None:
                raise PipelineError(
                    "google-cloud-bigquery library is not installed and no bq_client was injected."
                )
            self.bq_client = bigquery.Client(project=self.settings.gcp_project_id)
        return self.bq_client

    def load_parquet_from_gcs(
        self,
        gcs_uri: str,
        dataset_id: str,
        table_id: str,
        write_disposition: str = "WRITE_TRUNCATE",
    ) -> int:
        """Load Parquet files staged on GCS into target BigQuery table.

        Args:
            gcs_uri: Source Parquet GCS URI (e.g. 'gs://bucket/path/*.parquet').
            dataset_id: Target dataset name.
            table_id: Target table name.
            write_disposition: Write mode ('WRITE_TRUNCATE', 'WRITE_APPEND').

        Returns:
            int: Total loaded record count.
        """
        client = self._get_client()
        full_table_id = f"{self.settings.gcp_project_id}.{dataset_id}.{table_id}"

        if bigquery is not None:
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.PARQUET,
                write_disposition=write_disposition,
            )
        else:
            job_config = None

        logger.info(
            f"Submitting BigQuery Load Job: {gcs_uri} -> {full_table_id} [{write_disposition}]"
        )
        load_job = client.load_table_from_uri(gcs_uri, full_table_id, job_config=job_config)
        load_job.result()  # Wait for job completion

        destination_table = client.get_table(full_table_id)
        loaded_rows = destination_table.num_rows
        logger.info(
            f"BigQuery Load Job completed. Total table rows in {full_table_id}: {loaded_rows}"
        )
        return loaded_rows

    def execute_merge_upsert(self, sql_file_name: str, dataset_id: str) -> int:
        """Execute an idempotent MERGE SQL upsert statement.

        Args:
            sql_file_name: Name of SQL file in src/bigquery/sql/ (e.g. 'merge_fact_trips.sql').
            dataset_id: Target dataset name.

        Returns:
            int: Number of affected rows.
        """
        client = self._get_client()
        root_dir = Path(__file__).resolve().parents[2]
        sql_path = root_dir / "src" / "bigquery" / "sql" / sql_file_name

        if not sql_path.exists():
            raise PipelineError(f"BigQuery MERGE SQL script missing: {sql_path}")

        with open(sql_path, "r", encoding="utf-8") as f:
            sql_template = f.read()

        formatted_sql = sql_template.format(
            project_id=self.settings.gcp_project_id,
            dataset_id=dataset_id,
        )

        logger.info(
            f"Executing BigQuery MERGE Query from '{sql_file_name}' against dataset '{dataset_id}'..."
        )
        query_job = client.query(formatted_sql)
        query_job.result()  # Wait for query execution

        num_affected = query_job.num_dml_affected_rows or 0
        logger.info(
            f"BigQuery MERGE Query completed successfully. Affected DML rows: {num_affected}"
        )
        return num_affected
