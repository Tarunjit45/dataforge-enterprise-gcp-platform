"""Data Migration Framework Models & Metadata Definitions."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MigrationStatus(str, Enum):
    """Execution status for data migration tasks."""

    PENDING = "PENDING"
    ASSESSING = "ASSESSING"
    CONVERTING = "CONVERTING"
    EXTRACTING = "EXTRACTING"
    LOADING = "LOADING"
    VALIDATING = "VALIDATING"
    CDC_REPLICATING = "CDC_REPLICATING"
    CUTOVER_READY = "CUTOVER_READY"
    CUTOVER_SUCCESS = "CUTOVER_SUCCESS"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class ColumnMetadata(BaseModel):
    """Database column metadata model."""

    name: str
    data_type: str
    full_type: str = ""
    is_nullable: bool = True
    default_value: Optional[str] = None
    is_primary_key: bool = False
    is_auto_increment: bool = False
    character_maximum_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None


class IndexMetadata(BaseModel):
    """Database index metadata model."""

    index_name: str
    table_name: str
    columns: List[str]
    is_unique: bool = False
    index_type: str = "BTREE"


class ForeignKeyMetadata(BaseModel):
    """Database foreign key constraint metadata model."""

    constraint_name: str
    source_table: str
    source_column: str
    target_table: str
    target_column: str


class TableSchema(BaseModel):
    """Complete table schema definition model."""

    table_name: str
    storage_engine: str = "InnoDB"
    estimated_rows: int = 0
    size_bytes: int = 0
    columns: List[ColumnMetadata] = Field(default_factory=list)
    indexes: List[IndexMetadata] = Field(default_factory=list)
    foreign_keys: List[ForeignKeyMetadata] = Field(default_factory=list)


class DatabaseInventory(BaseModel):
    """Database assessment inventory model."""

    database_name: str
    tables: Dict[str, TableSchema] = Field(default_factory=dict)
    views: List[str] = Field(default_factory=list)
    total_tables: int = 0
    total_rows: int = 0
    total_size_bytes: int = 0
    unsupported_features: List[str] = Field(default_factory=list)
    compatibility_score: float = 100.0
    estimated_effort_hours: float = 0.0


class CheckpointRecord(BaseModel):
    """Data extraction & load checkpoint tracking model."""

    table_name: str
    last_processed_id: Optional[Any] = None
    rows_extracted: int = 0
    rows_loaded: int = 0
    is_completed: bool = False
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ValidationResult(BaseModel):
    """Migration validation comparison result model."""

    table_name: str
    source_row_count: int
    target_row_count: int
    row_count_match: bool
    source_checksum: str
    target_checksum: str
    checksum_match: bool
    sample_mismatches: int = 0
    foreign_key_orphans: int = 0
    is_passed: bool = False


class CutoverStatus(BaseModel):
    """Production cutover execution state model."""

    cutover_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    checklist_passed: bool = False
    maintenance_mode_active: bool = False
    final_sync_lag_seconds: float = 0.0
    application_switched: bool = False
    status: MigrationStatus = MigrationStatus.PENDING


class RollbackPlan(BaseModel):
    """Emergency migration rollback execution plan model."""

    plan_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trigger_reason: str
    target_tables_dropped: List[str] = Field(default_factory=list)
    snapshot_restored: Optional[str] = None
    dns_reverted: bool = False
    status: str = "READY"
