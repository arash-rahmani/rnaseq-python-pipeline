# rnaseq-python-pipeline

Reproducible RNA-seq analysis workflow in Python (QC -> DE -> reports), built with a clean `src/` layout and tested with `pytest`

## What's included (so far)
- Sample sheet loader + validation : `load_sample_tsv()` (`src/rnaseq_native/io.py`)
- Unit tests for input validation (`tests/test_io.py`)

## Project layout
- `src/` : pipeline source code (Python package)
- `config/`: configuration files (e.g. `samples.tsv`)
- `tests/`: automated tests (pytest)

## Setup
Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
# Windows Powershell:
.\venv\Scripts\Activate.ps1

python -m pip install -r requirments.txt


