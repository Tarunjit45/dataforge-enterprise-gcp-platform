"""Silver Parquet Writer and ETL Metrics Collector."""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pyspark.sql import DataFrame

from src.common.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ETLMetrics:
    """Model capturing detailed PySpark job execution metrics."""

    execution_id: str
    source_name: str
    entity_name: str
    records_read: int
    records_written: int
    invalid_records: int
    duplicate_records: int
    partition_count: int
    processing_duration_seconds: float
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SilverWriter:
    """Writes transformed PySpark DataFrames to Silver storage and records telemetry metrics."""

    @staticmethod
    def write_silver_dataset(
        df: DataFrame,
        output_path: str,
        partition_cols: Optional[List[str]] = None,
        mode: str = "overwrite",
    ) -> int:
        """Write DataFrame to Parquet with Snappy compression and partitioning.

        Args:
            df: Transformed PySpark DataFrame.
            output_path: Target output URI or local path.
            partition_cols: List of partition column names (e.g. ['pickup_month']).
            mode: Save mode ('overwrite', 'append').

        Returns:
            int: Number of records written.
        """
        record_count = df.count()
        logger.info(f"Writing {record_count} records to Silver Parquet target: {output_path}")

        writer = df.write.mode(mode).option("compression", "snappy")

        if partition_cols:
            writer = writer.partitionBy(*partition_cols)

        writer.parquet(output_path)
        logger.info(f"Successfully wrote Silver dataset to {output_path}")
        return record_count
