"""Schema drift detection engine."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from typing import Any, Dict, List
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType

from src.common.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SchemaDriftReport:
    """Model capturing schema drift analysis findings."""

    dataset_name: str
    has_drift: bool
    missing_columns: List[str] = field(default_factory=list)
    new_columns: List[str] = field(default_factory=list)
    type_changes: List[str] = field(default_factory=list)
    order_changed: bool = False
    generated_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SchemaDriftDetector:
    """Engine for detecting schema changes against historical baseline contracts."""

    @staticmethod
    def detect_drift(df: DataFrame, baseline_schema: StructType, dataset_name: str = "dataset") -> SchemaDriftReport:
        """Compare PySpark DataFrame schema against baseline contract.

        Args:
            df: Input PySpark DataFrame.
            baseline_schema: Historical baseline StructType schema.
            dataset_name: Name of target dataset.

        Returns:
            SchemaDriftReport: Structural drift analysis.
        """
        actual_fields = {f.name: f.dataType.simpleString() for f in df.schema.fields}
        baseline_fields = {f.name: f.dataType.simpleString() for f in baseline_schema.fields}

        missing = [c for c in baseline_fields if c not in actual_fields]
        new_cols = [c for c in actual_fields if c not in baseline_fields]

        type_changes = []
        for col, base_type in baseline_fields.items():
            if col in actual_fields:
                act_type = actual_fields[col]
                if act_type != base_type:
                    type_changes.append(f"{col}: baseline '{base_type}' -> actual '{act_type}'")

        actual_order = list(actual_fields.keys())
        baseline_order = list(baseline_fields.keys())
        order_changed = actual_order != baseline_order and not (missing or new_cols)

        has_drift = len(missing) > 0 or len(new_cols) > 0 or len(type_changes) > 0 or order_changed

        if has_drift:
            logger.warning(
                f"Schema Drift Detected for '{dataset_name}' | Missing: {missing} | "
                f"New: {new_cols} | Type Changes: {type_changes}"
            )

        return SchemaDriftReport(
            dataset_name=dataset_name,
            has_drift=has_drift,
            missing_columns=missing,
            new_columns=new_cols,
            type_changes=type_changes,
            order_changed=order_changed,
        )
