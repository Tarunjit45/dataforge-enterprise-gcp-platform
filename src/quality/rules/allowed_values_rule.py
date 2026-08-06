"""Allowed Values Rule implementation."""

from typing import List
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.quality.models.quality_result import RuleResult
from src.quality.rules.base_rule import BaseRule


class AllowedValuesRule(BaseRule):
    """Rule asserting column values belong to a set of allowed values."""

    def __init__(self, column: str, allowed_values: List[Any]):
        super().__init__(
            name=f"AllowedValuesCheck({column})",
            column=column,
            error_code="ERR_VALUE_NOT_ALLOWED",
        )
        self.allowed_values = allowed_values

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

        failed_count = df.filter(~F.col(self.column).isin(self.allowed_values)).count()
        passed = failed_count == 0

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            passed=passed,
            total_records=total,
            failed_records=failed_count,
            error_code=self.error_code,
            error_message=f"Column '{self.column}' has {failed_count} records not in allowed set {self.allowed_values}."
            if not passed
            else "Passed",
        )
