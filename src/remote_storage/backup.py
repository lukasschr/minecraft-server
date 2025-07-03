import shutil
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_backup(src_dir: Path, dest_dir: Path, name: str) -> Path:
    """
    Create a ZIP backup archive from a source directory.

    This function creates a ZIP archive of the given `src_dir` and saves it
    in `dest_dir` with the provided `name`. If `dest_dir` does not exist,
    it will be created, including all necessary parent directories.

    Args:
        src_dir (Path): Path to the directory to back up.
        dest_dir (Path): Path to the directory where the archive will be stored.
        name (str): Base name (without extension) for the resulting ZIP archive.

    Returns:
        Path: Path to the created ZIP archive.
    """
    try:
        # Ensure the destination directory exists
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Create the ZIP archive
        archive_path = shutil.make_archive(
            base_name=str(dest_dir / name),
            format="zip",
            root_dir=str(src_dir)
        )
        
        logger.info(f"Backup created successfully at '{archive_path}'.")
        return Path(archive_path)
    
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise