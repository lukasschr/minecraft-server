from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
import logging


class RemoteStorage(ABC):
    """Abstract base class for remote storages."""

    @abstractmethod
    def sync(self) -> None:
        """Synchronize local directory with the remote storage."""
        pass


class OCIBucket(RemoteStorage):

    def __init__(self, config_file: Path, key_file: Path,
                 bucket_name: str, bucket_namespace: str, sync_dir: Path):
        super().__init__()

        self.config_file = config_file
        self.key_file = key_file
        self.bucket_name = bucket_name
        self.bucket_namespace = bucket_namespace
        self.sync_dir = sync_dir

        self._validate_oci_setup()
    
    def sync(self) -> None:
        try:
            subprocess.run([
                'oci', 'os', 'object', 'sync',
                '--bucket-name', self.bucket_name,
                '--namespace', self.bucket_namespace,
                '--src-dir', str(self.sync_dir),
                '--delete',
                '--config-file', str(self.config_file)
            ], check=True)
            logging.info("✅ Sync with OCI bucket completed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Sync with OCI bucket failed: {e}")

    def _validate_oci_setup(self) -> None:
        try:
            for setup_file in [self.config_file, self.key_file]:
                if not setup_file.exists():
                    raise FileNotFoundError(f"Missing: {setup_file}")
                
                subprocess.run([
                    "oci", "setup", "repair-file-permissions", 
                    "--file", str(setup_file)
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError as e:
            logging.critical(f"❌ Configuration missing: {e}")
            raise
        except Exception as e:
            logging.critical(f"❌ OCI setup validation failed: {e}")
            raise