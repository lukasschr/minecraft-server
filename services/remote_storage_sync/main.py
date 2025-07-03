from pathlib import Path

from src.remote_storage.sync_daemon import Daemon
from src.utils.reader import read_yaml
from src.remote_storage.storage import OCIBucket


REMOTE_STORAGE = OCIBucket(
    config_file=Path(".oci/config"),
    key_file=Path(".oci/key.pem"),
    bucket_name="minecraft-server-data",
    bucket_namespace="frovort8qllg"
)


if __name__ == "__main__":
    config = read_yaml(yaml_file=Path("sync_daemon_config.yaml"))

    sync_daemon = Daemon(
        remote_storage=REMOTE_STORAGE,
        cron=config["cron"]
    )
    sync_daemon.run()