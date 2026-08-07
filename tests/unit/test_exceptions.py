"""Unit tests for custom exception hierarchy."""

import pytest

from src.common.exceptions.base import (
    CloudStorageError,
    ConfigurationError,
    MigrationError,
    PipelineError,
    PlatformError,
    QualityCheckError,
    ValidationError,
)


@pytest.mark.unit
def test_platform_error_formatting():
    """Verify base PlatformError string representation."""
    err = PlatformError("Base error", details="Additional info")
    assert str(err) == "Base error | Details: Additional info"


@pytest.mark.unit
def test_derived_exceptions():
    """Verify inheritance of derived exceptions."""
    assert issubclass(ConfigurationError, PlatformError)
    assert issubclass(ValidationError, PlatformError)
    assert issubclass(MigrationError, PlatformError)
    assert issubclass(PipelineError, PlatformError)
    assert issubclass(QualityCheckError, PlatformError)
    assert issubclass(CloudStorageError, PlatformError)
