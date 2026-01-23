# rnaseq-python-pipeline

Reproducible RNA-seq analysis workflow in Python (QC -> DE -> reports), built with a clean `src/` layout and tested with `pytest`.

## What's included (so far)
- Sample sheet loader + validation : `load_samples_tsv()` (`src/rnaseq_native/io.py`)
 - Validates required columns: sample, tree, condition,r1, r2
 - Strips whitespace
 - Rejects empty/duplicate sample names
 - Validates allowed conditions: Control / Protzen
 - Optional `strict_paths=True` checks FASTQ file exsistence
- Unit tests for input validation (`tests/test_io.py`)
- Test import setup (`tests/conftest.py` adds `<project_root>/src` to `sys.path`)

## Project layout
- `src/` : pipeline source code (Python package)
- `config/`: configuration files (e.g. `samples.tsv`)
- `tests/`: automated tests (pytest)
- `data/`: local input data (not committed)
- `results/`: generated outputs (not committed)

## Setup
Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv

# Windows Powershell:
.\venv\Scripts\Activate.ps1

python -m pip install -r requirments.txt


