from pathlib import Path
import pandas as pd

# Expected format for the sample sheet (TSV file)
REQUIRED_COLUMNS = ("sample", "tree", "condition", "r1", "r2")
ALLOWED_CONDITIONS = ("Control", "Protzen")


def load_samples_tsv(path: str | Path, strict_path: bool = False) -> pd.DataFrame:
    """ Load and validate a sample sheet TSV file for the RNA-seq pipeline.
    the TSV must contain REQUIRED_COLUMNS:
    sample, tree, condition, r1, r2
    
    Typical usage:
        - sample: sample ID (string)
        - tree: tree identifier (string/int stored as text)
        - condition: group label (e.g., Control / Protzen)
        - r1, r2: paths to paired-end FASTQ files
    Exceptions:
     FileNotFoundError: if the TSV file does not exist.
     ValueError: if required columns are missing.
    """
# Normalize input: create str or path, then work with a Path object consistently
    path = Path(path)

# Fail early if the file does not exist
    if not path.exists():
        raise FileNotFoundError(f"Sample sheet not found: {path}")

# Read the TSV file into a DataFrame
# sep="\t" specifies tab-separated values
# dtype=str ensures all data is read as strings (to avoid type inference issues)
# fillna replaces missing values with empty strings
    df = pd.read_csv(path, sep="\t", dtype=str)
    df = df.fillna("")

# Validate schema: check for required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns in {path.name}: {missing}. Required: {REQUIRED_COLUMNS}")
# Bsic data cleaning: trim whitespace from string columns
    for col in REQUIRED_COLUMNS:
        df[col] = df[col].str.strip()
# Validation: sample must be present and unique
    if (df["sample"] == "").any():
        raise ValueError(f"Some rows have empty 'sample' values.")
    if df["sample"].duplicated().any():
        dups = df.loc[df["sample"].duplicated(), "sample"].tolist()
        raise ValueError(f"Duplicate sample IDs found: {dups}")
# Validation: Condition must be one of the allowed values
    bad = sorted(set(df["condition"]) - set(ALLOWED_CONDITIONS))
    if bad:
        raise ValueError(
            f"unknown condition(s) {bad}. Allowed: {ALLOWED_CONDITIONS}")
# Optional validation: verify that FASTQ files exist
    if strict_path:
        missing_paths: list[str] = []
        for col in ("r1", "r2"):
            for p in df[col].tolist():
                if p and not Path(p).exists():
                    missing_paths.append(p)
        if missing_paths:
            raise FileNotFoundError(f"Missing FASTQ paths: {missing_paths}")

    return df
