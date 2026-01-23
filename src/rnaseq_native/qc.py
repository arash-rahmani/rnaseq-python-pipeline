from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FastpQCConfig:
    threads: int = 4


def fastp_command(sample: str, r1: str, r2: str, outdir: str | Path, cfg: FastpQCConfig) -> list[str]:
    """
    Build a fastp command for paired-end reads.
    We return a list[str] so it can be safely used with subprocess later.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    html = outdir / f"{sample}.fastp.html"
    json = outdir / f"{sample}.fastp.json"
    out_r1 = outdir / f"{sample}.trimmed.R1.fastq.gz"
    out_r2 = outdir / f"{sample}.trimmed.R2.fastq.gz"

    return [
        "fastp",
        "-i", r1,
        "-I", r2,
        "-o", str(out_r1),
        "-O", str(out_r2),
        "-h", str(html),
        "-j", str(json),
        "-w", str(cfg.threads),
    ]
