"""Enterprise Data Ingestion Framework package."""

from src.ingestion.base import BaseConnector, IngestionPayload, IngestionResult
from src.ingestion.connectors.http import HTTPConnector
from src.ingestion.connectors.nyc_taxi import NYCTaxiConnector
from src.ingestion.metadata import MetadataGenerator
from src.ingestion.pipeline import IngestionPipeline

__all__ = [
    "BaseConnector",
    "IngestionPayload",
    "IngestionResult",
    "HTTPConnector",
    "NYCTaxiConnector",
    "MetadataGenerator",
    "IngestionPipeline",
]
