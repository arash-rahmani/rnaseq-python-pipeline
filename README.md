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

## Data notes

project data and annotation resources are documented in `data/README.md`.

The repository uses an annotation-assisted mapping workflow to convert transcript-level STRG identifires into Arabidopsis TAIR loci for downstream enrichment analysis.

Main annotation resource currently used:

- `data/annotation/Final_Annotated_STRG_DESeq2_Expression_Merged_FIXED.csv`

This file is used by:

- `scripts/map_strg_to_tair.py`

It supports the merge:

- `Geneid` <-> `STRG_key`

and extracts Arabidopsis identifires from:

- `Arabidopsis_ID`

Outputs generated from this mapping step include:

- `results/exports/gsea_ranked_genes_TAIR.tsv`
- `results/exports/gsea_ranked_genes_TAIR.rnk`
- `results/exports/gsea_unmapped_STRG.tsv`
- `results/exports/strg_to_tair_mapping_used.tsv`

Note: some STRG IDs map to multiple TAIR canditates in the annotation table. In the current pipeline version, the first mapping per STRG is retained for reproducible downstream GSEA preparation.

## Functional enrichment(GSEA)

 Preranked Gene Set Enrichment Analysis (GSEA) is performed using the `gseapy` Python package.

Workflow steps:

1. Differential expression analysis using PyDESeq2.
2. Ranking genes based on signed statistical scores.
3. Mapping transcript IDs (STRG) to Arabidopsis TAIR identifiers.
4. Converting GO annotations into a valid GMT gene set file.
5. Running preranked GSEA.

Scripts used:

- scripts/map_strg_to_tair.py
- scripts/fix_go_gmt.py
- scripts/run_gsea.py

The `fix_go_gmt.py` script converts GO annotation tables into a valid GMT gene set format by aggregating genes belonging to the same GO term.


Outputs are written to:

results/gsea/go_bp/

These include enrichment tables and pathway plots for GO biological process terms.



