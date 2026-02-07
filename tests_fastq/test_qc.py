from pathlib import Path

from rnaseq_native.qc import FastpQCConfig, fastp_command


def test_fastp_command_build_expected_outputs(tmp_path: Path) -> None:
    cmd = fastp_command(
        sample="S1",
        r1="R1.fastq.gz",
        r2="R2.fastq.gz",
        outdir=tmp_path,
        cfg=FastpQCConfig(threads=8),
    )
    assert cmd[0] == "fastp"
    assert "-w" in cmd
    assert "8" in cmd
    assert str(tmp_path / "S1.fastp.html") in cmd
    assert str(tmp_path / "S1.trimmed.R1.fastq.gz") in cmd
