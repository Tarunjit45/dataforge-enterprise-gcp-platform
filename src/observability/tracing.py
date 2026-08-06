"""OpenTelemetry Tracing & Span Context Manager Engine."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class TelemetrySpan:
    """OpenTelemetry span representation model."""

    span_id: str
    name: str
    trace_id: str
    execution_id: str
    correlation_id: str
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)

    def finish(self) -> None:
        """Mark span execution finished."""
        self.end_time = datetime.now(timezone.utc)

    def add_attribute(self, key: str, value: Any) -> None:
        """Add attribute key-value pair to span."""
        self.attributes[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Serialize span data to dictionary format."""
        return {
            "span_id": self.span_id,
            "name": self.name,
            "trace_id": self.trace_id,
            "execution_id": self.execution_id,
            "correlation_id": self.correlation_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": (self.end_time - self.start_time).total_seconds() * 1000.0 if self.end_time else None,
            "attributes": self.attributes,
        }


class OpenTelemetryTracer:
    """OpenTelemetry compatible tracer managing spans, trace IDs, and context propagation."""

    def __init__(
        self,
        service_name: str = "enterprise_data_platform",
        trace_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        self.service_name = service_name
        self.trace_id = trace_id or str(uuid.uuid4())
        self.execution_id = execution_id or str(uuid.uuid4())
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.spans: List[TelemetrySpan] = []

    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> TelemetrySpan:
        """Start a new telemetry span with trace context propagation.

        Args:
            name: Span operation name.
            attributes: Optional key-value attributes.

        Returns:
            TelemetrySpan: Instantiated span object.
        """
        span = TelemetrySpan(
            span_id=str(uuid.uuid4()),
            name=name,
            trace_id=self.trace_id,
            execution_id=self.execution_id,
            correlation_id=self.correlation_id,
            attributes=attributes or {},
        )
        span.add_attribute("service.name", self.service_name)
        span.add_attribute("execution_id", self.execution_id)
        span.add_attribute("correlation_id", self.correlation_id)

        self.spans.append(span)
        return span
