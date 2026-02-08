from __future__ import annotations

import json
import sys
from pathlib import Path

from rnaseq_native.config import load_config_yaml
from rnaseq_native.io import load_samples_tsv
from rnaseq_native.counts import load_count_matrix, validate_count_matrix, align_counts_and_samples
from rnaseq_native.paths import project_root


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python scripts/counts_validate.py <config/config.yaml")
        return 2

    cfg_path = Path(argv[1])
    cfg = load_config_yaml(cfg_path)

    mode = cfg.get("pipline", {}).get("start_from", "counts")
    if mode != "counts":
        print(f"Skipping counts validation (start_from={mode}).")
        return 0

    inputs = cfg.get("inputs", {})
    counts_rel = inputs.get("counts")
    samples_rel = inputs.get("samples")

    if not counts_rel:
        raise ValueError("config.yaml missing: inputs.counts")
    if not samples_rel:
        raise ValueError("config.yaml missing: inputs.samples")

    counts_path = (cfg_path.parent / counts_rel).resolve()
    samples_path = (cfg_path.parent / samples_rel).resolve()

    # counts_first metadata does NOT require FASTQ columns
    meta = load_samples_tsv(samples_path, require_fastq=False)

    counts = load_count_matrix(counts_path)
    validate_count_matrix(counts)

    counts2, meta2 = align_counts_and_samples(counts, meta)

    # Simply summary
    sample_names = list(counts2.columns[1:])
    lib_sizes = counts2[sample_names].apply(
        lambda s: s.astype(int).sum()).to_dict()

    outdirs = cfg.get("outdir", {})
    outdir = Path(project_root() / outdirs.get("analysis",
                  "results/analysis")).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    summary = {
        "mode": mode,
        "counts_path": str(counts_path),
        "samples_path": str(samples_path),
        "n_genes": int(counts2.shape[0]),
        "n_samples": int(len(sample_names)),
        "samples": sample_names,
        "library_sizes": lib_sizes,
    }

    out_json = outdir / "validated_inputs.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Validated counts + metadata")
    print(f"Wrote: {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
