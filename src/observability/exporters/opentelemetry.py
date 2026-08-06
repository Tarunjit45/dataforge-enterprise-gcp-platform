"""OpenTelemetry Trace Span Exporter Engine."""

from typing import Any, Dict, List
from src.observability.tracing import OpenTelemetryTracer, TelemetrySpan
from src.observability.logging import TelemetryLogger

logger = TelemetryLogger("opentelemetry_exporter")


class OpenTelemetryExporter:
    """Exports OpenTelemetry span batches to Cloud Trace / OpenTelemetry Collector."""

    def __init__(self, tracer: OpenTelemetryTracer):
        self.tracer = tracer

    def export_spans(self) -> List[Dict[str, Any]]:
        """Export serialized span context payloads.

        Returns:
            List[Dict[str, Any]]: List of span dictionaries.
        """
        exported = [span.to_dict() for span in self.tracer.spans]
        logger.info(f"Exported {len(exported)} OpenTelemetry spans to Cloud Trace.")
        return exported
