from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED_GENE_COLUMN = "Geneid"



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


def validate_count_matrix(df: pd.DataFrame) -> None:
    """
    Validate the count matrix structure and vlues.
    
    Rules:
      - Must contian a first column named "Geneid
      - Gene IDs must be non-empty and unique
      - Sample columns must be numeric, integeer, non-negative
      - No missing values allowed
      """
    if df.shape[1] < 2:
        raise ValueError(
            "Count matrix must have at least 2 columns: Geneid + >=1 sample")

    if df.columns[0] != REQUIRED_GENE_COLUMN:
        raise ValueError(
            f"First comlumn must be '{REQUIRED_GENE_COLUMN}', but got '{df.columns[0]}'."

        )

    # Gene ID checks
    gene = df[REQUIRED_GENE_COLUMN].astype(str).str.strip()
    if (gene == "").any():
        raise ValueError("Count matrix contains empty Geneid values.")
    if gene.duplicated().any():
        dups = gene.loc[gene.duplicated()].unique().tolist()
        raise ValueError(f"Duplicate Geneid values found: {dups}")
