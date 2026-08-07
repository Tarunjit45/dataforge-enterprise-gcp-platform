"""Manifest-driven Bronze Data Reader for PySpark."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from pyspark.sql import DataFrame, SparkSession

from src.common.exceptions.base import ValidationError
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


class BronzeReader:
    """Reads Bronze payloads using manifest.json definitions."""

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def read_manifest(self, manifest_path: Path) -> Dict:
        """Read and parse manifest.json payload.

        Args:
            manifest_path: Path to local or staged manifest.json file.

        Returns:
            Dict: Manifest key-value payload.
        """
        if not manifest_path.exists():
            raise ValidationError(f"Manifest file missing at path: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        logger.info(f"Loaded manifest for execution ID: {manifest.get('execution_id')}")
        return manifest

    def read_bronze_dataset(
        self,
        payload_uri: str,
        columns: Optional[List[str]] = None,
    ) -> DataFrame:
        """Load Parquet payload specified in manifest into a PySpark DataFrame.

        Applies column pruning if columns list is provided.

        Args:
            payload_uri: Path or GCS URI to Parquet dataset.
            columns: Optional list of columns to select (column pruning).

        Returns:
            DataFrame: Loaded PySpark DataFrame.
        """
        logger.info(f"Loading Bronze Parquet payload from: {payload_uri}")
        df = self.spark.read.parquet(payload_uri)

        if columns:
            existing_cols = [c for c in columns if c in df.columns]
            df = df.select(*existing_cols)

        logger.info(f"Bronze dataset loaded successfully. Initial Schema Fields: {len(df.columns)}")
        return df
