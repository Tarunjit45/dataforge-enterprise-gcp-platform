"""Validation utility class scaffolding."""

from typing import Any, Dict


class ValidationUtilsScaffold:
    """Scaffold for generic data and schema validation functions."""

    @staticmethod
    def validate_dict_keys(payload: Dict[str, Any], required_keys: list[str]) -> bool:
        """Utility signature: Validate mandatory keys presence.

        Args:
            payload: Input dictionary payload.
            required_keys: List of required keys.

        Returns:
            bool: True if all keys exist.
        """
        return all(key in payload for key in required_keys)
