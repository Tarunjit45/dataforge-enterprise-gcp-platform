"""Google Cloud Monitoring Operational & Executive Dashboard Spec Generator."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from src.common.config.settings import get_settings
from src.observability.logging import TelemetryLogger

logger = TelemetryLogger("dashboard_generator")


class DashboardGenerator:
    """Generates Google Cloud Monitoring JSON dashboard specifications."""

    DASHBOARD_NAMES = [
        "Executive Dashboard",
        "Operations Dashboard",
        "ETL Dashboard",
        "Migration Dashboard",
        "Infrastructure Dashboard",
        "Cost Dashboard",
    ]

    def __init__(self):
        self.settings = get_settings()

    def generate_dashboard_spec(self, dashboard_name: str) -> Dict[str, Any]:
        """Generate Cloud Monitoring dashboard specification payload.

        Args:
            dashboard_name: Title of dashboard to generate.

        Returns:
            Dict[str, Any]: Dashboard specification JSON schema.
        """
        spec = {
            "displayName": f"{dashboard_name} - [{self.settings.environment.upper()}]",
            "gridLayout": {
                "columns": 2,
                "widgets": [
                    {
                        "title": f"{dashboard_name} Metric Widget",
                        "scorecard": {
                            "timeSeriesQuery": {
                                "timeSeriesFilter": {
                                    "filter": f'metric.type = "custom.googleapis.com/{dashboard_name.lower().replace(" ", "_")}"',
                                }
                            }
                        },
                    }
                ],
            },
        }
        logger.info(f"Generated Cloud Monitoring Dashboard spec for '{dashboard_name}'.")
        return spec

    def generate_all_dashboards(self, output_dir: str = ".") -> str:
        """Generate all 6 dashboards and save dashboard_summary.json artifact.

        Args:
            output_dir: Target output directory path.

        Returns:
            str: Path to saved dashboard_summary.json.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_file = out_path / "dashboard_summary.json"
        summary = {
            "environment": self.settings.environment,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "total_dashboards": len(self.DASHBOARD_NAMES),
            "dashboards": [self.generate_dashboard_spec(name) for name in self.DASHBOARD_NAMES],
        }

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Saved dashboard_summary.json to '{json_file.resolve()}'.")
        return str(json_file.resolve())
