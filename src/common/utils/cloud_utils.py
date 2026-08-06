"""Cloud storage utility scaffolding."""


class CloudStorageUtilsScaffold:
    """Scaffold for GCS bucket and URI path parsing operations."""

    @staticmethod
    def parse_gcs_uri(gcs_uri: str) -> tuple[str, str]:
        """Utility signature: Deconstruct GCS URI into bucket and object key.

        Args:
            gcs_uri: Full URI (e.g. 'gs://bucket-name/path/to/object')

        Returns:
            tuple[str, str]: (bucket_name, blob_path)
        """
        clean_uri = gcs_uri.replace("gs://", "")
        parts = clean_uri.split("/", 1)
        bucket_name = parts[0]
        blob_path = parts[1] if len(parts) > 1 else ""
        return bucket_name, blob_path
