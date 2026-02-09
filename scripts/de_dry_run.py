"""
DE dry_run (count_first): build a plan, no DE execution yet.

Run (windows):
    python scripts/de_dry_run.py config/config.yaml
"""

from __future__ import annotations

import sys
from pathlib import Path


from rnaseq_native.paths import project_root
from rnaseq_native.config import load_config_yaml


def main(argv: list[str]) -> int:
    cfg_path = Path(argv[1]) if len(
        argv) > 1 else project_root() / "config" / "config.yaml"
    cfg = load_config_yaml(cfg_path)

    # For now: just print we can read the config and print the two input paths.
    start_from = cfg.get("pipeline", {}).get("start_from", None)
    inputs = cfg.get("inputs", {})

    print(f"Config: {cfg_path}")
    print(f"pipeline.start_from: {start_from}")
    print(f"inputs.samples: {inputs.get('samples')}")
    print(f"inputs.counts: {inputs.get('counts')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
