"""Data Quality Models Package."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class RuleResult:
    """Outcome model for an individual data quality rule execution."""

    rule_name: str
    column: str
    passed: bool
    total_records: int
    failed_records: int
    error_code: str
    error_message: str
    failed_rows_sample: Optional[List[Dict[str, Any]]] = None


@dataclass
class ColumnProfile:
    """Statistical profile of a single column."""

    column_name: str
    data_type: str
    total_count: int
    null_count: int
    null_percentage: float
    distinct_count: int
    distinct_percentage: float
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    mean_val: Optional[float] = None
    top_values: Optional[Dict[str, int]] = None


@dataclass
class ProfileResult:
    """Collection model for dataset-wide statistical profile."""

    dataset_name: str
    total_rows: int
    total_columns: int
    duplicate_rows: int
    duplicate_percentage: float
    column_profiles: Dict[str, ColumnProfile] = field(default_factory=dict)
    generated_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class QualityScore:
    """Multi-dimensional Quality Score model."""

    completeness_score: float
    uniqueness_score: float
    validity_score: float
    overall_quality_score: float
    quality_grade: str


@dataclass
class QualityResult:
    """Overall Data Quality Engine execution result model."""

    execution_id: str
    dataset_name: str
    passed: bool
    total_records: int
    passed_records: int
    failed_records: int
    rule_results: List[RuleResult] = field(default_factory=list)
    profile: Optional[ProfileResult] = None
    score: Optional[QualityScore] = None
    processing_duration_seconds: float = 0.0
    generated_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
