"""Unit tests for Enterprise MySQL to AlloyDB Migration Framework (Phase 9)."""

import json
from pathlib import Path
import pytest

from src.migration.assessment import DatabaseAssessmentEngine
from src.migration.checksum import ChecksumEngine
from src.migration.cutover import CutoverOrchestrator
from src.migration.extractor import DataExtractor
from src.migration.loader import DataLoader
from src.migration.metadata import DatabaseInventory, MigrationStatus, ValidationResult
from src.migration.reporting import MigrationReporter
from src.migration.rollback import RollbackEngine
from src.migration.schema_converter import SchemaConverter
from src.migration.cdc.datastream import DatastreamCDCManager
from src.migration.cdc.replication import BinlogReplicationTracker
from src.migration.validator import MigrationValidator


@pytest.mark.unit
def test_schema_converter_datatype_mapping():
    """Verify MySQL to AlloyDB data type conversion rules."""
    converter = SchemaConverter()
    assert converter.convert_column_type("int") == "INTEGER"
    assert converter.convert_column_type("bigint") == "BIGINT"
    assert converter.convert_column_type("tinyint", "tinyint(1)") == "BOOLEAN"
    assert converter.convert_column_type("varchar", "varchar(255)") == "VARCHAR(255)"
    assert converter.convert_column_type("datetime") == "TIMESTAMP WITHOUT TIME ZONE"
    assert converter.convert_column_type("json") == "JSONB"
    assert converter.convert_column_type("longblob") == "BYTEA"


@pytest.mark.unit
def test_schema_converter_ddl_generation(tmp_path):
    """Verify DDL translation and report generation."""
    converter = SchemaConverter()
    assessment_engine = DatabaseAssessmentEngine()
    inventory = assessment_engine._introspect_mysql_schema("test_db")

    sql_ddl, report = converter.generate_alloydb_ddl(inventory, target_schema="public")
    assert "CREATE TABLE IF NOT EXISTS \"public\".\"customers\"" in sql_ddl
    assert "\"is_active\" BOOLEAN" in sql_ddl
    assert "GENERATED ALWAYS AS IDENTITY" in sql_ddl
    assert report["converted_tables_count"] == 4

    paths = converter.save_conversion_output(sql_ddl, report, output_dir=str(tmp_path))
    assert Path(paths["converted_sql"]).exists()
    assert Path(paths["conversion_report_json"]).exists()


@pytest.mark.unit
def test_database_assessment_engine(tmp_path):
    """Verify database inventory analysis, compatibility scoring, and report outputs."""
    engine = DatabaseAssessmentEngine()
    inventory = engine._introspect_mysql_schema("test_db")
    result = engine.assess_database(inventory)

    assert result.compatibility_score == 100.0
    assert result.estimated_effort_hours > 0.0

    paths = engine.generate_assessment_reports(result, output_dir=str(tmp_path))
    assert Path(paths["assessment_json"]).exists()
    assert Path(paths["compatibility_json"]).exists()
    assert Path(paths["assessment_md"]).exists()


@pytest.mark.unit
def test_checksum_engine():
    """Verify SHA256 hashing and checksum comparisons."""
    engine = ChecksumEngine()
    row1 = {"id": 1, "name": "Alice", "balance": 100.50}
    row2 = {"id": 1, "name": "Alice", "balance": 100.50}
    row3 = {"id": 1, "name": "Alice", "balance": 999.99}

    hash1 = engine.compute_row_hash(row1)
    hash2 = engine.compute_row_hash(row2)
    hash3 = engine.compute_row_hash(row3)

    assert hash1 == hash2
    assert hash1 != hash3

    table_data = [row1, row2]
    table_hash = engine.compute_table_checksum(table_data)
    assert engine.compare_checksums(table_hash, table_hash) is True


@pytest.mark.unit
def test_extractor_and_loader_pipeline(tmp_path):
    """Verify batch extraction, loading, and checkpoint tracking."""
    extractor = DataExtractor(batch_size=50)
    loader = DataLoader()

    sample_records = [{"id": i, "name": f"user_{i}"} for i in range(1, 101)]

    extracted_batches = list(extractor.extract_table_batches("users", sample_data=sample_records))
    assert len(extracted_batches) == 2  # 100 records / 50 batch_size = 2 batches

    first_batch = extracted_batches[0]
    checkpoint = loader.load_batch("users", first_batch["records"], expected_checksum=first_batch["batch_checksum"])

    assert checkpoint.rows_loaded == 50


@pytest.mark.unit
def test_migration_validator(tmp_path):
    """Verify row count, checksum, and sample validation logic."""
    validator = MigrationValidator()
    data_src = [{"id": 1, "val": "A"}, {"id": 2, "val": "B"}]
    data_tgt = [{"id": 1, "val": "A"}, {"id": 2, "val": "B"}]

    res_pass = validator.validate_table_migration("test_tbl", data_src, data_tgt)
    assert res_pass.is_passed is True

    data_mismatch = [{"id": 1, "val": "A"}, {"id": 2, "val": "X"}]
    res_fail = validator.validate_table_migration("test_tbl", data_src, data_mismatch)
    assert res_fail.is_passed is False

    paths = validator.generate_validation_report([res_pass], output_dir=str(tmp_path))
    assert Path(paths["validation_json"]).exists()
    assert Path(paths["validation_md"]).exists()


@pytest.mark.unit
def test_datastream_and_binlog_cdc():
    """Verify Datastream CDC config generator and binlog lag tracking."""
    cdc_mgr = DatastreamCDCManager()
    config = cdc_mgr.generate_datastream_config()
    assert "source_config" in config
    assert "destination_config" in config

    tracker = BinlogReplicationTracker()
    status = tracker.get_current_binlog_status()
    assert status["binlog_file"] == "mysql-bin.000042"

    lag = tracker.check_replication_lag(threshold_seconds=5.0)
    assert lag["is_ready_for_cutover"] is True


@pytest.mark.unit
def test_cutover_and_rollback_flow(tmp_path):
    """Verify production cutover and emergency rollback execution flows."""
    val_res = ValidationResult(
        table_name="customers",
        source_row_count=100,
        target_row_count=100,
        row_count_match=True,
        source_checksum="abc",
        target_checksum="abc",
        checksum_match=True,
        is_passed=True,
    )

    cutover_orch = CutoverOrchestrator()
    status = cutover_orch.execute_cutover([val_res], replication_lag_seconds=1.0, output_dir=str(tmp_path))
    assert status.status == MigrationStatus.CUTOVER_SUCCESS
    assert status.application_switched is True
    assert (tmp_path / "cutover_report.json").exists()

    rollback_eng = RollbackEngine()
    plan = rollback_eng.generate_rollback_plan(trigger_reason="Validation failure test", target_tables=["customers"])
    executed_plan = rollback_eng.execute_rollback(plan, output_dir=str(tmp_path))
    assert executed_plan.status == "EXECUTED"
    assert executed_plan.dns_reverted is True
    assert (tmp_path / "rollback_plan.json").exists()


@pytest.mark.unit
def test_migration_reporter_consolidation(tmp_path):
    """Verify consolidation of all 6 required migration JSON reports."""
    # Write mock JSON files
    required_files = [
        "migration_assessment.json",
        "compatibility_report.json",
        "schema_conversion_report.json",
        "migration_validation.json",
        "cutover_report.json",
        "rollback_plan.json",
    ]
    for fn in required_files:
        p = tmp_path / fn
        p.write_text(json.dumps({"test_key": fn}), encoding="utf-8")

    reporter = MigrationReporter(report_dir=str(tmp_path))
    consolidated = reporter.consolidate_reports()
    assert len(consolidated["reports"]) == 6

    summary_file = reporter.generate_executive_summary_md(output_dir=str(tmp_path))
    assert Path(summary_file).exists()
