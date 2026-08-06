"""Centralized BigQuery client factory."""

from typing import Any

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

from src.common.config.settings import get_settings
from src.common.exceptions.base import PipelineError
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


def get_bigquery_client(project_id: str = None) -> Any:
    """Instantiate and return a Google BigQuery client.

    Args:
        project_id: Target GCP Project ID.

    Returns:
        Any: Authenticated BigQuery client.
    """
    if bigquery is None:
        raise PipelineError("google-cloud-bigquery library is not installed.")

    settings = get_settings()
    target_project = project_id or settings.gcp_project_id
    logger.info(f"Initializing BigQuery Client for Project ID: '{target_project}'")
    return bigquery.Client(project=target_project)
