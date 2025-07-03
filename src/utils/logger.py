import logging
import logging.config
from pathlib import Path

from src.utils.reader import read_yaml


DEFAULT_CFG_FILE = Path("logging_config.yaml")
FALLBACK_LEVEL = logging.INFO
FALLBACK_FMT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

_is_configured = False


def _ensure_log_dirs_from_dictconfig(cfg: dict):
    """
    Ensure that all directories for file-based log handlers exist.

    Args:
        cfg (dict): Dictionary-based logging configuration, as used by `dictConfig`.
    """
    handlers = cfg.get('handlers', {})
    for handler_name, handler_conf in handlers.items():
        filename = handler_conf.get('filename')
        if filename:
            log_file = Path(filename)
            log_dir = log_file.parent
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise


def setup_logging(
    config_file: Path = DEFAULT_CFG_FILE,
    fallback_level: int = FALLBACK_LEVEL,
    fallback_fmt: str = FALLBACK_FMT
) -> None:
    """Configure logging using a YAML config file or fallback to basic logging.

    If a configuration file exists, it will be loaded and applied using `dictConfig`.
    Otherwise, a basic logging setup is used.

    Args:
        config_file (Path): Path to YAML logging configuration file.
        fallback_level (int): Logging level used if config file is missing.
        fallback_fmt (str): Log format used if config file is missing.
    """
    global _is_configured
    if _is_configured:
        return
    
    cfg_path = Path(config_file)
    if cfg_path.exists():
        cfg = read_yaml(yaml_file=cfg_path)
        _ensure_log_dirs_from_dictconfig(cfg)
        logging.config.dictConfig(cfg)
    else:
        logging.basicConfig(
            level=fallback_level,
            format=fallback_fmt
        )

    _is_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Retrieve a named logger, initializing logging if not already configured.

    Args:
        name (str): The name of the logger to retrieve (typically `__name__`).

    Returns:
        logging.Logger: Configured logger instance.
    """
    if not _is_configured:
        setup_logging()
    return logging.getLogger(name)