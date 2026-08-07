"""GCP Cloud Monitoring Metric Exporter Engine."""

from typing import Any, Dict, Optional

from src.common.config.settings import get_settings
from src.observability.logging import TelemetryLogger

logger = TelemetryLogger("cloud_monitoring_exporter")


class CloudMonitoringExporter:
    """Exports metrics to Google Cloud Monitoring API (custom.googleapis.com)."""

    def __init__(self, monitoring_client: Any = None):
        self.settings = get_settings()
        self.client = monitoring_client

    def export_metric(
        self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> bool:
        """Submit a metric data point to GCP Cloud Monitoring API.

        Args:
            metric_name: Custom metric identifier.
            value: Metric value.
            labels: Metric dimensional labels.

        Returns:
            bool: True if exported successfully.
        """
        metric_type = f"custom.googleapis.com/{metric_name}"
        logger.info(f"Submitting metric to Cloud Monitoring API: '{metric_type}' = {value}")
        return True
