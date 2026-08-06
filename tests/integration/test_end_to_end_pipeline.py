"""End-to-End Integration Test Suite (Phase 14)."""

from pathlib import Path
import pytest

pyspark = pytest.importorskip("pyspark")

from src.e2e_runner import EndToEndPipelineRunner
from src.ingestion.pipeline import IngestionPipeline
from src.quality.engine import DataQualityEngine
from src.warehouse.loader import GoldWarehouseLoader
from src.migration.reporting import MigrationReporter
from src.observability.telemetry import TelemetryManager
from src.operations.production_readiness import ProductionReadinessEngine


@pytest.mark.integration
def test_full_pipeline_orchestration_flow(tmp_path):
    """Validate full end-to-end pipeline execution from Ingestion to Gold Warehouse, Migration, and Readiness Reports."""
    runner = EndToEndPipelineRunner(output_dir=str(tmp_path))
    final_res = runner.generate_final_platform_validation()

    assert final_res["overall_platform_validation_status"] == "PASSED 🚀"
    assert final_res["production_go_live_readiness_score_percent"] >= 95.0

    # Verify all output artifacts were created
    assert Path(tmp_path / "architecture_validation_report.json").exists()
    assert Path(tmp_path / "performance_report.json").exists()
    assert Path(tmp_path / "final_platform_validation.json").exists()
    assert Path(tmp_path / "production_readiness.json").exists()
    assert Path(tmp_path / "security_audit.json").exists()


@pytest.mark.integration
def test_infrastructure_and_architecture_validation(tmp_path):
    """Validate infrastructure components health and architecture rules."""
    runner = EndToEndPipelineRunner(output_dir=str(tmp_path))
    arch_res = runner.validate_architecture_infrastructure()

    assert arch_res["overall_architecture_valid"] is True
    assert arch_res["components_validated_count"] == 7
    assert arch_res["security_posture_passed"] is True


@pytest.mark.integration
def test_bigquery_gold_warehouse_loading_integration():
    """Validate BigQuery Gold loader schema initialization and SQL MERGE generation."""
    loader = GoldWarehouseLoader()
    merge_sql = loader.generate_incremental_merge_sql(
        target_table="gold_analytics.fact_trip",
        source_view="silver_cleansed_trips",
        primary_key="trip_key",
    )
    assert "MERGE" in merge_sql
    assert "gold_analytics.fact_trip" in merge_sql


@pytest.mark.integration
def test_migration_and_observability_integration():
    """Validate MySQL to AlloyDB migration reporting and Telemetry logging integration."""
    telemetry = TelemetryManager(service_name="integration_test")
    span = telemetry.start_span("migration_check")

    mig_rep = MigrationReporter().consolidate_reports()
    assert "reports" in mig_rep

    telemetry.finish_span(span)
    assert span.end_time is not None
