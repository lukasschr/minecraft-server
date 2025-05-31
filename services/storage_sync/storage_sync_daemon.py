from remote_storages import OCIBucket
from croniter import croniter
from datetime import datetime
from pathlib import Path
from threading import Event
import signal
import logging


def run_daemon(remote_storage, cron: str = "*/10 * * * *"):
    """Runs the sync daemon that executes syncs on a cron schedule."""
    shutdown_event = Event()

    remote_storage.sync()
    next_run = croniter(cron, datetime.now()).get_next(datetime)

    def on_exit(signum, frame):
        logging.info("🛑 Shutdown signal received. Running final sync...")
        remote_storage.sync()
        shutdown_event.set()

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)
    logging.info("🔄 Sync daemon started.")

    while not shutdown_event.is_set():
        if datetime.now() >= next_run:
            remote_storage.sync()
            next_run = croniter(cron, datetime.now()).get_next(datetime)
        shutdown_event.wait(timeout=5)

    logging.info("🛑 Sync daemon stopped.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s]: %(message)s",
    )

    remote_storage = OCIBucket(
        config_file=Path(".oci/config"),
        key_file=Path(".oci/key.pem"),
        bucket_name="minecraft-server-data",
        bucket_namespace="frovort8qllg",
        sync_dir=Path("/mnt/pufferpanel")
    )
    
    run_daemon(remote_storage)