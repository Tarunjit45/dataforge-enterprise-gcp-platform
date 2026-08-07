"""Unit tests for PySpark ETL transformations and job pipeline."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

pyspark = pytest.importorskip("pyspark")
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from src.etl.jobs.clean_bronze_to_silver import run_bronze_to_silver_job
from src.etl.quality.schema_validator import SchemaValidator
from src.etl.spark_session import get_spark_session
from src.etl.transformations.cleaning import (
    deduplicate_records,
    filter_null_keys,
    normalize_timestamps,
)
from src.etl.transformations.nyc_taxi import transform_nyc_taxi_silver


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """Fixture providing a local SparkSession."""
    try:
        return get_spark_session("UT-SparkSession")
    except Exception as e:
        pytest.skip(f"PySpark Java Gateway unavailable: {e}")


@pytest.mark.unit
def test_spark_session_initialization(spark: SparkSession):
    """Verify local SparkSession factory creation."""
    assert spark is not None
    assert len(spark.version) > 0


@pytest.mark.unit
def test_filter_null_keys(spark: SparkSession):
    """Test filtering null primary key rows."""
    data = [("1", "2024-01-01 10:00:00"), (None, "2024-01-01 11:00:00")]
    schema = ["id", "timestamp"]
    df = spark.createDataFrame(data, schema)

    filtered_df = filter_null_keys(df, ["id"])
    assert filtered_df.count() == 1


@pytest.mark.unit
def test_deduplicate_records(spark: SparkSession):
    """Test record deduplication logic."""
    data = [
        (1, "2024-01-01 10:00:00", "v1"),
        (1, "2024-01-01 10:00:00", "v2"),
    ]
    schema = ["VendorID", "tpep_pickup_datetime", "val"]
    df = spark.createDataFrame(data, schema)

    dedup_df = deduplicate_records(df, ["VendorID", "tpep_pickup_datetime"], "tpep_pickup_datetime")
    assert dedup_df.count() == 1


@pytest.mark.unit
def test_schema_validator(spark: SparkSession):
    """Test schema validation engine against target StructType."""
    expected_schema = StructType(
        [
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
        ]
    )
    df = spark.createDataFrame([(1, "test")], expected_schema)

    result = SchemaValidator.validate_schema(df, expected_schema)
    assert result.is_valid is True
    assert len(result.missing_columns) == 0


@pytest.mark.unit
def test_nyc_taxi_business_transformations(spark: SparkSession):
    """Test NYC Taxi derived attribute transformations."""
    schema = StructType(
        [
            StructField("VendorID", IntegerType(), True),
            StructField("tpep_pickup_datetime", TimestampType(), True),
            StructField("tpep_dropoff_datetime", TimestampType(), True),
            StructField("trip_distance", DoubleType(), True),
            StructField("tip_amount", DoubleType(), True),
            StructField("total_amount", DoubleType(), True),
        ]
    )

    data = [
        (
            1,
            datetime(2024, 1, 15, 17, 0, 0),  # Monday 5 PM (Peak hour)
            datetime(2024, 1, 15, 17, 30, 0),  # 30 min duration
            10.0,  # 10 miles -> 20 mph speed
            4.0,  # Tip $4
            20.0,  # Total $20 -> 20% tip
        )
    ]

    df = spark.createDataFrame(data, schema)
    transformed_df = transform_nyc_taxi_silver(df)

    row = transformed_df.first()
    assert row["pickup_hour"] == 17
    assert row["trip_duration_minutes"] == 30.0
    assert row["tip_percentage"] == 20.0
    assert row["average_speed_mph"] == 20.0
    assert row["weekend_flag"] is False
    assert row["peak_hour_flag"] is True


@pytest.mark.unit
def test_full_bronze_to_silver_pipeline(spark: SparkSession, tmp_path: Path):
    """Test end-to-end Bronze to Silver PySpark job execution using local Parquet fixture."""
    schema = StructType(
        [
            StructField("VendorID", IntegerType(), True),
            StructField("tpep_pickup_datetime", TimestampType(), True),
            StructField("tpep_dropoff_datetime", TimestampType(), True),
            StructField("trip_distance", DoubleType(), True),
            StructField("tip_amount", DoubleType(), True),
            StructField("total_amount", DoubleType(), True),
        ]
    )

    data = [
        (
            1,
            datetime(2024, 1, 1, 10, 0, 0),
            datetime(2024, 1, 1, 10, 15, 0),
            5.0,
            2.0,
            10.0,
        )
    ]

    raw_parquet_dir = tmp_path / "raw_parquet"
    raw_parquet_dir.mkdir()
    raw_parquet_file = raw_parquet_dir / "sample.parquet"

    raw_df = spark.createDataFrame(data, schema)
    raw_df.write.parquet(str(raw_parquet_file))

    manifest_file = tmp_path / "manifest.json"
    manifest_data = {
        "execution_id": "test-exec-999",
        "source": "nyc_tlc",
        "entity": "yellow_taxi",
        "gcs_payload_uri": str(raw_parquet_file),
    }
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    silver_out_dir = tmp_path / "silver_output"
    metrics = run_bronze_to_silver_job(manifest_file, output_silver_path=str(silver_out_dir))

    assert metrics.records_read == 1
    assert metrics.records_written == 1
    assert metrics.invalid_records == 0
    assert metrics.duplicate_records == 0
    assert silver_out_dir.exists()
