"""Enterprise Data Quality & Governance Framework package."""

try:
    from src.quality.engine import DataQualityEngine
    from src.quality.models.quality_result import (
        ColumnProfile,
        ProfileResult,
        QualityResult,
        QualityScore,
        RuleResult,
    )
    from src.quality.profiler import DataProfiler
    from src.quality.quarantine import QuarantineRouter
    from src.quality.reporter import QualityReporter
    from src.quality.rules.allowed_values_rule import AllowedValuesRule
    from src.quality.rules.base_rule import BaseRule
    from src.quality.rules.custom_rule import CustomExpressionRule
    from src.quality.rules.datatype_rule import DataTypeRule
    from src.quality.rules.duplicate_rule import UniqueRule
    from src.quality.rules.null_rule import NotNullRule
    from src.quality.rules.range_rule import RangeRule
    from src.quality.rules.referential_integrity_rule import ReferentialIntegrityRule
    from src.quality.rules.regex_rule import RegexRule
    from src.quality.schema.schema_drift_detector import SchemaDriftDetector, SchemaDriftReport
    from src.quality.scorer import QualityScorer

    __all__ = [
        "DataQualityEngine",
        "DataProfiler",
        "QualityScorer",
        "QuarantineRouter",
        "QualityReporter",
        "SchemaDriftDetector",
        "SchemaDriftReport",
        "RuleResult",
        "ColumnProfile",
        "ProfileResult",
        "QualityScore",
        "QualityResult",
        "BaseRule",
        "NotNullRule",
        "UniqueRule",
        "RangeRule",
        "AllowedValuesRule",
        "RegexRule",
        "DataTypeRule",
        "ReferentialIntegrityRule",
        "CustomExpressionRule",
    ]
except ImportError:
    from src.quality.models.quality_result import (
        ColumnProfile,
        ProfileResult,
        QualityResult,
        QualityScore,
        RuleResult,
    )

    __all__ = [
        "RuleResult",
        "ColumnProfile",
        "ProfileResult",
        "QualityScore",
        "QualityResult",
    ]
