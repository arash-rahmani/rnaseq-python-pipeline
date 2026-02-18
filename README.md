# rnaseq-python-pipeline

Reproducible RNA-seq analysis workflow in Python (counts-first DE now; QC hooks ready), built with a clean `src/` layout and tested with `pytest`.

## What's included (so far)
- Sample sheet loader + validation : `load_samples_tsv()` (`src/rnaseq_native/io.py`)
 - required columns (FASTQ mode): `sample, tree, condition,r1, r2`
 - Counts-first mode: requires only `sample, tree, condition`
 - Strips whitespace
 - Rejects empty/duplicate sample names
 - Validates allowed conditions: Control / Protzen
 - Optional `strict_path=True` checks FASTQ file exsistence
- Count matrix loader + validation + alignment (`src/rnaseq_native/counts.py`)
- DE plan + DE run via PyDESeq2 (`scripts/de_dry_run.py`, `scripts/de_run.py`)
- Unit tests (`tests/`)
- Test import setup (`tests/conftest.py` adds `<project_root>/src` to `sys.path`)

## Project layout
- `src/` : pipeline source code (Python package)
- `config/`: configuration files (e.g. `config.yaml`, `samples.tsv`)
- `scripts`: runnable entry scripts
- `tests/`: automated tests (pytest)
- `data/`: local input data (not committed)
- `results/`: generated outputs (not committed)

```md
## Setup (Windows/Powershell)
```powershell
cd F:\python_thesis
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirement.txt




