"""Not Null Rule implementation."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.quality.models.quality_result import RuleResult
from src.quality.rules.base_rule import BaseRule


class NotNullRule(BaseRule):
    """Rule asserting that a column contains no NULL values."""

    def __init__(self, column: str):
        super().__init__(
            name=f"NotNullCheck({column})",
            column=column,
            error_code="ERR_NULL_KEY",
        )

    def evaluate(self, df: DataFrame) -> RuleResult:
        total = df.count()
        if total == 0:
            return RuleResult(
                rule_name=self.name,
                column=self.column,
                passed=True,
                total_records=0,
                failed_records=0,
                error_code=self.error_code,
                error_message="Empty DataFrame",
            )

        failed_df = df.filter(F.col(self.column).isNull())
        failed_count = failed_df.count()
        passed = failed_count == 0

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            passed=passed,
            total_records=total,
            failed_records=failed_count,
            error_code=self.error_code,
            error_message=(
                f"Column '{self.column}' contains {failed_count} null records."
                if not passed
                else "Passed"
            ),
        )
