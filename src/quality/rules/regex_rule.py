"""Regex Pattern Matching Rule implementation."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.quality.models.quality_result import RuleResult
from src.quality.rules.base_rule import BaseRule


class RegexRule(BaseRule):
    """Rule asserting string column values match a regex pattern."""

    def __init__(self, column: str, pattern: str):
        super().__init__(
            name=f"RegexCheck({column})",
            column=column,
            error_code="ERR_REGEX_MISMATCH",
        )
        self.pattern = pattern

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

        failed_count = df.filter(~F.col(self.column).rlike(self.pattern)).count()
        passed = failed_count == 0

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            passed=passed,
            total_records=total,
            failed_records=failed_count,
            error_code=self.error_code,
            error_message=f"Column '{self.column}' has {failed_count} values failing regex pattern '{self.pattern}'."
            if not passed
            else "Passed",
        )
