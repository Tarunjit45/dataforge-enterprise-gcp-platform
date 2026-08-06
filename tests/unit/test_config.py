"""Unit tests for centralized configuration loader."""

import os
import pytest
from src.common.config.settings import PlatformConfig, get_settings
from src.common.exceptions.base import ConfigurationError


@pytest.mark.unit
def test_platform_config_defaults():
    """Verify default values on PlatformConfig."""
    config = PlatformConfig()
    assert config.environment == "dev"
    assert config.region == "us-central1"


@pytest.mark.unit
def test_get_settings_environment_override(monkeypatch):
    """Verify get_settings loads test environment correctly."""
    get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "test")
    config = get_settings()
    assert config.environment == "test"


@pytest.mark.unit
def test_invalid_environment(monkeypatch):
    """Verify exception raised when invalid ENVIRONMENT set."""
    get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "invalid_env")
    with pytest.raises(ConfigurationError):
        get_settings()
