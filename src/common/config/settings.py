"""Centralized environment-driven configuration loader.

Supports Dev, Test, and Prod environments without hardcoded business configuration.
"""

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

from src.common.exceptions.base import ConfigurationError


class PlatformConfig(BaseSettings):
    """Platform baseline environment configuration model."""

    environment: str = Field(default="dev", description="Execution environment (dev, test, prod)")
    gcp_project_id: str = Field(default="enterprise-data-dev", description="Target GCP Project ID")
    region: str = Field(default="us-central1", description="Target GCP Region")
    log_level: str = Field(default="INFO", description="Application logging level")
    raw_bucket: str = Field(default="", description="GCS Raw Landing Bucket URI")
    processed_bucket: str = Field(default="", description="GCS Processed Bucket URI")
    quarantine_bucket: str = Field(default="", description="GCS Quarantine Bucket URI")
    bigquery_dataset: str = Field(default="", description="BigQuery target dataset name")

    model_config = ConfigDict(
        env_prefix="PLATFORM_",
        case_sensitive=False,
        extra="ignore",
    )


def _get_config_path(env: str) -> Path:
    """Resolve configuration JSON file path for a given environment."""
    root_dir = Path(__file__).resolve().parents[3]
    return root_dir / "config" / "settings" / f"{env}.json"


@lru_cache(maxsize=1)
def get_settings() -> PlatformConfig:
    """Load and return environment settings with caching.

    Returns:
        PlatformConfig: Instantiated platform configuration instance.

    Raises:
        ConfigurationError: If environment file is invalid or missing.
    """
    env = os.getenv("ENVIRONMENT", "dev").lower()
    if env not in ("dev", "test", "prod"):
        raise ConfigurationError(f"Invalid ENVIRONMENT '{env}'. Must be one of: dev, test, prod.")

    config_file = _get_config_path(env)
    config_data: Dict[str, Any] = {}

    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            raise ConfigurationError(f"Failed to parse configuration file {config_file}: {e}") from e

    return PlatformConfig(**config_data)
