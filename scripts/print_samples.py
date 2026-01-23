from __future__ import annotations

import sys
from pathlib import Path

# Add project_root/src to import path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv: list[str]) -> int:
    from rnaseq_native.io import load_samples_tsv
    if len(argv) < 2:
        print(
            "Usage: python scripts/print_samples.py <path/to/samples.tsv> [--strict]")
        return 2
    samples_path = Path(argv[1])
    strict = "--strict" in argv[2:]

    df = load_samples_tsv(samples_path, strict_path=strict)

    print(f"Samples file: {samples_path}")
    print(f"Rows: {len(df)}")
    print(f"Conditions: {sorted(df['condition'].unique().tolist())}")
    print(f"Trees: {sorted(df['tree'].unique().tolist())}")
    print("\nCounts per condition:")
    print(df["condition"].value_counts().tolist())

    print("\nSamples:")
    for s in df["sample"].tolist():
        print(f" - {s}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
