from pathlib import Path

import pytest

from rnaseq_native.config import load_config_yaml


def test_load_config_yaml_missing_file_raises(tmp_path: Path) -> None:
    p = tmp_path / "nope.yaml"
    with pytest.raises(FileNotFoundError):
        load_config_yaml(p)

def test_load_config_yaml_reads_values(tmp_path: Path) -> None:
    p = tmp_path / "config.yaml"
    p.write_text(
        "samples_tsv: config/samples.tsv\n"
        "strict_paths: false\n"
        "qc:\n"
        " outdir: results/qc\n"
        " fastp:\n"
        "   threads: 7\n",
        encoding="utf-8",
    )
    cfg = load_config_yaml(p)
    assert cfg["samples_tsv"] == "config/samples.tsv"
    assert cfg["strict_paths"] is False
    assert cfg["qc"]["fastp"]["threads"] == 7

def test_load_config_yaml_empty_yaml_returns_empty_dict(tmp_path: Path) -> None:
    p = tmp_path / "empty.yaml"
    p.write_text("", encoding="utf-8")
    cfg = load_config_yaml(p)
    assert cfg == {}