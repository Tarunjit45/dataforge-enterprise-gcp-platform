"""Prometheus Exposition Format Metric Exporter Engine."""

from typing import Any, Dict
from src.observability.metrics import MetricsCollector


class PrometheusExporter:
    """Exports metrics in Prometheus Exposition text format."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector

    def export_prometheus_text(self) -> str:
        """Format metrics in Prometheus text format.

        Returns:
            str: Prometheus exposition formatted text string.
        """
        metrics = self.collector.get_all_metrics()["metrics"]
        lines = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        return "\n".join(lines) + "\n"
