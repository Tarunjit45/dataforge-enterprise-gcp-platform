"""Google Cloud Datastream & DMS CDC Configuration Manager."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from src.common.config.settings import get_settings
from src.common.logging.logger import get_logger

logger = get_logger(__name__)


class DatastreamCDCManager:
    """Manages Google Cloud Datastream CDC continuous replication streams from MySQL to AlloyDB."""

    def __init__(self, stream_id: str = "ds-mysql-to-alloydb"):
        self.settings = get_settings()
        self.stream_id = stream_id

    def generate_datastream_config(
        self,
        mysql_host: str = "10.0.0.5",
        mysql_port: int = 3306,
        mysql_user: str = "datastream_cdc",
        database_name: str = "production_db",
        alloydb_cluster_id: str = "alloydb-cluster-dev",
    ) -> Dict[str, Any]:
        """Generate Google Cloud Datastream Stream and Connection Profile configuration spec.

        Args:
            mysql_host: Source MySQL host IP/hostname.
            mysql_port: Source MySQL port.
            mysql_user: CDC replication user name.
            database_name: Source database to stream.
            alloydb_cluster_id: Target AlloyDB cluster ID.

        Returns:
            Dict[str, Any]: Complete Datastream stream specification payload.
        """
        logger.info(f"Generating Datastream CDC stream configuration for '{self.stream_id}'...")
        config = {
            "name": f"projects/{self.settings.gcp_project_id}/locations/{self.settings.region}/streams/{self.stream_id}",
            "display_name": f"Datastream CDC {database_name} -> {alloydb_cluster_id}",
            "source_config": {
                "source_connection_profile": f"projects/{self.settings.gcp_project_id}/locations/{self.settings.region}/connectionProfiles/cp-mysql-source",
                "mysql_source_config": {
                    "include_objects": {
                        "mysql_databases": [
                            {
                                "database": database_name,
                            }
                        ]
                    },
                    "cdc_method": {
                        "binlog_cdc_method": {}
                    },
                },
            },
            "destination_config": {
                "destination_connection_profile": f"projects/{self.settings.gcp_project_id}/locations/{self.settings.region}/connectionProfiles/cp-alloydb-target",
                "postgresql_destination_config": {
                    "schema": "public",
                },
            },
            "state": "RUNNING",
        }
        logger.info(f"Datastream stream config generated successfully for '{self.stream_id}'.")
        return config

    def save_cdc_config(self, config: Dict[str, Any], output_dir: str = ".") -> str:
        """Save Datastream JSON payload configuration to disk.

        Args:
            config: Datastream configuration dictionary.
            output_dir: Target output directory path.

        Returns:
            str: Path to saved datastream_config.json file.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        config_file = out_path / "datastream_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Saved Datastream CDC config to '{config_file.resolve()}'.")
        return str(config_file.resolve())
