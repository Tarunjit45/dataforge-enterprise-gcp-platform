"""Enterprise Metrics Collector & Performance Registry Engine."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.common.config.settings import get_settings
from src.observability.logging import TelemetryLogger

logger = TelemetryLogger("metrics_collector")


class MetricsCollector:
    """Collects, aggregates, and stores custom GCP platform telemetry metrics."""

    def __init__(self):
        self.settings = get_settings()
        self.metrics_store: Dict[str, Any] = {
            "pipeline_duration_seconds": 0.0,
            "records_processed_total": 0,
            "records_rejected_total": 0,
            "data_quality_score_percent": 100.0,
            "quarantine_rate_percent": 0.0,
            "spark_execution_time_seconds": 0.0,
            "bigquery_load_duration_seconds": 0.0,
            "migration_duration_seconds": 0.0,
            "cdc_replication_lag_seconds": 0.0,
            "infrastructure_deployment_duration_seconds": 0.0,
        }

    def record_metric(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record or update a custom metric value.

        Args:
            name: Metric name key.
            value: Metric numeric value.
            labels: Optional dictionary of dimensional labels.
        """
        self.metrics_store[name] = value
        logger.info(f"Recorded metric '{name}' = {value} (labels: {labels or {}})")

    def calculate_quarantine_rate(self, total_processed: int, total_rejected: int) -> float:
        """Calculate quarantine rate percentage."""
        if total_processed <= 0:
            return 0.0
        rate = round((total_rejected / total_processed) * 100.0, 2)
        self.record_metric("quarantine_rate_percent", rate)
        return rate

    def get_all_metrics(self) -> Dict[str, Any]:
        """Retrieve full metric snapshot."""
        return {
            "environment": self.settings.environment,
            "gcp_project_id": self.settings.gcp_project_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "metrics": self.metrics_store,
        }

    def save_pipeline_metrics(self, output_dir: str = ".") -> str:
        """Output pipeline_metrics.json artifact file.

        Args:
            output_dir: Target directory path.

        Returns:
            str: Absolute file path to saved JSON artifact.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_file = out_path / "pipeline_metrics.json"
        data = self.get_all_metrics()

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved pipeline_metrics.json to '{json_file.resolve()}'.")
        return str(json_file.resolve())
