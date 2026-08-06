"""Unique / Duplicate Rule implementation."""

from typing import List
from pyspark.sql import DataFrame

from src.quality.models.quality_result import RuleResult
from src.quality.rules.base_rule import BaseRule


class UniqueRule(BaseRule):
    """Rule asserting uniqueness over a column or set of primary key columns."""

    def __init__(self, column: str, additional_keys: List[str] = None):
        super().__init__(
            name=f"UniqueCheck({column})",
            column=column,
            error_code="ERR_DUPLICATE_KEY",
        )
        self.keys = [column] + (additional_keys or [])

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

        distinct_count = df.select(*self.keys).distinct().count()
        failed_count = total - distinct_count
        passed = failed_count == 0

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            passed=passed,
            total_records=total,
            failed_records=failed_count,
            error_code=self.error_code,
            error_message=f"Duplicate records found: {failed_count} duplicates."
            if not passed
            else "Passed",
        )
