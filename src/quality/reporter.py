"""Multi-report JSON generator for Data Quality audits."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from src.common.logging.logger import get_logger
from src.quality.models.quality_result import QualityResult
from src.quality.schema.schema_drift_detector import SchemaDriftReport

logger = get_logger(__name__)


class QualityReporter:
    """Generates standardized human and machine-readable JSON quality reports."""

    @staticmethod
    def generate_all_reports(
        quality_result: QualityResult,
        schema_drift: SchemaDriftReport,
        output_dir: Path,
    ) -> Dict[str, Path]:
        """Generate and save all 5 quality audit reports as JSON files.

        Args:
            quality_result: Completed QualityResult model.
            schema_drift: SchemaDriftReport model.
            output_dir: Local output directory for report JSONs.

        Returns:
            Dict[str, Path]: Map of report names to generated file paths.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        report_files = {}

        # 1. quality_report.json
        q_report_path = output_dir / "quality_report.json"
        with open(q_report_path, "w", encoding="utf-8") as f:
            json.dump(asdict(quality_result), f, indent=2)
        report_files["quality_report"] = q_report_path

        # 2. profiling_report.json
        p_report_path = output_dir / "profiling_report.json"
        profile_data = asdict(quality_result.profile) if quality_result.profile else {}
        with open(p_report_path, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2)
        report_files["profiling_report"] = p_report_path

        # 3. schema_drift_report.json
        s_report_path = output_dir / "schema_drift_report.json"
        with open(s_report_path, "w", encoding="utf-8") as f:
            json.dump(asdict(schema_drift), f, indent=2)
        report_files["schema_drift_report"] = s_report_path

        # 4. quality_score.json
        sc_report_path = output_dir / "quality_score.json"
        score_data = asdict(quality_result.score) if quality_result.score else {}
        with open(sc_report_path, "w", encoding="utf-8") as f:
            json.dump(score_data, f, indent=2)
        report_files["quality_score"] = sc_report_path

        # 5. execution_summary.json
        exec_summary = {
            "execution_id": quality_result.execution_id,
            "dataset_name": quality_result.dataset_name,
            "passed": quality_result.passed,
            "total_records": quality_result.total_records,
            "passed_records": quality_result.passed_records,
            "failed_records": quality_result.failed_records,
            "quality_grade": quality_result.score.quality_grade if quality_result.score else "N/A",
            "overall_score": (
                quality_result.score.overall_quality_score if quality_result.score else 0.0
            ),
            "schema_drift_detected": schema_drift.has_drift,
            "duration_seconds": quality_result.processing_duration_seconds,
            "generated_at_utc": quality_result.generated_at_utc,
        }
        e_report_path = output_dir / "execution_summary.json"
        with open(e_report_path, "w", encoding="utf-8") as f:
            json.dump(exec_summary, f, indent=2)
        report_files["execution_summary"] = e_report_path

        logger.info(
            f"Generated {len(report_files)} Quality JSON reports in directory: {output_dir}"
        )
        return report_files
