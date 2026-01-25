from __future__ import annotations

import sys
from pathlib import Path

from rnaseq_native.config import load_config_yaml
from rnaseq_native.io import load_samples_tsv
from rnaseq_native.qc import FastpQCConfig, fastp_command


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python scripts/qc_dry_run.py <config/config.yaml")
        return 2

    cfg_path = Path(argv[1])
    cfg = load_config_yaml(cfg_path)

    samples_tsv = cfg.get("samples_tsv")
    if not samples_tsv:
        raise ValueError("Config must contain 'samples_tsv'.")

    samples_path = (cfg_path.parent / samples_tsv).resolve()
    strict = bool(cfg.get("strict_path", False))
    df = load_samples_tsv(samples_path, strict_path=strict)

    qc_cfg = cfg.get("qc", {})
    outdir = qc_cfg.get("outdir", "results/qc")

    fastp_cfg = qc_cfg.get("fastp", {})
    threads = int(fastp_cfg.get("threads", 4))

    print(f"QC outdir: {outdir}")
    print(f"fastp threads: {threads}\n")

    for _, row in df.iterrows():
        cmd = fastp_command(
            sample=row["sample"],
            r1=row["r1"],
            r2=row["r2"],
            outdir=outdir,
            cfg=FastpQCConfig(threads=threads),
        )
        print(" ".join(cmd))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
