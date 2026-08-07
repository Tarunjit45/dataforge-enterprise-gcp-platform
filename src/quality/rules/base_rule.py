"""Abstract Base Class for Data Quality Rules."""

from abc import ABC, abstractmethod
from typing import Any

from pyspark.sql import DataFrame

from src.quality.models.quality_result import RuleResult


class BaseRule(ABC):
    """Abstract Base Class for all PySpark data quality rules."""

    def __init__(self, name: str, column: str, error_code: str = "ERR_GENERIC_DQ"):
        self.name = name
        self.column = column
        self.error_code = error_code

    @abstractmethod
    def evaluate(self, df: DataFrame) -> RuleResult:
        """Evaluate rule against PySpark DataFrame.

        Args:
            df: Input PySpark DataFrame.

        Returns:
            RuleResult: Detailed outcome of rule evaluation.
        """
        pass
