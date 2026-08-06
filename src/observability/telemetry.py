"""Unified Telemetry Manager for Logging, Metrics, and Tracing."""

from typing import Any, Dict, Optional

from src.observability.logging import TelemetryLogger
from src.observability.metrics import MetricsCollector
from src.observability.tracing import OpenTelemetryTracer, TelemetrySpan


class TelemetryManager:
    """Unified Telemetry manager providing single point of entry for logs, metrics, and OTel traces."""

    def __init__(
        self,
        service_name: str = "enterprise_data_platform",
        correlation_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        self.tracer = OpenTelemetryTracer(
            service_name=service_name,
            trace_id=trace_id,
            execution_id=execution_id,
            correlation_id=correlation_id,
        )
        self.logger = TelemetryLogger(
            name=service_name,
            correlation_id=self.tracer.correlation_id,
            execution_id=self.tracer.execution_id,
            batch_id=batch_id,
            trace_id=self.tracer.trace_id,
        )
        self.metrics = MetricsCollector()

    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> TelemetrySpan:
        """Start a trace span and log start event."""
        span = self.tracer.start_span(name, attributes=attributes)
        self.logger.info(f"Started Span [{name}] (span_id: {span.span_id})")
        return span

    def finish_span(self, span: TelemetrySpan) -> None:
        """Finish a trace span and log completion."""
        span.finish()
        duration = (span.end_time - span.start_time).total_seconds() if span.end_time else 0.0
        self.logger.info(f"Finished Span [{span.name}] (duration: {duration:.3f}s)")
