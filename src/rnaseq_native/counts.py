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
      - Must contain a first column named "Geneid
      - Gene IDs must be non-empty and unique
      - Sample columns must be numeric, integer, non-negative
      - No missing values allowed
      """
    if df.shape[1] < 2:
        raise ValueError(
            "Count matrix must have at least 2 columns: Geneid + >=1 sample")

    if df.columns[0] != REQUIRED_GENE_COLUMN:
        raise ValueError(
            f"First column must be '{REQUIRED_GENE_COLUMN}', but got '{df.columns[0]}'."

        )

    # Gene ID checks
    gene = df[REQUIRED_GENE_COLUMN].astype(str).str.strip()
    if (gene == "").any():
        raise ValueError("Count matrix contains empty Geneid values.")
    if gene.duplicated().any():
        dups = gene.loc[gene.duplicated()].unique().tolist()
        raise ValueError(f"Duplicate Geneid values found: {dups}")

    # Sample columns (everything except Geneid)
    sample_cols = list(df.columns[1:])

    # No missing values in sample columns
    if df[sample_cols].isna().any().any():
        raise ValueError(
            "Count matrix contains missing values in sample columns.")

    # Covert to numeric (will raise if non-numeric values found)
    numeric = df[sample_cols].apply(pd.to_numeric, errors="raise")

    # Must be integer-like (no decimals)
    if (numeric % 1 != 0).any().any():
        raise ValueError(
            "Count matrix contains non-integer values in sample columns (counts must be integers)")

    # Must be non-negative
    if (numeric < 0).any().any():
        raise ValueError(
            "Count matrix contains negative values in sample columns (counts must be >=0)")


def align_counts_and_samples(
    counts_df: pd.DataFrame, samples_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ensure sample names match between count matrix and samples metadata.
    
    - Count matrix sample columns are counts_df.columns[1:]
    - samples_df must have a 'sample' column
    - Reorders samples_df ro match the column order in counts_df
    - Raises clear errors listing missing/extra sample names

    """
    if "sample" not in samples_df.columns:
        raise ValueError("samples_df must contain a 'sample' column.")

    count_samples = list(counts_df.columns[1:])
    meta_samples = samples_df["sample"].astype(str).tolist()

    missing_in_meta = sorted(set(count_samples) - set(meta_samples))
    extra_in_meta = sorted(set(meta_samples) - set(count_samples))

    if missing_in_meta or extra_in_meta:
        parts: list[str] = []
        if missing_in_meta:
            parts.append(f"Missing in samples.tsv: {missing_in_meta}")
        if extra_in_meta:
            parts.append(f"Extra in samples.tsv: {extra_in_meta}")
        raise ValueError(
            "Sample mismatch between count matrix and samples.tsv. " + " | ".join(parts))
    # Reorder metadata to match count matrix column order
    samples_df = samples_df.set_index(
        "sample").loc[count_samples].reset_index()

    return counts_df, samples_df
