"""Referential Integrity Rule implementation."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.quality.models.quality_result import RuleResult
from src.quality.rules.base_rule import BaseRule


class ReferentialIntegrityRule(BaseRule):
    """Rule asserting foreign key values exist in a reference DataFrame."""

    def __init__(self, column: str, reference_df: DataFrame, reference_column: str):
        super().__init__(
            name=f"ReferentialIntegrityCheck({column} -> {reference_column})",
            column=column,
            error_code="ERR_FOREIGN_KEY_VIOLATION",
        )
        self.ref_df = reference_df
        self.ref_col = reference_column

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

        unmatched_df = df.join(
            self.ref_df,
            df[self.column] == self.ref_df[self.ref_col],
            "left_anti",
        )
        failed_count = unmatched_df.count()
        passed = failed_count == 0

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            passed=passed,
            total_records=total,
            failed_records=failed_count,
            error_code=self.error_code,
            error_message=(
                f"Found {failed_count} orphaned foreign key records in column '{self.column}'."
                if not passed
                else "Passed"
            ),
        )
