"""Multi-Year Capacity Planning & Resource Growth Estimation Engine."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from src.common.config.settings import get_settings
from src.observability.logging import TelemetryLogger

logger = TelemetryLogger("capacity_planner")


class CapacityPlanningEngine:
    """Calculates 1-year and 3-year capacity growth projections for Storage, Compute, Network, BigQuery, and AlloyDB."""

    def __init__(self):
        self.settings = get_settings()

    def calculate_capacity_projections(
        self,
        current_monthly_data_tb: float = 1.5,
        monthly_growth_rate_pct: float = 8.0,
    ) -> Dict[str, Any]:
        """Calculate 1-year and 3-year capacity projections.

        Args:
            current_monthly_data_tb: Baseline monthly data ingestion in TB.
            monthly_growth_rate_pct: Expected monthly volume growth percentage.

        Returns:
            Dict[str, Any]: Multi-year capacity projections object.
        """
        logger.info(f"Calculating capacity projections (Baseline: {current_monthly_data_tb} TB/mo, Growth: {monthly_growth_rate_pct}%)...")

        # Compound growth formula: A = P(1 + r)^n
        growth_factor_1yr = (1 + (monthly_growth_rate_pct / 100.0)) ** 12
        growth_factor_3yr = (1 + (monthly_growth_rate_pct / 100.0)) ** 36

        tb_1yr = round(current_monthly_data_tb * growth_factor_1yr, 2)
        tb_3yr = round(current_monthly_data_tb * growth_factor_3yr, 2)

        proj = {
            "environment": self.settings.environment,
            "calculated_at_utc": datetime.now(timezone.utc).isoformat(),
            "baseline_monthly_ingestion_tb": current_monthly_data_tb,
            "monthly_growth_rate_percent": monthly_growth_rate_pct,
            "one_year_projection": {
                "monthly_ingestion_tb": tb_1yr,
                "total_storage_capacity_tb": round(tb_1yr * 12 * 0.7, 2),
                "dataproc_vcpu_hours_per_month": round(120.0 * growth_factor_1yr, 1),
                "bigquery_slots_recommended": int(round(500 * (1 + (monthly_growth_rate_pct / 100.0) * 6))),
                "alloydb_recommended_read_pool_nodes": 2,
                "network_egress_gb_per_month": round(50.0 * growth_factor_1yr, 1),
            },
            "three_year_projection": {
                "monthly_ingestion_tb": tb_3yr,
                "total_storage_capacity_tb": round(tb_3yr * 36 * 0.7, 2),
                "dataproc_vcpu_hours_per_month": round(120.0 * growth_factor_3yr, 1),
                "bigquery_slots_recommended": int(round(500 * (1 + (monthly_growth_rate_pct / 100.0) * 18))),
                "alloydb_recommended_read_pool_nodes": 4,
                "network_egress_gb_per_month": round(50.0 * growth_factor_3yr, 1),
            },
        }

        logger.info(f"Capacity Projections: 1-Year Monthly Ingestion={tb_1yr} TB, 3-Year Monthly Ingestion={tb_3yr} TB.")
        return proj

    def generate_capacity_plan(self, output_dir: str = ".") -> str:
        """Save capacity_plan.json artifact.

        Args:
            output_dir: Target output directory path.

        Returns:
            str: Path to generated capacity_plan.json.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_file = out_path / "capacity_plan.json"
        plan = self.calculate_capacity_projections()

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)

        logger.info(f"Saved capacity_plan.json to '{json_file.resolve()}'.")
        return str(json_file.resolve())
