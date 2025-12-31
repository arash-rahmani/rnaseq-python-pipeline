from pathlib import Path
import pandas as pd

REQUIERED_COLUMNS = ("saample", "tree", "condition", "r1", "r2")


def load_samples_tsv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Sample sheet not found: {path}")

    raise NotImplementedError("next step: we will read the tsv with pandas")
