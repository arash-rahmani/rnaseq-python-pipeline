from __future__ import annotations

from pathlib import Path
import pandas as pd


def load_count_matrix(path: str | Path) -> pd.DataFrame:
    """
    Load agen-level count matrix

    Expected shape:
      rows = genes
      columns = samples
    First column must be: Geneid
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Count matrix file not found: {path}")

    # Choose delimiter from file extension
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path, dtype=str)
    else:
        # Default to TSV for .tsv/.txt/anything else
        df = pd.read_csv(path, sep="\t", dtype=str)

    return df
