"""Migration Reporting & Documentation Consolidation Engine."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.common.config.settings import get_settings
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


class MigrationReporter:
    """Consolidates JSON reports and produces unified migration executive dashboards."""

    REQUIRED_REPORT_FILES = [
        "migration_assessment.json",
        "compatibility_report.json",
        "schema_conversion_report.json",
        "migration_validation.json",
        "cutover_report.json",
        "rollback_plan.json",
    ]

    def __init__(self, report_dir: str = "."):
        self.settings = get_settings()
        self.report_dir = Path(report_dir)

    def consolidate_reports(self) -> Dict[str, Any]:
        """Load and consolidate all 6 Phase 9 JSON migration reports.

        Returns:
            Dict[str, Any]: Consolidated migration reporting metrics object.
        """
        consolidated: Dict[str, Any] = {"environment": self.settings.environment, "reports": {}}

        for filename in self.REQUIRED_REPORT_FILES:
            filepath = self.report_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        consolidated["reports"][filename] = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not parse '{filename}': {e}")
                    consolidated["reports"][filename] = {"error": str(e)}
            else:
                consolidated["reports"][filename] = {"status": "MISSING"}

        logger.info(f"Consolidated {len(consolidated['reports'])} migration report artifacts.")
        return consolidated

    def generate_executive_summary_md(self, output_dir: str = ".") -> str:
        """Generate consolidated Markdown migration summary executive dashboard.

        Args:
            output_dir: Target output directory path.

        Returns:
            str: Path to generated migration_executive_summary.md file.
        """
        data = self.consolidate_reports()
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        summary_md_path = out_path / "migration_executive_summary.md"

        md_lines = [
            f"# Enterprise MySQL → AlloyDB Migration Executive Dashboard",
            f"**Execution Environment**: `{self.settings.environment}` | **Project**: `{self.settings.gcp_project_id}`",
            "",
            "## 📊 Generated Report Artifacts Summary",
            "| Report File | Status | Key Metric |",
            "| --- | --- | --- |",
        ]

        reports = data.get("reports", {})
        for req_file in self.REQUIRED_REPORT_FILES:
            file_data = reports.get(req_file, {})
            if "status" in file_data and file_data["status"] == "MISSING":
                md_lines.append(f"| `{req_file}` | ⚠️ MISSING | Not generated |")
            elif "error" in file_data:
                md_lines.append(f"| `{req_file}` | ❌ ERROR | Parse failure |")
            else:
                metric_str = "Generated"
                if "compatibility_score" in file_data:
                    metric_str = f"Score: {file_data['compatibility_score']}%"
                elif "converted_tables_count" in file_data:
                    metric_str = f"Converted Tables: {file_data['converted_tables_count']}"
                elif isinstance(file_data, list):
                    metric_str = f"Tables Validated: {len(file_data)}"
                elif "status" in file_data and isinstance(file_data["status"], dict):
                    metric_str = f"Cutover: {file_data['status'].get('status', 'N/A')}"
                elif "plan_id" in file_data:
                    metric_str = f"Plan ID: {file_data['plan_id']}"

                md_lines.append(f"| `{req_file}` | ✅ GENERATED | `{metric_str}` |")

        with open(summary_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        logger.info(f"Saved executive summary dashboard to '{summary_md_path.resolve()}'.")
        return str(summary_md_path.resolve())
