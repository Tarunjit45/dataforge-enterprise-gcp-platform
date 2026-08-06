"""File management utility class scaffolding."""

from pathlib import Path
from typing import List


class FileUtilsScaffold:
    """Scaffold for local and staged file operations."""

    @staticmethod
    def ensure_directory_exists(directory_path: Path) -> bool:
        """Utility signature: Ensure directory path exists.

        Args:
            directory_path: Target directory path.

        Returns:
            bool: True if created or exists.
        """
        directory_path.mkdir(parents=True, exist_ok=True)
        return True

    @staticmethod
    def list_files_by_extension(directory_path: Path, extension: str) -> List[Path]:
        """Utility signature: List files matching extension.

        Args:
            directory_path: Search directory.
            extension: Extension filter (e.g. '.parquet', '.json').

        Returns:
            List[Path]: Matching file paths.
        """
        if not directory_path.exists():
            return []
        return list(directory_path.glob(f"*{extension}"))
