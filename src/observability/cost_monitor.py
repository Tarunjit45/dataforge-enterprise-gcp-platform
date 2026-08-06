"""FinOps & GCP Infrastructure Cost Observability Engine."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from src.common.config.settings import get_settings
from src.observability.logging import TelemetryLogger

logger = TelemetryLogger("cost_monitor")


class CostObservabilityEngine:
    """Estimates and tracks GCP resource spend across BigQuery, Dataproc, Cloud Storage, AlloyDB, and Network Egress."""

    # Standard GCP List Pricing Constants
    BIGQUERY_PER_TB_SCANNED_USD = 6.25
    DATAPROC_VCPU_PER_HOUR_USD = 0.0475
    STORAGE_PER_GB_MONTH_USD = 0.02
    ALLOYDB_VCPU_PER_HOUR_USD = 0.088
    NETWORK_EGRESS_PER_GB_USD = 0.12

    def __init__(self):
        self.settings = get_settings()

    def calculate_cost_estimate(
        self,
        bigquery_tb_scanned: float = 2.5,
        dataproc_vcpu_hours: float = 120.0,
        storage_gb: float = 500.0,
        alloydb_vcpu_hours: float = 720.0,
        egress_gb: float = 50.0,
    ) -> Dict[str, Any]:
        """Calculate breakdown of estimated daily and monthly GCP resource spend.

        Args:
            bigquery_tb_scanned: Total BigQuery terabytes scanned.
            dataproc_vcpu_hours: Dataproc cluster vCPU hours.
            storage_gb: Total GCS storage volume in GB.
            alloydb_vcpu_hours: AlloyDB instance vCPU hours.
            egress_gb: Network egress volume in GB.

        Returns:
            Dict[str, Any]: Cost breakdown dictionary.
        """
        bq_cost = bigquery_tb_scanned * self.BIGQUERY_PER_TB_SCANNED_USD
        dataproc_cost = dataproc_vcpu_hours * self.DATAPROC_VCPU_PER_HOUR_USD
        gcs_cost = (storage_gb / 30.0) * self.STORAGE_PER_GB_MONTH_USD
        alloydb_cost = alloydb_vcpu_hours * self.ALLOYDB_VCPU_PER_HOUR_USD
        egress_cost = egress_gb * self.NETWORK_EGRESS_PER_GB_USD

        total_daily = bq_cost + dataproc_cost + gcs_cost + (alloydb_cost / 30.0) + egress_cost
        estimated_monthly = round(total_daily * 30.0, 2)

        cost_data = {
            "environment": self.settings.environment,
            "calculated_at_utc": datetime.now(timezone.utc).isoformat(),
            "cost_breakdown_usd": {
                "bigquery_query_cost": round(bq_cost, 2),
                "dataproc_compute_cost": round(dataproc_cost, 2),
                "cloud_storage_cost": round(gcs_cost, 2),
                "alloydb_instance_cost": round(alloydb_cost / 30.0, 2),
                "network_egress_cost": round(egress_cost, 2),
                "estimated_daily_total": round(total_daily, 2),
            },
            "estimated_monthly_spend_usd": estimated_monthly,
            "budget_status": "NORMAL" if estimated_monthly < 5000.0 else "ANOMALY_WARNING",
        }

        logger.info(f"Calculated Estimated Monthly GCP Spend: ${estimated_monthly:.2f} USD (Daily Total: ${total_daily:.2f} USD)")
        return cost_data

    def generate_cost_report(self, output_dir: str = ".") -> str:
        """Save cost_report.json artifact.

        Args:
            output_dir: Target output directory path.

        Returns:
            str: Path to generated cost_report.json.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_file = out_path / "cost_report.json"
        report = self.calculate_cost_estimate()

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Saved cost_report.json to '{json_file.resolve()}'.")
        return str(json_file.resolve())
