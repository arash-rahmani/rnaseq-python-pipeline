from pathlib import Path

import pandas as pd
import pytest

from rnaseq_native.counts import (
    load_count_matrix, 
    validate_count_matrix, 
    align_counts_and_samples,
)



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
        assert "First column must be" in str(e)


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


def test_counts_sample_mismatch_raises_clear_error() -> None:
    counts = pd.DataFrame(
        {"Geneid": ["g1"], "A": ["1"], "B": ["2"]}
    )
    meta = pd.DataFrame(
        {"sample": ["A", "C"], "tree": ["1", "1"], "condition": ["Control", "Protzen"],
         "r1": ["x", "y"], "r2": ["x", "y"]}
    )
    try:
        align_counts_and_samples(counts, meta)
        assert False, "Expected ValueError"
    except ValueError as e:
        msg = str(e)
        assert "Missing in samples.tsv" in msg
        assert "Extra in samples.tsv" in msg
        assert "B" in msg  # missing
        assert "C" in msg  # extra


def test_align_reorders_metadata_to_match_counts() -> None:
    counts = pd.DataFrame({"Geneid": ["g1"], "B": ["2"], "A": ["1"]})
    meta = pd.DataFrame(
        {
            "sample": ["A", "B"],
            "tree": ["1", "1"],
            "condition": ["Control", "Protzen"],
            "r1": ["x", "y"],
            "r2": ["x", "y"]
        }
    )
    _, meta2 = align_counts_and_samples(counts, meta)
    assert meta2["sample"].tolist() == ["B", "A"]
