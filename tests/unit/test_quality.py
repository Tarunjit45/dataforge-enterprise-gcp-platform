"""Unit tests for Enterprise Data Quality & Governance Framework."""

import json
from pathlib import Path
import pytest

pyspark = pytest.importorskip("pyspark")

from src.quality.engine import DataQualityEngine
from src.quality.models.quality_result import QualityResult
from src.quality.profiler import DataProfiler
from src.quality.quarantine import QuarantineRouter
from src.quality.reporter import QualityReporter
from src.quality.rules.allowed_values_rule import AllowedValuesRule
from src.quality.rules.null_rule import NotNullRule
from src.quality.rules.range_rule import RangeRule
from src.quality.schema.schema_drift_detector import SchemaDriftDetector
from src.quality.scorer import QualityScorer

pyspark = pytest.importorskip("pyspark")
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """Fixture providing local SparkSession."""
    from src.etl.spark_session import get_spark_session
    return get_spark_session("UT-QualityEngine")


@pytest.mark.unit
def test_null_and_range_rules(spark: SparkSession):
    """Test NotNullRule and RangeRule evaluations."""
    df = spark.createDataFrame(
        [(1, 10.0), (None, 5.0), (3, -1.0)],
        ["id", "val"],
    )

    null_rule = NotNullRule(column="id")
    res_null = null_rule.evaluate(df)
    assert res_null.passed is False
    assert res_null.failed_records == 1

    range_rule = RangeRule(column="val", min_val=0.0, max_val=100.0)
    res_range = range_rule.evaluate(df)
    assert res_range.passed is False
    assert res_range.failed_records == 1


@pytest.mark.unit
def test_data_profiler_and_scorer(spark: SparkSession):
    """Test statistical profiling and multi-dimensional quality scoring."""
    df = spark.createDataFrame(
        [(1, "A"), (2, "B"), (3, "A")],
        ["id", "category"],
    )

    profile = DataProfiler.profile_dataset(df, "test_dataset")
    assert profile.total_rows == 3
    assert profile.total_columns == 2
    assert profile.duplicate_rows == 0

    score = QualityScorer.calculate_score(profile, [])
    assert score.overall_quality_score == 100.0
    assert score.quality_grade == "A"


@pytest.mark.unit
def test_schema_drift_detector(spark: SparkSession):
    """Test baseline schema drift detection."""
    df = spark.createDataFrame([(1, "data")], ["id", "new_col"])
    baseline_schema = StructType(
        [
            StructField("id", IntegerType(), True),
            StructField("missing_col", StringType(), True),
        ]
    )

    report = SchemaDriftDetector.detect_drift(df, baseline_schema, "test_dataset")
    assert report.has_drift is True
    assert "missing_col" in report.missing_columns
    assert "new_col" in report.new_columns


@pytest.mark.unit
def test_quarantine_router(spark: SparkSession):
    """Test routing non-compliant records to Quarantine without pipeline failure."""
    df = spark.createDataFrame(
        [(1, 10.0), (2, -5.0)],
        ["id", "val"],
    )
    rules = [RangeRule(column="val", min_val=0.0)]

    valid_df, quarantine_df = QuarantineRouter.route_invalid_records(df, rules, "exec-123")
    assert valid_df.count() == 1
    assert quarantine_df.count() == 1
    assert "_execution_id" in quarantine_df.columns


@pytest.mark.unit
def test_data_quality_engine_from_config(spark: SparkSession):
    """Test dynamic DataQualityEngine instantiation from config dictionary."""
    config_data = {
        "rules": {
            "id": {"not_null": True},
            "val": {"min": 0.0, "max": 100.0},
        }
    }

    engine = DataQualityEngine.from_config(config_data)
    assert len(engine.rules) == 2

    df = spark.createDataFrame([(1, 50.0)], ["id", "val"])
    result = engine.run_checks(df, "exec-456", "test_config_dataset")
    assert result.passed is True


@pytest.mark.unit
def test_quality_reporter(spark: SparkSession, tmp_path: Path):
    """Test generating 5 JSON quality reports."""
    df = spark.createDataFrame([(1, 10.0)], ["id", "val"])
    engine = DataQualityEngine([NotNullRule("id")])
    result = engine.run_checks(df, "exec-789", "test_report_dataset")

    schema_drift = SchemaDriftDetector.detect_drift(df, df.schema, "test_report_dataset")
    reports = QualityReporter.generate_all_reports(result, schema_drift, tmp_path)

    assert len(reports) == 5
    assert (tmp_path / "quality_report.json").exists()
    assert (tmp_path / "execution_summary.json").exists()
