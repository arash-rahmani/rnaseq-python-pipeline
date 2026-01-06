from __future__ import annotations

from pathlib import Path

import pytest

from rnaseq_native.io import load_samples_tsv, REQUIRED_COLUMNS


def _write_tsv(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_missing_file_raises_filenotfounderror(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.tsv"
    with pytest.raises(FileNotFoundError):
        load_samples_tsv(missing)


def test_missing_required_columns_raise_valueerror(tmp_path: Path) -> None:
    p = _write_tsv(
        tmp_path / "missing_col.tsv",
        "sample\ttree\tcondition\tr1\nA\t1\tControl\tR1\n",  # R2 is missing
    )
    with pytest.raises(ValueError) as excinfo:
        load_samples_tsv(p)
    msg = str(excinfo.value)
    assert "Missing required columns" in msg
    assert "r2" in msg


def test_strip_whitespace(tmp_path: Path) -> None:
    p = _write_tsv(
        tmp_path / "spaces.tsv",
        "sample\ttree\tcondition\tr1\tr2\n  A  \t 1 \t Control  \t R1 \t R2 \n",
    )
    df = load_samples_tsv(p)
    assert df.loc[0, "sample"] == "A"
    assert df.loc[0, "condition"] == "Control"


def test_empty_sample_rejected(tmp_path: Path) -> None:
    p = _write_tsv(
        tmp_path / "empty_sample.tsv",
        "sample\ttree\tcondition\tr1\tr2\n\t1\tControl\tR1\tR2\n",
    )
    with pytest.raises(ValueError) as excinfo:
        load_samples_tsv(p)
    assert "empty" in str(excinfo.value).lower()
    assert "sample" in str(excinfo.value).lower()


def test_duplicate_samples_rejected(tmp_path: Path) -> None:
    p = _write_tsv(
        tmp_path / "dups.tsv",
        "sample\ttree\tcondition\tr1\tr2\nA\t1\tControl\tR1\tR2\nA\t1\tProtzen\tR1\tR2\n",
    )
    with pytest.raises(ValueError) as excinfo:
        load_samples_tsv(p)
    assert "duplicate" in str(excinfo.value).lower()
    assert "A" in str(excinfo.value)


def test_required_columns_is_correct() -> None:
    assert REQUIRED_COLUMNS == ("sample", "tree", "condition", "r1", "r2")
