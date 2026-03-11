# Data directory 

This directory contains project data resources used by the RNA-seq pipeline.

## Contents 

### `annotations/`
Contains annotation tables used to map transcript-level STRG identifiers to Arabidopsis refrence loci.

Current annotation file used in the pipeline:

- `Final_Annotated_STRG_DESeq2_Expression_Merged_FIXED.csv`

## Annotation mapping purpose

The pipeline performs differential expression analysis from a count matrix and exports ranked genes for GSEA. Because downstream enrichment uses Arabidopsis-based gene sets, ranked STRG identifires are mapped to TAIR loci using the annotation table.

This mapping is performed by:

- `scripts/map_strg_to_tair.py`

## Mapping logic

The script merges:

- `results/exports/gsea_ranked_genes.tsv`
- `STRG_key` from the annotation table

It then extracts Arabidopsis locus information from:
- `Arabidopsis_ID`

Isoform suffixes are removed so the final ranked output contains uniqe TAIR-style gene identifires suitable for GSEA.

## Mapping outputs

The mapping step writes:

- `results/exports/gsea_ranked_genes_TAIR.tsv`
- `results/exports/gsea_ranked_genes_TAIR.rnk`
- `results/exports/gsea_unmapped_STRG.tsv`
- `results/exports/strg_to_tair_mapping_used.tsv`

## Interpretation note

This mapping is annotation-assisted and intended for downstream functional interpretation using Arabidopsis reference gene sets.

Some STRG IDs may map to multiple Arabidopsis candidates in the annotation table. In this pipline implementation, the first mapping per STRG is selected to make a reproducible one-to-one ranked file for GSEA.

## Reproducibility note

Large raw data files and bulky intermediate outputs should generally not be committed to Git unless needed for demonstration. Code, configuration, lightweight metadata, and documentation should remained version-controlled.
