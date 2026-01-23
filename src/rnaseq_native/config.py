from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config_yaml(path: str | Path) -> dict[str, Any]:
    """
    Load a YAML configuration file and return it as a dictionary.

    Raises:
        FileNotFoundError: if config file does not exsist
        valueError: if YAML is emty or invalid
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        cfg = yaml.safe_load(file)

    if cfg is None:
        return {}

    if not isinstance(cfg, dict):
        raise ValueError(f"Config yaml must be mapping (top-level dict).")

    return cfg
