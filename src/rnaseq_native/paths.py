from __future__ import annotations
from pathlib import Path


def project_root() -> Path:
    # <repo>/scripts/*.py -> parents[1] is repo root
    return Path(__file__).resolve().parents[2]
