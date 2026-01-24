from __future__ import annotations

import sys
from pathlib import Path


def usage() -> str:
    return (
        "Usage:\n"
        "  python scripts/print_samples.py <path/to/samples.tsv> [--strict]\n"
        "  python scripts/print_samples.py <path/to/config.yaml> [--strict]\n"

    )


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(usage())
        return 2

    # Make src/ importable when running this script directly
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))

    # Import AFTER sys.path fix (and inside main so VSCode won't move it)
    from rnaseq_native.config import load_config_yaml
    from rnaseq_native.io import load_samples_tsv

    target = Path(argv[1])
    strict_override = "--strict" in argv[2:]

    # If user passes YAML, read config -> resolve samples path + strict paths
    if target.suffix.lower() in {".yaml", ".yml"}:
        cfg = load_config_yaml(target)

        samples_tsv = cfg.get("samples_tsv")
        if not samples_tsv:
            raise ValueError(
                "Config must contain 'samples_tsv' (path to samples.tsv).")

        # samples_tsv is relative to repo rot typically; resolve to config file Location
        samples_path = (target.parent / samples_tsv).resolve()

        strict_cfg = bool(cfg.get("strict_paths", False))
        strict = strict_cfg or strict_override

    else:
        # Otherwise treat input as tsv
        samples_path = target
        strict = strict_override

    df = load_samples_tsv(samples_path, strict_path=strict)

    print(f"Samples file: {samples_path}")
    print(f"Rows: {len(df)}")
    print(f"Conditions: {sorted(df['condition'].unique().tolist())}")
    print(f"Trees: {sorted(df['tree'].unique().tolist())}")
    print("\nCounts per condition:")
    print(df["condition"].value_counts().to_string())

    print("\nSamples:")
    for s in df["sample"].tolist():
        print(f" - {s}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
