"""Cost & Performance Optimization Recommendation Engine."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from src.common.config.settings import get_settings
from src.observability.logging import TelemetryLogger

logger = TelemetryLogger("optimization_engine")


class OptimizationEngine:
    """Generates cost and performance optimization recommendations for BigQuery, Dataproc, GCS, and AlloyDB."""

    def __init__(self):
        self.settings = get_settings()

    def generate_recommendations(self) -> Dict[str, Any]:
        """Generate platform optimization recommendations.

        Returns:
            Dict[str, Any]: Optimization report object.
        """
        logger.info("Generating Cost & Performance Optimization Recommendations...")

        recs = [
            {"category": "Partition Optimization", "item": "FACT_TAXI_TRIPS", "action": "Enforce require_partition_filter=true on BigQuery daily trip_date partitions", "estimated_savings": "30% BQ scan cost"},
            {"category": "Cluster Optimization", "item": "FACT_TAXI_TRIPS", "action": "Cluster by vendor_key, payment_type_key, pickup_location_key, rate_code_key", "estimated_savings": "40% scan reduction"},
            {"category": "Spot VM Usage", "item": "Dataproc Clusters", "action": "Utilize Preemptible/Spot VMs for secondary Dataproc worker nodes", "estimated_savings": "60% compute cost"},
            {"category": "Lifecycle Rules", "item": "GCS Buckets", "action": "Transition raw_bronze files to Nearline after 30 days and Coldline after 90 days", "estimated_savings": "50% GCS storage cost"},
            {"category": "Storage Tiering", "item": "AlloyDB Backups", "action": "Set quantity_based_expiry to 4 weekly backups", "estimated_savings": "20% backup cost"},
            {"category": "Query Optimization", "item": "BigQuery Views", "action": "Use Materialized Views mv_executive_summary_mart and mv_geographic_demand_mart", "estimated_savings": "80% dashboard query latency"},
        ]

        report = {
            "environment": self.settings.environment,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "recommendations_count": len(recs),
            "recommendations": recs,
        }

        logger.info(f"Generated {len(recs)} optimization recommendations.")
        return report

    def generate_optimization_report(self, output_dir: str = ".") -> str:
        """Save optimization_report.json artifact.

        Args:
            output_dir: Target output directory path.

        Returns:
            str: Path to generated optimization_report.json.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_file = out_path / "optimization_report.json"
        report = self.generate_recommendations()

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Saved optimization_report.json to '{json_file.resolve()}'.")
        return str(json_file.resolve())
