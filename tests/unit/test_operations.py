"""Unit tests for Phase 12 Operational Excellence & Production Hardening Framework."""

from pathlib import Path
import pytest

from src.operations.backup_manager import BackupManager
from src.operations.capacity_planner import CapacityPlanningEngine
from src.operations.chaos_testing import ChaosTestingEngine
from src.operations.compliance import ComplianceAuditEngine
from src.operations.disaster_recovery import DisasterRecoveryEngine
from src.operations.iam_audit import IAMAuditEngine
from src.operations.load_testing import LoadTestingEngine
from src.operations.optimization import OptimizationEngine
from src.operations.performance_benchmark import PerformanceBenchmarkEngine
from src.operations.production_readiness import ProductionReadinessEngine
from src.operations.reports import OperationalReportConsolidator
from src.operations.restore_validator import RestoreValidator
from src.operations.security_posture import SecurityPostureEngine


@pytest.mark.unit
def test_iam_audit_engine():
    """Verify IAM audit, primitive role violation detection, and least privilege verification."""
    engine = IAMAuditEngine()
    report = engine.audit_iam_policy()

    assert report["least_privilege_passed"] is True
    assert len(report["primitive_role_violations"]) == 0
    assert report["workload_identity_configured"] is True


@pytest.mark.unit
def test_backup_and_restore_validator(tmp_path):
    """Verify backup status checking and restore validation report artifact."""
    validator = RestoreValidator()
    report = validator.validate_all_backups()

    assert report["overall_status"] == "PASSED"
    assert len(report["validations"]) == 4

    filepath = validator.generate_backup_validation_report(output_dir=str(tmp_path))
    assert Path(filepath).exists()


@pytest.mark.unit
def test_disaster_recovery_simulation(tmp_path):
    """Verify regional failover simulation and RPO/RTO target checks."""
    dr = DisasterRecoveryEngine(primary_region="us-central1", secondary_region="us-east4")
    res = dr.simulate_regional_failover(target_rpo_minutes=5.0, target_rto_minutes=15.0)

    assert res["overall_dr_passed"] is True
    assert res["rpo"]["passed"] is True
    assert res["rto"]["passed"] is True

    filepath = dr.generate_dr_report(output_dir=str(tmp_path))
    assert Path(filepath).exists()


@pytest.mark.unit
def test_chaos_testing_engine():
    """Verify chaos experiment fault injections and resiliency recovery."""
    chaos = ChaosTestingEngine()
    suite = chaos.run_all_experiments()

    assert suite["overall_resiliency_status"] == "PASSED"
    assert suite["total_experiments_run"] == 6


@pytest.mark.unit
def test_performance_benchmark_engine(tmp_path):
    """Verify performance throughput benchmarking and SLA evaluation."""
    bench = PerformanceBenchmarkEngine()
    res = bench.run_benchmark_suite()

    assert res["overall_benchmark_passed"] is True
    assert res["metrics"]["etl_throughput_records_per_sec"] >= 10000.0

    filepath = bench.generate_benchmark_report(output_dir=str(tmp_path))
    assert Path(filepath).exists()


@pytest.mark.unit
def test_load_testing_engine():
    """Verify load stress testing concurrency simulation."""
    load_tester = LoadTestingEngine()
    res = load_tester.run_concurrency_stress_test(concurrent_streams=50)

    assert res["concurrent_streams"] == 50
    assert res["peak_throughput_rps"] == 25000.0


@pytest.mark.unit
def test_capacity_planning_engine(tmp_path):
    """Verify 1-year and 3-year capacity growth projections."""
    planner = CapacityPlanningEngine()
    proj = planner.calculate_capacity_projections(current_monthly_data_tb=1.5, monthly_growth_rate_pct=8.0)

    assert "one_year_projection" in proj
    assert "three_year_projection" in proj
    assert proj["three_year_projection"]["monthly_ingestion_tb"] > proj["one_year_projection"]["monthly_ingestion_tb"]

    filepath = planner.generate_capacity_plan(output_dir=str(tmp_path))
    assert Path(filepath).exists()


@pytest.mark.unit
def test_security_and_compliance(tmp_path):
    """Verify security posture and CIS GCP Benchmark compliance audits."""
    sec = SecurityPostureEngine()
    sec_rep = sec.audit_security_posture()
    assert sec_rep["overall_security_passed"] is True
    assert Path(sec.generate_security_report(output_dir=str(tmp_path))).exists()

    comp = ComplianceAuditEngine()
    comp_rep = comp.evaluate_compliance()
    assert comp_rep["overall_compliance_score_percent"] == 100.0
    assert Path(comp.generate_compliance_report(output_dir=str(tmp_path))).exists()


@pytest.mark.unit
def test_optimization_engine(tmp_path):
    """Verify optimization recommendations generation."""
    opt = OptimizationEngine()
    recs = opt.generate_recommendations()
    assert recs["recommendations_count"] > 0
    assert Path(opt.generate_optimization_report(output_dir=str(tmp_path))).exists()


@pytest.mark.unit
def test_production_readiness_scorecard(tmp_path):
    """Verify 8-dimension Production Readiness Scorecard evaluation."""
    readiness = ProductionReadinessEngine()
    scorecard = readiness.evaluate_production_readiness()

    assert scorecard["overall_readiness_score_percent"] >= 95.0
    assert scorecard["dimensions_evaluated_count"] == 8
    assert "Security" in scorecard["readiness_scorecard"]
    assert "Operational Excellence" in scorecard["readiness_scorecard"]

    filepath = readiness.generate_readiness_report(output_dir=str(tmp_path))
    assert Path(filepath).exists()


@pytest.mark.unit
def test_production_deployment_engine(tmp_path):
    """Verify ProductionDeploymentEngine report generation and validation checks."""
    from src.operations.deployment_engine import ProductionDeploymentEngine
    engine = ProductionDeploymentEngine(output_dir=str(tmp_path))
    reports = engine.run_full_deployment_pipeline()

    assert len(reports) == 3
    assert Path(tmp_path / "system_inventory.json").exists()
    assert Path(tmp_path / "deployment_validation.json").exists()
    assert Path(tmp_path / "production_deployment_report.json").exists()


@pytest.mark.unit
def test_all_operational_reports_generation(tmp_path):
    """Verify generation of all 8 required Phase 12 JSON report artifacts."""
    consolidator = OperationalReportConsolidator(output_dir=str(tmp_path))
    report_map = consolidator.generate_all_operational_reports()

    assert len(report_map) == 8
    for fname, fpath in report_map.items():
        assert Path(fpath).exists(), f"Report file missing: {fname}"
