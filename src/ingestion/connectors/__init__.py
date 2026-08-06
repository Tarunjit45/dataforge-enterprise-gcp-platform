"""Ingestion connectors package."""

from src.ingestion.connectors.http import HTTPConnector
from src.ingestion.connectors.nyc_taxi import NYCTaxiConnector

__all__ = ["HTTPConnector", "NYCTaxiConnector"]
