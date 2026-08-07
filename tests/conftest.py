"""Global PyTest configuration and shared test fixtures."""

import os

import pytest

from src.common.config.settings import PlatformConfig, get_settings


@pytest.fixture(autouse=True)
def set_test_env():
    """Ensure test environment variable is set during testing."""
    os.environ["ENVIRONMENT"] = "test"
    yield
    os.environ["ENVIRONMENT"] = "test"


@pytest.fixture
def mock_config() -> PlatformConfig:
    """Fixture providing a mock PlatformConfig instance."""
    return PlatformConfig(
        environment="test",
        gcp_project_id="test-project-123",
        region="us-central1",
        log_level="DEBUG",
        raw_bucket="gs://test-raw-bronze",
        processed_bucket="gs://test-processed-silver",
        quarantine_bucket="gs://test-quarantine",
        bigquery_dataset="test_analytics",
    )
