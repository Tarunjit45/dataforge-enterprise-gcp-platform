"""Generic PySpark cleaning and deduplication transformations."""

from typing import List
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from src.common.logging.logger import get_logger

logger = get_logger(__name__)


def filter_null_keys(df: DataFrame, required_key_cols: List[str]) -> DataFrame:
    """Filter out rows where mandatory business keys are NULL.

    Args:
        df: Input PySpark DataFrame.
        required_key_cols: List of column names that must not be NULL.

    Returns:
        DataFrame: Filtered DataFrame.
    """
    filtered_df = df
    for col in required_key_cols:
        filtered_df = filtered_df.filter(F.col(col).isNotNull())
    return filtered_df


def deduplicate_records(
    df: DataFrame, primary_keys: List[str], order_by_col: str
) -> DataFrame:
    """Deduplicate records based on primary key group, retaining the latest record.

    Args:
        df: Input PySpark DataFrame.
        primary_keys: Primary key columns identifying duplicate groups.
        order_by_col: Timestamp/sequence column to order records DESC.

    Returns:
        DataFrame: Deduplicated DataFrame.
    """
    window_spec = Window.partitionBy(*primary_keys).orderBy(F.col(order_by_col).desc())
    dedup_df = (
        df.withColumn("_row_num", F.row_number().over(window_spec))
        .filter(F.col("_row_num") == 1)
        .drop("_row_num")
    )
    return dedup_df


def normalize_timestamps(df: DataFrame, timestamp_cols: List[str]) -> DataFrame:
    """Ensure timestamp columns are converted to standard TimestampType in UTC.

    Args:
        df: Input PySpark DataFrame.
        timestamp_cols: List of timestamp column names.

    Returns:
        DataFrame: DataFrame with normalized timestamp columns.
    """
    norm_df = df
    for col in timestamp_cols:
        norm_df = norm_df.withColumn(col, F.to_timestamp(F.col(col)))
    return norm_df
