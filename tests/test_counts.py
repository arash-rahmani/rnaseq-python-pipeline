from pathlib import Path
import pytest

from rnaseq_native.counts import load_count_matrix


def test_missing_count_matrix_raises(tmp_path: Path) -> None:
    p = tmp_path / "nope.tsv"
    with pytest.raises(FileNotFoundError):
        load_count_matrix(p)
