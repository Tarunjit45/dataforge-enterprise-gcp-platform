"""Schema validation and drift detection engine for PySpark Dataframes."""

from dataclasses import dataclass, field
from typing import List
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType

from src.common.exceptions.base import ValidationError
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SchemaValidationResult:
    """Model capturing schema comparison findings."""

    is_valid: bool
    missing_columns: List[str] = field(default_factory=list)
    unexpected_columns: List[str] = field(default_factory=list)
    type_mismatches: List[str] = field(default_factory=list)


class SchemaValidator:
    """Engine for enforcing expected schemas and detecting schema drift."""

    @staticmethod
    def validate_schema(df: DataFrame, expected_schema: StructType) -> SchemaValidationResult:
        """Compare PySpark DataFrame schema against expected StructType target.

        Args:
            df: Input PySpark DataFrame.
            expected_schema: Target StructType contract.

        Returns:
            SchemaValidationResult: Detailed validation outcome.
        """
        actual_fields = {field.name: field.dataType.simpleString() for field in df.schema.fields}
        expected_fields = {field.name: field.dataType.simpleString() for field in expected_schema.fields}

        missing = [col for col in expected_fields if col not in actual_fields]
        unexpected = [col for col in actual_fields if col not in expected_fields]

        type_mismatches = []
        for col, expected_type in expected_fields.items():
            if col in actual_fields:
                actual_type = actual_fields[col]
                if actual_type != expected_type:
                    type_mismatches.append(f"{col}: expected {expected_type}, got {actual_type}")

        is_valid = len(missing) == 0 and len(type_mismatches) == 0

        if not is_valid:
            logger.warning(
                f"Schema Validation Issues Detected | Missing: {missing} | "
                f"Unexpected: {unexpected} | Mismatches: {type_mismatches}"
            )
        else:
            logger.info("Schema Validation Passed Successfully.")

        return SchemaValidationResult(
            is_valid=is_valid,
            missing_columns=missing,
            unexpected_columns=unexpected,
            type_mismatches=type_mismatches,
        )
