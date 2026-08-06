"""Unit tests for utility scaffolding."""

import pytest
from src.common.utils.cloud_utils import CloudStorageUtilsScaffold
from src.common.utils.date_utils import DateUtilsScaffold
from src.common.utils.retry_utils import retry_on_exception
from src.common.utils.validation_utils import ValidationUtilsScaffold


@pytest.mark.unit
def test_parse_gcs_uri():
    """Verify parse_gcs_uri utility signature."""
    bucket, path = CloudStorageUtilsScaffold.parse_gcs_uri("gs://my-bucket/data/file.parquet")
    assert bucket == "my-bucket"
    assert path == "data/file.parquet"


@pytest.mark.unit
def test_validate_dict_keys():
    """Verify validate_dict_keys utility signature."""
    payload = {"a": 1, "b": 2}
    assert ValidationUtilsScaffold.validate_dict_keys(payload, ["a", "b"]) is True
    assert ValidationUtilsScaffold.validate_dict_keys(payload, ["a", "c"]) is False


@pytest.mark.unit
def test_utc_partition():
    """Verify UTC partition string format."""
    partition = DateUtilsScaffold.get_current_utc_partition()
    assert len(partition.split("/")) == 3


@pytest.mark.unit
def test_retry_decorator():
    """Verify retry decorator behavior."""
    attempts = 0

    @retry_on_exception(max_retries=2, backoff_factor=0.1)
    def flaky_func():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ValueError("Temporary failure")
        return "success"

    result = flaky_func()
    assert result == "success"
    assert attempts == 2
