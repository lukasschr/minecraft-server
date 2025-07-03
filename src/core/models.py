from abc import ABC, abstractmethod
from pathlib import Path


class RemoteStorage(ABC):
    """Abstract base class for remote storage backends."""

    @abstractmethod
    def download_all(self, download_dir: Path) -> None:
        """
        Download all remote files into the specified local directory.

        Args:
            download_dir (Path): Path to the target local directory.
        """
        pass

    @abstractmethod
    def upload_all(self, src_dir: Path) -> None:
        """
        Upload all files from a local directory to the remote storage.

        Args:
            src_dir (Path): Path to the source directory containing files to upload.
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """
        Delete all content from the remote storage.

        Intended for full cleanup of the remote bucket or target location.
        """
        pass

    @abstractmethod
    def sync(self, sync_dir: Path) -> None:
        """
        Synchronize local directory with remote storage.

        This method should perform a two-way sync between the 
        given local directory and the remote storage.

        Args:
            sync_dir (Path): Path to the local directory to sync.
        """
        pass