from pathlib import Path
from typing import Dict, Any

import yaml # type: ignore

def read_yaml(yaml_file: Path) -> Dict[str, Any]:
    """
    Load a YAML configuration file into a dictionary.

    This function reads the given file as UTF-8 text, parses it as YAML,
    and returns the resulting mapping.

    Args:
        config_file: Path to the YAML configuration file.
    
    Returns:
        Dict[str, Any]: Parsed configuration data.
    """
    cfg = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
    return cfg