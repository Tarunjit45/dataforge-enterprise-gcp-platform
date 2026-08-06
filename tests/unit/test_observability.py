"""Unit tests for Enterprise Monitoring & Observability Platform (Phase 11)."""

import json
from pathlib import Path
import pytest

from src.observability.alerting import AlertEvaluator
from src.observability.cost_monitor import CostObservabilityEngine
from src.observability.dashboards import DashboardGenerator
from src.observability.health_checks import ServiceHealthChecker
from src.observability.logging import TelemetryLogger
from src.observability.metrics import MetricsCollector
from src.observability.sla import SLACalculator
from src.observability.telemetry import TelemetryManager
from src.observability.tracing import OpenTelemetryTracer
from src.observability.exporters.cloud_monitoring import CloudMonitoringExporter
from src.observability.exporters.cloud_logging import CloudLoggingExporter
from src.observability.exporters.prometheus import PrometheusExporter
from src.observability.exporters.opentelemetry import OpenTelemetryExporter


@pytest.mark.unit
def test_structured_logging_context():
    """Verify TelemetryLogger output formatting and correlation IDs."""
    logger = TelemetryLogger(name="test_logger", correlation_id="corr_123", execution_id="exec_456")
    assert logger.correlation_id == "corr_123"
    assert logger.execution_id == "exec_456"
    assert logger.trace_id is not None


@pytest.mark.unit
def test_metrics_collector_and_artifact(tmp_path):
    """Verify metrics recording and pipeline_metrics.json generation."""
    collector = MetricsCollector()
    collector.record_metric("pipeline_duration_seconds", 45.2)
    collector.record_metric("records_processed_total", 10000)
    rate = collector.calculate_quarantine_rate(10000, 500)

    assert rate == 5.0
    assert collector.get_all_metrics()["metrics"]["quarantine_rate_percent"] == 5.0

    filepath = collector.save_pipeline_metrics(output_dir=str(tmp_path))
    assert Path(filepath).exists()


@pytest.mark.unit
def test_opentelemetry_tracing_and_spans():
    """Verify OpenTelemetry tracer span creation, duration, and attributes."""
    tracer = OpenTelemetryTracer(service_name="test_service", trace_id="tr_100")
    span = tracer.start_span("test_operation", attributes={"batch_id": "b_1"})

    assert span.trace_id == "tr_100"
    assert span.attributes["batch_id"] == "b_1"

    span.finish()
    assert span.end_time is not None
    span_dict = span.to_dict()
    assert "duration_ms" in span_dict


@pytest.mark.unit
def test_unified_telemetry_manager():
    """Verify TelemetryManager wrapper for spans and logs."""
    mgr = TelemetryManager(service_name="unified_test")
    span = mgr.start_span("etl_process")
    mgr.finish_span(span)
    assert span.end_time is not None


@pytest.mark.unit
def test_service_health_checks_and_artifact(tmp_path):
    """Verify service health checks and health_report.json generation."""
    checker = ServiceHealthChecker()
    report = checker.run_all_health_checks()

    assert report["overall_status"] == "HEALTHY"
    assert len(report["services"]) == 7

    filepath = checker.generate_health_report(output_dir=str(tmp_path))
    assert Path(filepath).exists()


@pytest.mark.unit
def test_alert_evaluator():
    """Verify alert policy condition triggers."""
    evaluator = AlertEvaluator()

    # Normal metrics (No alert)
    alert_none = evaluator.evaluate_metric("high_cdc_lag", 2.0)
    assert alert_none is None

    # Threshold breach (Alert Fired)
    alert_fired = evaluator.evaluate_metric("high_cdc_lag", 15.0)
    assert alert_fired is not None
    assert alert_fired["severity"] == "HIGH"

    dq_alert = evaluator.evaluate_metric("dq_score_below_threshold", 65.0)
    assert dq_alert is not None
    assert dq_alert["severity"] == "HIGH"


@pytest.mark.unit
def test_dashboard_generator_and_artifact(tmp_path):
    """Verify dashboard specs and dashboard_summary.json generation."""
    generator = DashboardGenerator()
    summary_path = generator.generate_all_dashboards(output_dir=str(tmp_path))
    assert Path(summary_path).exists()


@pytest.mark.unit
def test_sla_calculator_and_artifact(tmp_path):
    """Verify SLO metrics calculation and sla_report.json generation."""
    calculator = SLACalculator()
    slo_res = calculator.calculate_platform_slo(total_executions=1000, successful_executions=999)

    assert slo_res["availability"]["is_met"] is True
    assert slo_res["error_budget"]["remaining_percent"] > 0

    filepath = calculator.generate_sla_report(output_dir=str(tmp_path))
    assert Path(filepath).exists()


@pytest.mark.unit
def test_cost_observability_and_artifact(tmp_path):
    """Verify cost calculation breakdown and cost_report.json generation."""
    cost_eng = CostObservabilityEngine()
    cost_data = cost_eng.calculate_cost_estimate(bigquery_tb_scanned=10.0, dataproc_vcpu_hours=200.0)

    assert cost_data["cost_breakdown_usd"]["bigquery_query_cost"] == 62.5
    assert cost_data["estimated_monthly_spend_usd"] > 0

    filepath = cost_eng.generate_cost_report(output_dir=str(tmp_path))
    assert Path(filepath).exists()


@pytest.mark.unit
def test_exporters():
    """Verify metrics, log, Prometheus, and OTel exporters."""
    collector = MetricsCollector()
    collector.record_metric("test_metric", 123.4)

    prom_exp = PrometheusExporter(collector)
    prom_text = prom_exp.export_prometheus_text()
    assert "test_metric 123.4" in prom_text

    tracer = OpenTelemetryTracer()
    span = tracer.start_span("test_span")
    otel_exp = OpenTelemetryExporter(tracer)
    exported_spans = otel_exp.export_spans()
    assert len(exported_spans) == 1

    cm_exp = CloudMonitoringExporter()
    assert cm_exp.export_metric("test_metric", 123.4) is True

    cl_exp = CloudLoggingExporter()
    assert cl_exp.export_log_entry({"message": "test"}) is True
