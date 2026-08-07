"""Range Rule implementation."""

from typing import Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.quality.models.quality_result import RuleResult
from src.quality.rules.base_rule import BaseRule


class RangeRule(BaseRule):
    """Rule asserting that column values fall within [min_val, max_val]."""

    def __init__(
        self, column: str, min_val: Optional[float] = None, max_val: Optional[float] = None
    ):
        super().__init__(
            name=f"RangeCheck({column}: min={min_val}, max={max_val})",
            column=column,
            error_code="ERR_RANGE_INVALID",
        )
        self.min_val = min_val
        self.max_val = max_val

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

        condition = F.lit(True)
        if self.min_val is not None:
            condition = condition & (F.col(self.column) >= self.min_val)
        if self.max_val is not None:
            condition = condition & (F.col(self.column) <= self.max_val)

        failed_count = df.filter(~condition).count()
        passed = failed_count == 0

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            passed=passed,
            total_records=total,
            failed_records=failed_count,
            error_code=self.error_code,
            error_message=(
                f"Column '{self.column}' has {failed_count} values outside range [{self.min_val}, {self.max_val}]."
                if not passed
                else "Passed"
            ),
        )
