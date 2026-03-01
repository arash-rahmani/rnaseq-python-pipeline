from __future__ import annotations
from pathlib import Path


def project_root() -> Path:
    """Locate repo root by finding a directory that contains 'src' and 'scripts'."""
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "src").is_dir() and (parent / "scripts").is_dir():
            return parent
        raise RuntimeError(
            "Could not locate project root (src/ and scripts/ not found)")
