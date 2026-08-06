"""Alert Policy Evaluator & Incident Management Engine."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from src.common.config.settings import get_settings
from src.observability.logging import TelemetryLogger

logger = TelemetryLogger("alert_engine")


class AlertEvaluator:
    """Evaluates metric values against configured threshold rules and triggers alerts."""

    ALERT_RULES = {
        "pipeline_failure": {"metric": "pipeline_status", "op": "==", "threshold": "FAILED", "severity": "CRITICAL"},
        "spark_job_failure": {"metric": "spark_job_status", "op": "==", "threshold": "FAILED", "severity": "CRITICAL"},
        "bigquery_load_failure": {"metric": "bigquery_job_status", "op": "==", "threshold": "FAILED", "severity": "HIGH"},
        "high_cdc_lag": {"metric": "cdc_replication_lag_seconds", "op": ">", "threshold": 10.0, "severity": "HIGH"},
        "dq_score_below_threshold": {"metric": "data_quality_score_percent", "op": "<", "threshold": 70.0, "severity": "HIGH"},
        "high_quarantine_ratio": {"metric": "quarantine_rate_percent", "op": ">", "threshold": 10.0, "severity": "MEDIUM"},
        "infrastructure_deployment_failure": {"metric": "deploy_status", "op": "==", "threshold": "FAILED", "severity": "CRITICAL"},
        "high_cost_anomaly": {"metric": "daily_spend_usd", "op": ">", "threshold": 150.0, "severity": "MEDIUM"},
    }

    def __init__(self):
        self.settings = get_settings()

    def evaluate_metric(self, alert_name: str, current_value: Any) -> Optional[Dict[str, Any]]:
        """Evaluate a single metric value against an alert policy.

        Args:
            alert_name: Alert rule name key.
            current_value: Observed metric value.

        Returns:
            Optional[Dict[str, Any]]: Fired alert payload if threshold breached, else None.
        """
        rule = self.ALERT_RULES.get(alert_name)
        if not rule:
            return None

        is_fired = False
        op = rule["op"]
        threshold = rule["threshold"]

        if op == "==" and current_value == threshold:
            is_fired = True
        elif op == ">" and isinstance(current_value, (int, float)) and current_value > threshold:
            is_fired = True
        elif op == "<" and isinstance(current_value, (int, float)) and current_value < threshold:
            is_fired = True

        if is_fired:
            alert_payload = {
                "alert_name": alert_name,
                "severity": rule["severity"],
                "observed_value": current_value,
                "threshold": threshold,
                "environment": self.settings.environment,
                "fired_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            logger.critical(f"ALERT FIRED [{alert_name}]: {current_value} {op} {threshold}", error_category="ALERT_TRIGGERED")
            return alert_payload

        return None
