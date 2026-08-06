"""Custom exception hierarchy.

Provides distinct, typed exceptions for data pipeline failures, storage errors,
configuration issues, quality check failures, and migration errors.
"""


class PlatformError(Exception):
    """Base exception for all GCP Enterprise Data Platform errors."""

    def __init__(self, message: str, details: str = ""):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(PlatformError):
    """Raised when environment or platform configuration is missing or invalid."""

    pass


class ValidationError(PlatformError):
    """Raised when schema validation or input payload verification fails."""

    pass


class MigrationError(PlatformError):
    """Raised during database migration processing or schema translation failures."""

    pass


class PipelineError(PlatformError):
    """Raised when an ETL pipeline or PySpark job execution encounters an error."""

    pass


class QualityCheckError(PlatformError):
    """Raised when data quality checks fail or quarantine threshold is exceeded."""

    pass


class CloudStorageError(PlatformError):
    """Raised when GCS or cloud storage operations fail."""

    pass
