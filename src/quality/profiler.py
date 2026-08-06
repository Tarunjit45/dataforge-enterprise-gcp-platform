"""Statistical Data Profiling engine for PySpark DataFrames."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import NumericType

from src.common.logging.logger import get_logger
from src.quality.models.quality_result import ColumnProfile, ProfileResult

logger = get_logger(__name__)


class DataProfiler:
    """Profiler generating statistical summaries for PySpark DataFrames."""

    @staticmethod
    def profile_dataset(df: DataFrame, dataset_name: str = "dataset") -> ProfileResult:
        """Compute statistical profile metrics over input PySpark DataFrame.

        Args:
            df: Input PySpark DataFrame.
            dataset_name: Name identifier for dataset.

        Returns:
            ProfileResult: Detailed statistical profiling outcome.
        """
        total_rows = df.count()
        total_cols = len(df.columns)

        if total_rows == 0:
            return ProfileResult(
                dataset_name=dataset_name,
                total_rows=0,
                total_columns=total_cols,
                duplicate_rows=0,
                duplicate_percentage=0.0,
            )

        distinct_rows = df.distinct().count()
        duplicate_rows = total_rows - distinct_rows
        duplicate_pct = round((duplicate_rows / total_rows) * 100.0, 2)

        column_profiles = {}
        for field in df.schema.fields:
            col_name = field.name
            data_type = field.dataType.simpleString()

            null_count = df.filter(F.col(col_name).isNull()).count()
            null_pct = round((null_count / total_rows) * 100.0, 2)

            distinct_cnt = df.select(col_name).distinct().count()
            distinct_pct = round((distinct_cnt / total_rows) * 100.0, 2)

            min_val = None
            max_val = None
            mean_val = None

            if isinstance(field.dataType, NumericType):
                stats = df.select(
                    F.min(F.col(col_name)).alias("min"),
                    F.max(F.col(col_name)).alias("max"),
                    F.mean(F.col(col_name)).alias("mean"),
                ).first()
                if stats:
                    min_val = stats["min"]
                    max_val = stats["max"]
                    mean_val = round(stats["mean"], 2) if stats["mean"] is not None else None

            column_profiles[col_name] = ColumnProfile(
                column_name=col_name,
                data_type=data_type,
                total_count=total_rows,
                null_count=null_count,
                null_percentage=null_pct,
                distinct_count=distinct_cnt,
                distinct_percentage=distinct_pct,
                min_val=min_val,
                max_val=max_val,
                mean_val=mean_val,
            )

        logger.info(f"Completed statistical profiling for dataset '{dataset_name}' ({total_rows} rows, {total_cols} cols).")

        return ProfileResult(
            dataset_name=dataset_name,
            total_rows=total_rows,
            total_columns=total_cols,
            duplicate_rows=duplicate_rows,
            duplicate_percentage=duplicate_pct,
            column_profiles=column_profiles,
        )
