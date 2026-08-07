"""Main PySpark ETL Job: Transforms Bronze Raw Parquet into Silver Cleansed Parquet."""

import time
from pathlib import Path
from typing import Optional

from src.common.config.settings import get_settings
from src.common.logging.logger import get_logger, set_correlation_id
from src.etl.reader import BronzeReader
from src.etl.spark_session import get_spark_session
from src.etl.transformations.cleaning import (
    deduplicate_records,
    filter_null_keys,
    normalize_timestamps,
)
from src.etl.transformations.nyc_taxi import transform_nyc_taxi_silver
from src.etl.writer import ETLMetrics, SilverWriter

logger = get_logger(__name__)


def run_bronze_to_silver_job(
    manifest_path: Path,
    output_silver_path: Optional[str] = None,
) -> ETLMetrics:
    """Run Bronze to Silver PySpark ETL pipeline for a single manifest payload.

    Args:
        manifest_path: Local or GCS path to manifest.json file.
        output_silver_path: Optional override for Silver output location.

    Returns:
        ETLMetrics: Execution summary metrics model.
    """
    start_time = time.time()
    spark = get_spark_session("BronzeToSilverETL")
    settings = get_settings()

    reader = BronzeReader(spark)
    manifest = reader.read_manifest(manifest_path)
    execution_id = manifest.get("execution_id", "local-run")
    set_correlation_id(execution_id)

    payload_uri = manifest.get("gcs_payload_uri") or str(
        manifest_path.parent / manifest.get("payload_filename", "")
    )
    source_name = manifest.get("source", "nyc_tlc")
    entity_name = manifest.get("entity", "yellow_taxi")

    # Read Bronze Data
    bronze_df = reader.read_bronze_dataset(payload_uri)
    records_read = bronze_df.count()

    # Step 1: Cleaning & Deduplication
    required_keys = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]
    null_filtered_df = filter_null_keys(bronze_df, required_keys)
    records_after_null = null_filtered_df.count()
    invalid_records = records_read - records_after_null

    norm_df = normalize_timestamps(null_filtered_df, required_keys)
    dedup_df = deduplicate_records(
        norm_df,
        primary_keys=["tpep_pickup_datetime", "VendorID"],
        order_by_col="tpep_pickup_datetime",
    )
    records_after_dedup = dedup_df.count()
    duplicate_records = records_after_null - records_after_dedup

    # Step 2: Domain Business Transformations
    silver_df = transform_nyc_taxi_silver(dedup_df)

    # Step 3: Write Silver Parquet
    target_path = (
        output_silver_path
        or f"{settings.processed_bucket or 'gs://' + settings.gcp_project_id + '-processed-silver'}/{entity_name}"
    )

    records_written = SilverWriter.write_silver_dataset(
        silver_df, output_path=target_path, partition_cols=["pickup_month"]
    )

    duration = time.time() - start_time
    metrics = ETLMetrics(
        execution_id=execution_id,
        source_name=source_name,
        entity_name=entity_name,
        records_read=records_read,
        records_written=records_written,
        invalid_records=invalid_records,
        duplicate_records=duplicate_records,
        partition_count=silver_df.rdd.getNumPartitions(),
        processing_duration_seconds=round(duration, 2),
    )

    logger.info(
        f"Bronze-to-Silver ETL Job Completed | Read: {records_read} | "
        f"Written: {records_written} | Invalid: {invalid_records} | "
        f"Duplicates: {duplicate_records} | Duration: {metrics.processing_duration_seconds}s"
    )
    return metrics
