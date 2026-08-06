"""NYC Taxi specific PySpark business transformations."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def transform_nyc_taxi_silver(df: DataFrame) -> DataFrame:
    """Enrich raw NYC Taxi DataFrame with derived business attributes.

    Calculates:
    - pickup_hour, pickup_day, pickup_month
    - trip_duration (minutes)
    - tip_percentage
    - average_speed (mph)
    - weekend_flag
    - peak_hour_flag

    Args:
        df: Input PySpark DataFrame (Bronze stage).

    Returns:
        DataFrame: Enriched PySpark DataFrame (Silver stage).
    """
    pickup_col = "tpep_pickup_datetime"
    dropoff_col = "tpep_dropoff_datetime"

    # Filter out invalid trip durations and negative distances/amounts
    valid_df = df.filter(
        (F.col(dropoff_col) > F.col(pickup_col))
        & (F.col("trip_distance") > 0)
        & (F.col("total_amount") >= 0)
    )

    enriched_df = (
        valid_df.withColumn("pickup_hour", F.hour(F.col(pickup_col)))
        .withColumn("pickup_day", F.dayofmonth(F.col(pickup_col)))
        .withColumn("pickup_month", F.month(F.col(pickup_col)))
        .withColumn(
            "trip_duration_minutes",
            F.round(
                (F.col(dropoff_col).cast("long") - F.col(pickup_col).cast("long")) / 60.0,
                2,
            ),
        )
        .withColumn(
            "tip_percentage",
            F.when(
                F.col("total_amount") > 0,
                F.round((F.col("tip_amount") / F.col("total_amount")) * 100.0, 2),
            ).otherwise(0.0),
        )
        .withColumn(
            "average_speed_mph",
            F.when(
                F.col("trip_duration_minutes") > 0,
                F.round(
                    F.col("trip_distance") / (F.col("trip_duration_minutes") / 60.0),
                    2,
                ),
            ).otherwise(0.0),
        )
        .withColumn(
            "weekend_flag",
            F.when(F.dayofweek(F.col(pickup_col)).isin(1, 7), True).otherwise(False),
        )
        .withColumn(
            "peak_hour_flag",
            F.when(
                (~F.dayofweek(F.col(pickup_col)).isin(1, 7))
                & (F.hour(F.col(pickup_col)).between(16, 19)),
                True,
            ).otherwise(False),
        )
    )

    return enriched_df
