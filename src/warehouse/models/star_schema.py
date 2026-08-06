"""Dimensional Star Schema Models & Entity Registry."""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class SCDType(str, Enum):
    """Slowly Changing Dimension Type designation."""

    NONE = "NONE"
    TYPE_1 = "TYPE_1"
    TYPE_2 = "TYPE_2"


class ColumnDefinition(BaseModel):
    """BigQuery column definition model."""

    name: str
    data_type: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_surrogate_key: bool = False
    is_business_key: bool = False
    scd_tracking: Optional[SCDType] = None
    description: str = ""


class DimensionModel(BaseModel):
    """Star Schema Dimension Table Model."""

    table_name: str
    schema_file: str
    scd_type: SCDType = SCDType.TYPE_2
    surrogate_key: str
    business_key: str
    columns: List[ColumnDefinition] = Field(default_factory=list)


class FactModel(BaseModel):
    """Star Schema Fact Table Model."""

    table_name: str
    schema_file: str
    partition_column: str
    cluster_columns: List[str]
    surrogate_key: str
    foreign_keys: Dict[str, str]  # fk_column -> referenced_dimension_table
    columns: List[ColumnDefinition] = Field(default_factory=list)


def get_star_schema_definition() -> Dict[str, Any]:
    """Retrieve full Star Schema architecture definition."""
    return {
        "dimensions": {
            "DIM_DATE": DimensionModel(
                table_name="DIM_DATE",
                schema_file="dim_date",
                scd_type=SCDType.NONE,
                surrogate_key="date_key",
                business_key="full_date",
            ),
            "DIM_VENDOR": DimensionModel(
                table_name="DIM_VENDOR",
                schema_file="dim_vendor",
                scd_type=SCDType.TYPE_2,
                surrogate_key="vendor_key",
                business_key="vendor_id",
            ),
            "DIM_PAYMENT_TYPE": DimensionModel(
                table_name="DIM_PAYMENT_TYPE",
                schema_file="dim_payment_type",
                scd_type=SCDType.TYPE_2,
                surrogate_key="payment_type_key",
                business_key="payment_type_id",
            ),
            "DIM_LOCATION": DimensionModel(
                table_name="DIM_LOCATION",
                schema_file="dim_location",
                scd_type=SCDType.TYPE_2,
                surrogate_key="location_key",
                business_key="location_id",
            ),
            "DIM_RATE_CODE": DimensionModel(
                table_name="DIM_RATE_CODE",
                schema_file="dim_rate_code",
                scd_type=SCDType.TYPE_2,
                surrogate_key="rate_code_key",
                business_key="rate_code_id",
            ),
            "DIM_CUSTOMER": DimensionModel(
                table_name="DIM_CUSTOMER",
                schema_file="dim_customer",
                scd_type=SCDType.TYPE_2,
                surrogate_key="customer_key",
                business_key="customer_id",
            ),
        },
        "facts": {
            "FACT_TAXI_TRIPS": FactModel(
                table_name="FACT_TAXI_TRIPS",
                schema_file="fact_trip",
                partition_column="trip_date",
                cluster_columns=["vendor_key", "payment_type_key", "pickup_location_key", "rate_code_key"],
                surrogate_key="trip_key",
                foreign_keys={
                    "vendor_key": "DIM_VENDOR",
                    "payment_type_key": "DIM_PAYMENT_TYPE",
                    "rate_code_key": "DIM_RATE_CODE",
                    "pickup_location_key": "DIM_LOCATION",
                    "dropoff_location_key": "DIM_LOCATION",
                    "customer_key": "DIM_CUSTOMER",
                    "pickup_date_key": "DIM_DATE",
                    "dropoff_date_key": "DIM_DATE",
                },
            )
        },
    }
