"""DataType Rule implementation."""

from pyspark.sql import DataFrame

from src.quality.models.quality_result import RuleResult
from src.quality.rules.base_rule import BaseRule


class DataTypeRule(BaseRule):
    """Rule asserting column data type matches expected target type."""

    def __init__(self, column: str, expected_type: str):
        super().__init__(
            name=f"DataTypeCheck({column}: {expected_type})",
            column=column,
            error_code="ERR_DATATYPE_MISMATCH",
        )
        self.expected_type = expected_type.lower()

    def evaluate(self, df: DataFrame) -> RuleResult:
        total = df.count()
        actual_type = dict(df.dtypes).get(self.column, "").lower()

        passed = actual_type == self.expected_type
        failed_count = 0 if passed else total

        return RuleResult(
            rule_name=self.name,
            column=self.column,
            passed=passed,
            total_records=total,
            failed_records=failed_count,
            error_code=self.error_code,
            error_message=(
                f"Column '{self.column}' type is '{actual_type}', expected '{self.expected_type}'."
                if not passed
                else "Passed"
            ),
        )
