"""Warehouse Load Metadata & Lineage Models."""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class WarehouseLoadMetadata(BaseModel):
    """Metadata tracking Gold Warehouse execution, data quality, and lineage."""

    batch_id: str = Field(..., description="Unique ETL batch ID")
    source_execution_id: str = Field(..., description="Phase 7 source pipeline execution ID")
    source_manifest: str = Field(..., description="URI of the processed source manifest file")
    data_quality_score: float = Field(..., description="Data Quality score percentage computed by Phase 7 DQ framework")
    records_read: int = Field(default=0, ge=0, description="Total Silver records read")
    records_inserted: int = Field(default=0, ge=0, description="Total records inserted into Gold")
    records_updated: int = Field(default=0, ge=0, description="Total records updated (MERGE/SCD)")
    records_rejected: int = Field(default=0, ge=0, description="Total records rejected due to DQ score threshold")
    load_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when load completed in UTC",
    )
    dataset_id: str = Field(default="gold_analytics", description="Target BigQuery dataset")
    table_id: str = Field(default="fact_taxi_trips", description="Target BigQuery table")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize metadata object to Python dictionary."""
        return {
            "batch_id": self.batch_id,
            "source_execution_id": self.source_execution_id,
            "source_manifest": self.source_manifest,
            "data_quality_score": self.data_quality_score,
            "records_read": self.records_read,
            "records_inserted": self.records_inserted,
            "records_updated": self.records_updated,
            "records_rejected": self.records_rejected,
            "load_timestamp": self.load_timestamp.isoformat(),
            "dataset_id": self.dataset_id,
            "table_id": self.table_id,
        }
