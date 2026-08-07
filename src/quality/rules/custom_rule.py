"""Custom SQL/Column Expression Rule implementation."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.quality.models.quality_result import RuleResult
from src.quality.rules.base_rule import BaseRule


class CustomExpressionRule(BaseRule):
    """Rule asserting records pass a custom PySpark SQL boolean expression string."""

    def __init__(self, name: str, expression: str, column: str = "*"):
        super().__init__(
            name=name,
            column=column,
            error_code="ERR_CUSTOM_RULE_VIOLATION",
        )
        self.expression = expression

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

        failed_count = df.filter(f"NOT ({self.expression})").count()
        passed = failed_count == 0

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            passed=passed,
            total_records=total,
            failed_records=failed_count,
            error_code=self.error_code,
            error_message=(
                f"Custom expression '{self.expression}' failed for {failed_count} records."
                if not passed
                else "Passed"
            ),
        )
