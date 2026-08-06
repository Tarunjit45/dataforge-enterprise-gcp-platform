"""Data Checksum & SHA256 Validation Engine."""

import hashlib
import json
from typing import Any, Dict, List, Optional

from src.common.config.settings import get_settings
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


class ChecksumEngine:
    """Computes SHA256 / MD5 hash signatures per table and batch block for data validation."""

    def __init__(self):
        self.settings = get_settings()

    def compute_row_hash(self, row_dict: Dict[str, Any], excluded_keys: Optional[List[str]] = None) -> str:
        """Compute SHA256 checksum string for a single data record dictionary.

        Args:
            row_dict: Key-value dictionary representing a single database row.
            excluded_keys: Optional list of keys to ignore during hash computation.

        Returns:
            str: SHA256 hex digest.
        """
        excluded = set(excluded_keys or [])
        sorted_pairs = []
        for k in sorted(row_dict.keys()):
            if k not in excluded:
                val = row_dict[k]
                val_str = str(val) if val is not None else ""
                sorted_pairs.append(f"{k}:{val_str}")

        payload = "|".join(sorted_pairs)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def compute_table_checksum(self, rows: List[Dict[str, Any]], excluded_keys: Optional[List[str]] = None) -> str:
        """Compute aggregate SHA256 checksum for a collection of table row dictionaries.

        Args:
            rows: List of row dictionaries.
            excluded_keys: Optional list of column names to ignore.

        Returns:
            str: Combined SHA256 hex digest representing table dataset state.
        """
        hasher = hashlib.sha256()
        for row in rows:
            row_hash = self.compute_row_hash(row, excluded_keys=excluded_keys)
            hasher.update(row_hash.encode("utf-8"))
        digest = hasher.hexdigest()
        logger.info(f"Computed table checksum across {len(rows)} records: {digest}")
        return digest

    def compare_checksums(self, source_hash: str, target_hash: str) -> bool:
        """Compare source and target checksum strings.

        Args:
            source_hash: Source SHA256 digest string.
            target_hash: Target SHA256 digest string.

        Returns:
            bool: True if checksum digests match exactly.
        """
        match = source_hash == target_hash
        if match:
            logger.info(f"Checksum comparison MATCHED: {source_hash}")
        else:
            logger.warning(f"Checksum comparison MISMATCH! Source: {source_hash} vs Target: {target_hash}")
        return match
