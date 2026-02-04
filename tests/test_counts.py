from pathlib import Path

import pandas as pd
import pytest

from rnaseq_native.counts import load_count_matrix, validate_count_matrix


def test_missing_count_matrix_raises(tmp_path: Path) -> None:
    p = tmp_path / "nope.tsv"
    with pytest.raises(FileNotFoundError):
        load_count_matrix(p)


def test_validate_requires_geneid_first_column() -> None:
    df = pd.DataFrame({"notGeneid": ["g1"], "S1": ["1"]})
    try:
        validate_count_matrix(df)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "First comlumn must be" in str(e)


def test_validate_rejects_empty_geneid() -> None:
    df = pd.DataFrame({"Geneid": [""], "S1": ["1"]})
    try:
        validate_count_matrix(df)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "empty geneid" in str(e).lower()


def test_validate_rejects_duplicate_geneid() -> None:
    df = pd.DataFrame({"Geneid": ["g1", "g1"], "S1": ["1", "2"]})
    try:
        validate_count_matrix(df)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "duplicate" in str(e).lower()
        assert "g1" in str(e)


def test_counts_rejects_negative() -> None:
    df = pd.DataFrame({"Geneid": ["g1"], "S1": ["-1"]})
    try:
        validate_count_matrix(df)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "negative" in str(e).lower()


def test_counts_rejects_non_integer() -> None:
    df = pd.DataFrame({"Geneid": ["g1"], "S1": ["1.5"]})
    try:
        validate_count_matrix(df)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "non-integer" in str(e).lower()


def test_counts_rejects_non_numeric() -> None:
    df = pd.DataFrame({"Geneid": ["g1"], "S1": ["abc"]})
    try:
        validate_count_matrix(df)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "parse string" in str(e).lower()
