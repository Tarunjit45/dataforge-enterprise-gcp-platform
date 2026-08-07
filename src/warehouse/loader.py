"""Enterprise BigQuery Gold Warehouse Orchestration Engine."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

from src.common.config.settings import get_settings
from src.common.exceptions.base import ConfigurationError, PipelineError, QualityCheckError
from src.common.logging.logger import get_logger
from src.warehouse.clustering import ClusteringManager
from src.warehouse.models.metadata import WarehouseLoadMetadata
from src.warehouse.models.star_schema import get_star_schema_definition
from src.warehouse.partition_manager import PartitionManager

logger = get_logger(__name__)


class GoldWarehouseLoader:
    """Enterprise Gold Warehouse Orchestration Engine for Star Schema ETL and Analytics."""

    DEFAULT_DQ_SCORE_THRESHOLD = 70.0  # Grade C threshold from Phase 7

    def __init__(self, bq_client: Any = None):
        self.settings = get_settings()
        self.bq_client = bq_client
        self.partition_manager = PartitionManager(bq_client=bq_client)
        self.clustering_manager = ClusteringManager(bq_client=bq_client)
        self.schema_definition = get_star_schema_definition()

    def _get_client(self) -> Any:
        """Lazy-initialize BigQuery client."""
        if self.bq_client is None:
            if bigquery is None:
                raise PipelineError(
                    "google-cloud-bigquery library is not installed and no bq_client injected."
                )
            self.bq_client = bigquery.Client(project=self.settings.gcp_project_id)
        return self.bq_client

    def _load_sql_script(self, script_name: str) -> str:
        """Load SQL script template from src/warehouse/sql/."""
        sql_dir = Path(__file__).resolve().parent / "sql"
        script_path = sql_dir / script_name
        if not script_path.exists():
            raise PipelineError(f"Warehouse SQL script not found: {script_path}")
        with open(script_path, "r", encoding="utf-8") as f:
            return f.read()

    def initialize_warehouse_schema(
        self,
        dataset_id: str = "gold_analytics",
        staged_dataset_id: str = "silver_staged",
    ) -> bool:
        """Create BigQuery Gold dataset, dimension DDLs, and fact table DDLs.

        Args:
            dataset_id: BigQuery Gold dataset ID.
            staged_dataset_id: Staged Silver dataset ID.

        Returns:
            bool: True if initialization completed without errors.
        """
        client = self._get_client()

        # Create dataset if not exists
        full_dataset_id = f"{self.settings.gcp_project_id}.{dataset_id}"
        dataset = bigquery.Dataset(full_dataset_id)
        dataset.location = self.settings.region
        dataset.labels = {"layer": "gold", "env": self.settings.environment}
        try:
            client.create_dataset(dataset, exists_ok=True)
            logger.info(
                f"Initialized Gold dataset '{full_dataset_id}' in region '{self.settings.region}'."
            )
        except Exception as e:
            logger.warning(f"Dataset creation check for '{full_dataset_id}': {e}")

        # Execute DDL scripts
        for ddl_script in ["create_dimensions.sql", "create_fact_tables.sql"]:
            raw_sql = self._load_sql_script(ddl_script)
            formatted_sql = raw_sql.format(
                project_id=self.settings.gcp_project_id,
                dataset_id=dataset_id,
                staged_dataset=staged_dataset_id,
            )
            query_job = client.query(formatted_sql)
            query_job.result()
            logger.info(f"Executed warehouse DDL script '{ddl_script}' against '{dataset_id}'.")

        return True

    def load_dimensions(self, dataset_id: str = "gold_analytics") -> int:
        """Seed and update dimension tables with SCD Type 1 & 2 logic.

        Args:
            dataset_id: Target BigQuery dataset ID.

        Returns:
            int: Total DML affected rows across dimension updates.
        """
        client = self._get_client()
        raw_sql = self._load_sql_script("load_dimensions.sql")
        formatted_sql = raw_sql.format(
            project_id=self.settings.gcp_project_id,
            dataset_id=dataset_id,
        )
        logger.info(f"Executing dimension load & SCD update script on dataset '{dataset_id}'...")
        query_job = client.query(formatted_sql)
        query_job.result()
        affected = query_job.num_dml_affected_rows or 0
        logger.info(
            f"Successfully updated dimension tables in '{dataset_id}'. Affected rows: {affected}"
        )
        return affected

    def load_incremental_fact(
        self,
        batch_id: str,
        source_execution_id: str,
        source_manifest: str,
        data_quality_score: float,
        dataset_id: str = "gold_analytics",
        staged_dataset_id: str = "silver_staged",
        min_dq_threshold: float = DEFAULT_DQ_SCORE_THRESHOLD,
    ) -> WarehouseLoadMetadata:
        """Merge validated Silver dataset records into Gold FACT_TAXI_TRIPS idempotently.

        Args:
            batch_id: ETL Batch ID.
            source_execution_id: Phase 7 execution ID.
            source_manifest: GCS manifest URI.
            data_quality_score: Calculated Data Quality score from Phase 7.
            dataset_id: Target Gold dataset ID.
            staged_dataset_id: Source Silver staged dataset ID.
            min_dq_threshold: Minimum allowable DQ score percentage.

        Returns:
            WarehouseLoadMetadata: Load metadata execution report.

        Raises:
            DataValidationError: If data quality score is below threshold.
        """
        logger.info(
            f"Evaluating Data Quality score for Gold ingestion: {data_quality_score:.2f}% (Threshold: {min_dq_threshold:.2f}%)"
        )
        if data_quality_score < min_dq_threshold:
            errMsg = (
                f"Data Quality score {data_quality_score:.2f}% is below Gold Warehouse threshold {min_dq_threshold:.2f}%. "
                f"Batch '{batch_id}' quarantined from Gold layer."
            )
            logger.error(errMsg)
            raise QualityCheckError(errMsg)

        client = self._get_client()
        raw_sql = self._load_sql_script("incremental_merge.sql")
        formatted_sql = raw_sql.format(
            project_id=self.settings.gcp_project_id,
            dataset_id=dataset_id,
            staged_dataset=staged_dataset_id,
            batch_id=batch_id,
            source_execution_id=source_execution_id,
            source_manifest=source_manifest,
            data_quality_score=data_quality_score,
        )

        logger.info(f"Submitting incremental MERGE query for batch '{batch_id}'...")
        query_job = client.query(formatted_sql)
        query_job.result()
        affected_rows = query_job.num_dml_affected_rows or 0

        metadata = WarehouseLoadMetadata(
            batch_id=batch_id,
            source_execution_id=source_execution_id,
            source_manifest=source_manifest,
            data_quality_score=data_quality_score,
            records_read=affected_rows,
            records_inserted=affected_rows,
            records_updated=0,
            dataset_id=dataset_id,
            table_id="FACT_TAXI_TRIPS",
        )
        logger.info(
            f"Gold Warehouse load completed successfully for batch '{batch_id}'. Inserted/Merged rows: {affected_rows}"
        )
        return metadata

    def deploy_analytics_layer(self, dataset_id: str = "gold_analytics") -> bool:
        """Deploy analytical views and data marts on BigQuery Gold dataset.

        Args:
            dataset_id: Target BigQuery dataset ID.

        Returns:
            bool: True if deployment completed successfully.
        """
        client = self._get_client()
        for view_script in ["views.sql", "data_marts.sql"]:
            raw_sql = self._load_sql_script(view_script)
            formatted_sql = raw_sql.format(
                project_id=self.settings.gcp_project_id,
                dataset_id=dataset_id,
            )
            logger.info(
                f"Deploying analytical script '{view_script}' against dataset '{dataset_id}'..."
            )
            query_job = client.query(formatted_sql)
            query_job.result()
        logger.info("Successfully deployed analytics layer views and data marts.")
        return True
