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
from rnaseq_native.io import load_samples_tsv
from rnaseq_native.counts import load_count_matrix



def main(argv: list[str]) -> int:
    cfg_path = Path(argv[1]) if len(
        argv) > 1 else project_root() / "config" / "config.yaml"
    cfg = load_config_yaml(cfg_path)

    # For now: just print we can read the config and print the two input paths.
    start_from = cfg.get("pipeline", {}).get("start_from", None)
    inputs = cfg.get("inputs", {})

    # Resolve input paths relative to config file location
    samples_rel = inputs.get("samples")
    counts_rel = inputs.get("counts")

    samples_path = (cfg_path.parent / samples_rel).resolve()
    counts_path = (cfg_path.parent / counts_rel).resolve()

    print(f"samples_path (resolved): {samples_path}")
    print(f"counts_path (resolved): {counts_path}")

    # Load samples.tsv (counts-first mode)
    samples_df = load_samples_tsv(samples_path, require_fastq=False)
    print(f"samples loaded: {samples_df.shape}")
    print(f"samples columns: {list(samples_df.columns)}")
    # Load count matrix
    counts_df = load_count_matrix(counts_path)

    print(f"counts loaded: {counts_df.shape}")
    print(f"counts columns (first 10): {list(counts_df.columns)[:10]}")

    print(f"Config: {cfg_path}")
    print(f"pipeline.start_from: {start_from}")
    print(f"inputs.samples: {inputs.get('samples')}")
    print(f"inputs.counts: {inputs.get('counts')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
