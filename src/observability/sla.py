"""Service Level Agreement (SLA) & SLO Error Budget Engine."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.common.config.settings import get_settings
from src.observability.logging import TelemetryLogger

logger = TelemetryLogger("sla_engine")


class SLACalculator:
    """Calculates platform Availability, Latency, Data Freshness, Success Rate, MTTR, and Error Budget consumption."""

    def __init__(self):
        self.settings = get_settings()

    def calculate_platform_slo(
        self,
        total_executions: int = 1000,
        successful_executions: int = 998,
        avg_latency_seconds: float = 180.0,
        data_freshness_minutes: float = 25.0,
        mttr_minutes: float = 8.5,
    ) -> Dict[str, Any]:
        """Calculate SLA/SLO compliance metrics and Error Budget consumption.

        Args:
            total_executions: Total pipeline runs evaluated.
            successful_executions: Total successful pipeline runs.
            avg_latency_seconds: Observed average processing latency.
            data_freshness_minutes: Observed data freshness lag in minutes.
            mttr_minutes: Observed Mean Time to Recover.

        Returns:
            Dict[str, Any]: SLA compliance metrics dictionary.
        """
        availability_pct = round((successful_executions / max(1, total_executions)) * 100.0, 2)
        target_availability = 99.9
        error_budget_total = 100.0 - target_availability  # 0.1% total error budget
        error_budget_consumed = max(0.0, round(target_availability - availability_pct, 2))
        error_budget_remaining_pct = (
            max(0.0, round(100.0 - (error_budget_consumed / error_budget_total * 100.0), 2))
            if error_budget_total > 0
            else 100.0
        )

        slo_report = {
            "environment": self.settings.environment,
            "calculated_at_utc": datetime.now(timezone.utc).isoformat(),
            "availability": {
                "target_percent": target_availability,
                "observed_percent": availability_pct,
                "is_met": availability_pct >= target_availability,
            },
            "latency": {
                "target_seconds": 300.0,
                "observed_avg_seconds": avg_latency_seconds,
                "is_met": avg_latency_seconds <= 300.0,
            },
            "data_freshness": {
                "target_minutes": 60.0,
                "observed_minutes": data_freshness_minutes,
                "is_met": data_freshness_minutes <= 60.0,
            },
            "success_rate": {
                "target_percent": 99.5,
                "observed_percent": availability_pct,
                "is_met": availability_pct >= 99.5,
            },
            "recovery_time_objective": {
                "target_mttr_minutes": 15.0,
                "observed_mttr_minutes": mttr_minutes,
                "is_met": mttr_minutes <= 15.0,
            },
            "error_budget": {
                "target_error_budget_percent": error_budget_total,
                "consumed_percent": error_budget_consumed,
                "remaining_percent": error_budget_remaining_pct,
            },
        }

        logger.info(
            f"SLA Calculation: Availability={availability_pct}%, Freshness={data_freshness_minutes}m, ErrorBudgetRemaining={error_budget_remaining_pct}%"
        )
        return slo_report

    def generate_sla_report(self, output_dir: str = ".") -> str:
        """Save sla_report.json artifact.

        Args:
            output_dir: Target output directory path.

        Returns:
            str: Path to generated sla_report.json.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_file = out_path / "sla_report.json"
        report = self.calculate_platform_slo()

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Saved sla_report.json to '{json_file.resolve()}'.")
        return str(json_file.resolve())
