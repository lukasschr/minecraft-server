import signal
from datetime import datetime
from pathlib import Path
from threading import Event

from croniter import croniter # type: ignore

from src.core.models import RemoteStorage
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Daemon:
    """Periodic sync daemon for synchronizing a local directory with remote storage.

    This daemon regularly syncs a local directory with any storage backend that
    implements the RemoteStorage interface (e.g., cloud buckets, FTP, S3, OCI).
    """
    def __init__(
            self, 
            remote_storage: RemoteStorage, 
            cron: str, 
            sync_dir=Path("/mnt/pufferpanel")
    ) -> None:
        """
        Initialize the sync daemon.

        Args:
            remote_storage (RemoteStorage): Remote storage backend for syncing.
            cron (str): Cron expression defining sync intervals.
            sync_dir (Path): Local directory to synchronize.
        """
        self.remote_storage = remote_storage
        self.cron = cron
        self.sync_dir = Path(sync_dir)
        self.shutdown_event = Event()

    def _sync_bootstrap(self) -> None:
        recoverfile = self.sync_dir / ".recoverfile"
        markerfile = self.sync_dir / ".sync_bootstrap_complete"

        if markerfile.exists():
            logger.info(f"Sync bootstrap marker present: skipping bootstrap.")
            return
        
        if recoverfile.exists():
            logger.info(f"Recovery detected (recoverfile present). Deleting all remote and uploading local files...")
            self.remote_storage.delete_all()
            recoverfile.unlink()
            self.remote_storage.upload_all(src_dir=self.sync_dir)
            logger.info(f"Recovery upload to remote storage completed successfully.")
        else:
            try:
                logger.info(f"Performing initial download from remote storage.")
                self.remote_storage.download_all(download_dir=self.sync_dir)
                logger.info(f"Initial remote download successful.")
            except Exception as e:
                logger.error(f"Initial remote download failed: {e}")
                raise

        with open(markerfile, "w") as marker:
            marker.write("1")
        logger.info(f"Bootstrap marker file created at {markerfile}.")


    def run(self):
        """
        Start the sync daemon loop.

        Handles signal termination, initial bootstrap, and cron-based syncing.
        Syncs will occur according to the cron schedule until shutdown is triggered.
        """
        logger.info(f"Starting sync daemon.")
        
        # Run Bootstrap
        try:
            self._sync_bootstrap()
        except Exception:
            logger.error(f"Sync daemon aborted due to bootstrap failure.")
            return

        # Signal handler for graceful shutdown
        def on_exit(signum, frame):
            logger.info(f"Shutdown signal {signum} received. Performing final sync...")
            try:
                self.remote_storage.sync(sync_dir=self.sync_dir)
                logger.info(f"Final sync completed successfully.")
            except Exception as e:
                logger.error(f"Final sync failed: {e}")
            self.shutdown_event.set()

        signal.signal(signal.SIGINT, on_exit)
        signal.signal(signal.SIGTERM, on_exit)
    
        next_run = croniter(self.cron, datetime.now()).get_next(datetime)
        logger.info(f"Autosync enabled. Next sync scheduled at {next_run.strftime('%Y-%m-%d %H:%M:%S')}.")

        try:
            while not self.shutdown_event.is_set():
                now = datetime.now()
                if now >= next_run:
                    try:
                        self.remote_storage.sync(sync_dir=self.sync_dir)
                        logger.info(f"Sync completed successfully.")
                    except Exception as e:
                        logger.error(f"Sync failed: {e}")
                    next_run = croniter(self.cron, now).get_next(datetime)
                self.shutdown_event.wait(timeout=2)
        except Exception as e:
            logger.error(f"Sync daemon aborted due to unexpected error: {e}")
        finally:
            logger.info(f"Sync daemon stopped.")
