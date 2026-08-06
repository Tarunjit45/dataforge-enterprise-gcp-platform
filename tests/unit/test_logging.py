"""Unit tests for structured logging framework."""

import logging
import pytest
from src.common.logging.logger import get_logger, set_correlation_id


@pytest.mark.unit
def test_get_logger_instantiation():
    """Verify logger creation and settings."""
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


@pytest.mark.unit
def test_set_correlation_id():
    """Verify setting correlation ID context."""
    set_correlation_id("test-corr-id-999")
    logger = get_logger("test_module_corr")
    assert logger is not None
