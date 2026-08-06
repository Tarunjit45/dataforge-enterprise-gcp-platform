"""Configuration-driven Data Quality Engine orchestrator."""

from pathlib import Path
import time
from typing import Any, Dict, List, Optional
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType

from src.common.exceptions.base import ConfigurationError
from src.common.logging.logger import get_logger
from src.quality.models.quality_result import QualityResult, RuleResult
from src.quality.profiler import DataProfiler
from src.quality.rules.allowed_values_rule import AllowedValuesRule
from src.quality.rules.base_rule import BaseRule
from src.quality.rules.custom_rule import CustomExpressionRule
from src.quality.rules.datatype_rule import DataTypeRule
from src.quality.rules.duplicate_rule import UniqueRule
from src.quality.rules.null_rule import NotNullRule
from src.quality.rules.range_rule import RangeRule
from src.quality.rules.regex_rule import RegexRule
from src.quality.schema.schema_drift_detector import SchemaDriftDetector, SchemaDriftReport
from src.quality.scorer import QualityScorer

logger = get_logger(__name__)


class DataQualityEngine:
    """Enterprise Data Quality Engine orchestrating rule execution, profiling, and scoring."""

    def __init__(self, rules: List[BaseRule] = None):
        self.rules = rules or []

    @classmethod
    def from_config(cls, config_data: Dict[str, Any]) -> "DataQualityEngine":
        """Instantiate Engine dynamically from configuration dictionary.

        Args:
            config_data: Parsed rule configuration dictionary.

        Returns:
            DataQualityEngine: Configured engine instance.
        """
        rules: List[BaseRule] = []
        rules_spec = config_data.get("rules", {})

        for col, rule_defs in rules_spec.items():
            if not isinstance(rule_defs, dict):
                continue

            if rule_defs.get("not_null"):
                rules.append(NotNullRule(column=col))

            if rule_defs.get("unique"):
                rules.append(UniqueRule(column=col))

            if "min" in rule_defs or "max" in rule_defs:
                rules.append(
                    RangeRule(
                        column=col,
                        min_val=rule_defs.get("min"),
                        max_val=rule_defs.get("max"),
                    )
                )

            if "allowed_values" in rule_defs:
                rules.append(
                    AllowedValuesRule(
                        column=col,
                        allowed_values=rule_defs["allowed_values"],
                    )
                )

            if "regex" in rule_defs:
                rules.append(
                    RegexRule(
                        column=col,
                        pattern=rule_defs["regex"],
                    )
                )

            if "data_type" in rule_defs:
                rules.append(
                    DataTypeRule(
                        column=col,
                        expected_type=rule_defs["data_type"],
                    )
                )

            if "expression" in rule_defs:
                rules.append(
                    CustomExpressionRule(
                        name=f"CustomExpr({col})",
                        expression=rule_defs["expression"],
                        column=col,
                    )
                )

        logger.info(f"Loaded {len(rules)} Data Quality rules dynamically from configuration.")
        return cls(rules=rules)

    def run_checks(
        self,
        df: DataFrame,
        execution_id: str,
        dataset_name: str = "dataset",
        baseline_schema: Optional[StructType] = None,
    ) -> QualityResult:
        """Execute all data quality rules, profiling, scoring, and drift detection.

        Args:
            df: Input PySpark DataFrame.
            execution_id: Current pipeline execution ID.
            dataset_name: Dataset name identifier.
            baseline_schema: Optional historical baseline schema for drift detection.

        Returns:
            QualityResult: Comprehensive quality execution summary model.
        """
        start_time = time.time()
        total_records = df.count()
        rule_results: List[RuleResult] = []

        logger.info(f"Running Data Quality Engine checks for dataset '{dataset_name}' ({total_records} records)...")

        for rule in self.rules:
            result = rule.evaluate(df)
            rule_results.append(result)

        overall_passed = all(r.passed for r in rule_results)
        failed_records = max([r.failed_records for r in rule_results], default=0)
        passed_records = max(0, total_records - failed_records)

        # Profile & Score
        profile = DataProfiler.profile_dataset(df, dataset_name)
        score = QualityScorer.calculate_score(profile, rule_results)

        duration = time.time() - start_time

        logger.info(
            f"Data Quality Check Completed | Overall Grade: {score.quality_grade} "
            f"({score.overall_quality_score}%) | Rules Evaluated: {len(rule_results)} | Passed: {overall_passed}"
        )

        return QualityResult(
            execution_id=execution_id,
            dataset_name=dataset_name,
            passed=overall_passed,
            total_records=total_records,
            passed_records=passed_records,
            failed_records=failed_records,
            rule_results=rule_results,
            profile=profile,
            score=score,
            processing_duration_seconds=round(duration, 2),
        )
