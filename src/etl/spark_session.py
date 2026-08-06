"""Centralized SparkSession factory supporting local and Dataproc execution."""

import os
from pyspark.sql import SparkSession
from src.common.config.settings import get_settings
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


def get_spark_session(app_name: str = "Enterprise-GCP-Data-Platform") -> SparkSession:
    """Build and return a configured SparkSession instance.

    Detects execution environment (local vs Dataproc cloud cluster) and applies
    optimized Spark configurations.

    Args:
        app_name: Name of the Spark application.

    Returns:
        SparkSession: Configured active SparkSession instance.
    """
    settings = get_settings()
    env = os.getenv("ENVIRONMENT", settings.environment).lower()

    builder = SparkSession.builder.appName(f"{app_name}-{env}")

    if env in ("dev", "test"):
        logger.info(f"Initializing SparkSession in Local Mode for environment '{env}'")
        builder = (
            builder.master("local[*]")
            .config("spark.sql.shuffle.partitions", "4")
            .config("spark.driver.memory", "2g")
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        )
    else:
        logger.info(f"Initializing SparkSession in Dataproc Managed Mode for environment '{env}'")
        builder = (
            builder.config("spark.sql.shuffle.partitions", "200")
            .config("spark.sql.parquet.compression.codec", "snappy")
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        )

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark
