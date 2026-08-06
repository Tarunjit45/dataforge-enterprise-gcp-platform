"""Consolidated Operations & Production Readiness Reporter Engine."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.common.config.settings import get_settings
from src.observability.logging import TelemetryLogger
from src.operations.backup_manager import BackupManager
from src.operations.capacity_planner import CapacityPlanningEngine
from src.operations.compliance import ComplianceAuditEngine
from src.operations.disaster_recovery import DisasterRecoveryEngine
from src.operations.iam_audit import IAMAuditEngine
from src.operations.optimization import OptimizationEngine
from src.operations.performance_benchmark import PerformanceBenchmarkEngine
from src.operations.production_readiness import ProductionReadinessEngine
from src.operations.restore_validator import RestoreValidator
from src.operations.security_posture import SecurityPostureEngine

logger = TelemetryLogger("operations_reporter")


class OperationalReportConsolidator:
    """Consolidates and generates all Phase 12 operational readiness and security JSON reports."""

    ALL_REPORT_FILES = [
        "production_readiness.json",
        "security_audit.json",
        "backup_validation.json",
        "dr_validation.json",
        "benchmark_report.json",
        "capacity_plan.json",
        "optimization_report.json",
        "compliance_report.json",
    ]

    def __init__(self, output_dir: str = "."):
        self.settings = get_settings()
        self.output_dir = Path(output_dir)

    def generate_all_operational_reports(self) -> Dict[str, str]:
        """Execute and generate all 8 required Phase 12 JSON report artifacts.

        Returns:
            Dict[str, str]: Map of report artifact key to generated file path.
        """
        logger.info("Generating all 8 Phase 12 Operational & Production Readiness Report Artifacts...")

        p1 = ProductionReadinessEngine().generate_readiness_report(str(self.output_dir))
        p2 = SecurityPostureEngine().generate_security_report(str(self.output_dir))
        p3 = RestoreValidator().generate_backup_validation_report(str(self.output_dir))
        p4 = DisasterRecoveryEngine().generate_dr_report(str(self.output_dir))
        p5 = PerformanceBenchmarkEngine().generate_benchmark_report(str(self.output_dir))
        p6 = CapacityPlanningEngine().generate_capacity_plan(str(self.output_dir))
        p7 = OptimizationEngine().generate_optimization_report(str(self.output_dir))
        p8 = ComplianceAuditEngine().generate_compliance_report(str(self.output_dir))

        report_map = {
            "production_readiness.json": p1,
            "security_audit.json": p2,
            "backup_validation.json": p3,
            "dr_validation.json": p4,
            "benchmark_report.json": p5,
            "capacity_plan.json": p6,
            "optimization_report.json": p7,
            "compliance_report.json": p8,
        }

        logger.info(f"Successfully generated {len(report_map)} Phase 12 JSON report artifacts in '{self.output_dir.resolve()}'.")
        return report_map
