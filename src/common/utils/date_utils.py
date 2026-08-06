"""Date and partition formatting utility scaffolding."""

from datetime import datetime, timezone


class DateUtilsScaffold:
    """Scaffold for UTC date partition path formatting."""

    @staticmethod
    def get_current_utc_partition() -> str:
        """Utility signature: Return date string formatted as YYYY/MM/DD for partition paths.

        Returns:
            str: Date partition path string.
        """
        now = datetime.now(timezone.utc)
        return now.strftime("%Y/%m/%d")
