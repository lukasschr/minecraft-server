import argparse
import tempfile
from pathlib import Path

from src.remote_storage.backup import create_backup
from src.remote_storage.storage import OCIBucket


REMOTE_STORAGE = OCIBucket(
    config_file=Path(".oci/config"),
    key_file=Path(".oci/key.pem"),
    bucket_name="minecraft-server-data",
    bucket_namespace="frovort8qllg"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--dest_dir", type=Path, required=True, help="Zielverzeichnis für das Backup")
    parser.add_argument("-n", "--name", type=str, required=True, help="Name des Backups")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    try:
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir = Path(temp_dir_obj.name)
    
        REMOTE_STORAGE.download_all(download_dir=temp_dir)

        create_backup(src_dir=temp_dir, dest_dir=args.dest_dir, name=args.name)
    
    finally:
        temp_dir_obj.cleanup()