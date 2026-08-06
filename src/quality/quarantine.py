"""Quarantine Data Router Engine for non-compliant records."""

from datetime import datetime, timezone
from typing import List, Tuple
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.common.logging.logger import get_logger
from src.quality.rules.base_rule import BaseRule

logger = get_logger(__name__)


class QuarantineRouter:
    """Routes non-compliant records to Quarantine without halting primary pipeline execution."""

    @staticmethod
    def route_invalid_records(
        df: DataFrame, rules: List[BaseRule], execution_id: str
    ) -> Tuple[DataFrame, DataFrame]:
        """Evaluate DataFrame against rules and split into valid vs quarantine records.

        Args:
            df: Input PySpark DataFrame.
            rules: List of active quality rules.
            execution_id: Current pipeline execution ID.

        Returns:
            Tuple[DataFrame, DataFrame]: (valid_df, quarantine_df)
        """
        if df.count() == 0 or not rules:
            empty_quarantine = df.withColumn("_failed_rule", F.lit("")) \
                                 .withColumn("_error_code", F.lit("")) \
                                 .withColumn("_quarantined_at_utc", F.lit("")) \
                                 .filter(F.lit(False))
            return df, empty_quarantine

        # Add tracking column to flag failure conditions
        quarantine_df = df
        has_error_cond = F.lit(False)

        for rule in rules:
            if hasattr(rule, "min_val") and rule.min_val is not None:
                fail_cond = F.col(rule.column).isNull() | (F.col(rule.column) < rule.min_val)
            elif hasattr(rule, "allowed_values") and rule.allowed_values:
                fail_cond = F.col(rule.column).isNull() | (~F.col(rule.column).isin(rule.allowed_values))
            else:
                fail_cond = F.col(rule.column).isNull()

            has_error_cond = has_error_cond | fail_cond

        valid_df = df.filter(~has_error_cond)
        quarantine_df = (
            df.filter(has_error_cond)
            .withColumn("_failed_rule", F.lit("QualityRuleViolation"))
            .withColumn("_error_code", F.lit("ERR_QUALITY_QUARANTINE"))
            .withColumn("_quarantined_at_utc", F.lit(datetime.now(timezone.utc).isoformat()))
            .withColumn("_execution_id", F.lit(execution_id))
        )

        valid_count = valid_df.count()
        quarantine_count = quarantine_df.count()

        logger.info(
            f"Quarantine Routing Completed | Valid Records: {valid_count} | "
            f"Quarantined Records: {quarantine_count}"
        )

        return valid_df, quarantine_df
