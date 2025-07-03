import subprocess
import logging
from pathlib import Path

from src.core.models import RemoteStorage
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OCIBucket(RemoteStorage):
    """Handles OCI Object Storage bucket operations using the OCI CLI."""

    def __init__(
            self,
            config_file: Path,
            key_file: Path,
            bucket_name: str,
            bucket_namespace: str
    ) -> None:
        """
        Initialize the OCI bucket handler.

        Args:
            config_file (Path): Path to the OCI CLI configuration file.
            key_file (Path): Path to the OCI private key file.
            bucket_name (str): The name of the OCI bucket.
            bucket_namespace (str): The OCI namespace the bucket belongs to.
        """
        self.config_file = config_file
        self.key_file = key_file
        self.bucket_name = bucket_name
        self.bucket_namespace = bucket_namespace
        
        logger.debug(f"Initializing OCIBucket with config: {config_file}")
        self._validate_oci_setup()

    def download_all(self, download_dir: Path) -> None:
        """
        Download all objects from the OCI bucket to a local directory.

        Args:
            download_dir (Path): Local path to store downloaded objects.
        """
        logger.info(f"Downloading all objects from OCI bucket '{self.bucket_name}' to '{download_dir}'")
        try:
            subprocess.run([
                "oci", "os", "object", "bulk-download",
                "--bucket-name", self.bucket_name,
                "--namespace", self.bucket_namespace,
                "--download-dir", str(download_dir),
                "--overwrite",
                "--config-file", str(self.config_file),
            ], check=True)
            logger.info("Download completed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Download from OCI bucket failed: {e}")
            raise
    
    def delete_all(self) -> None:
        """
        Delete all objects in the OCI bucket.
        """
        logger.warning(f"Deleting all objects from OCI bucket '{self.bucket_name}'")
        try:
            subprocess.run([
                "oci", "os", "object", "bulk-delete",
                "--bucket-name", self.bucket_name,
                "--namespace", self.bucket_namespace,
                "--force",
                "--config-file", str(self.config_file),
            ], check=True)
            logger.info("All objects deleted successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Deletion in OCI bucket failed: {e}")
            raise

    def upload_all(self, src_dir: Path) -> None:
        """
        Upload all files from a local directory to the OCI bucket.

        Args:
            src_dir (Path): Local path containing files to upload.
        """
        logger.info(f"Uploading all files from '{src_dir}' to OCI bucket '{self.bucket_name}'")
        try:
            subprocess.run([
                'oci', 'os', 'object', 'bulk-upload',
                '--bucket-name', self.bucket_name,
                '--namespace', self.bucket_namespace,
                '--src-dir', str(src_dir),
                '--overwrite',
                '--config-file', str(self.config_file)
            ], check=True)
            logger.info("Upload completed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Upload to OCI bucket failed: {e}")
            raise
    
    def sync(self, sync_dir: Path) -> None:
        """
        Synchronize a local directory with the OCI bucket.

        Deletes remote files that do not exist locally.

        Args:
            sync_dir (Path): Path to the local directory to sync.
        """
        logger.info(f"Starting sync from '{sync_dir}' to OCI bucket '{self.bucket_name}'")
        try:
            subprocess.run([
                'oci', 'os', 'object', 'sync',
                '--bucket-name', self.bucket_name,
                '--namespace', self.bucket_namespace,
                '--src-dir', str(sync_dir),
                '--delete',
                '--config-file', str(self.config_file)
            ], check=True)
            logger.info("Sync completed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Sync with OCI bucket failed: {e}")
            raise

    def _validate_oci_setup(self) -> None:
        """
        Validate the OCI CLI setup and required files.

        Ensures that the config and key files exist and have correct permissions.
        """
        try:
            for setup_file in [self.config_file, self.key_file]:
                if not setup_file.exists():
                    raise FileNotFoundError(f"Missing required file: {setup_file}")
                logger.debug(f"Repairing file permissions for '{setup_file}'")
                subprocess.run([
                    "oci", "setup", "repair-file-permissions",
                    "--file", str(setup_file)
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info("OCI CLI setup validated successfully.")
        except FileNotFoundError as e:
            logger.critical(f"Missing file: {e}")
            raise
        except Exception as e:
            logger.critical(f"OCI setup validation failed: {e}")
            raise