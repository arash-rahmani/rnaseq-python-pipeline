from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

import pandas as pd
from rnaseq_native.paths import project_root


def strip_tair_isoform(gene_id: str) -> str:
    """
    Convert Arabidopsis isoform IDs like AT1G11910.1 -> AT1G11910.
    Leave values unchanged if they are not strings or do not contain '.'.
    """
    if not isinstance(gene_id, str):
        return gene_id
    return gene_id.split(".")[0].strip()


def main(argv: list[str]) -> int:
    project_root = Path(__file__).resolve().parents[1]

    ranked_path = (
        Path(argv[1])
        if len(argv) > 1
        else project_root / "results" / "exports" / "gsea_ranked_genes.tsv"
    )

    annotation_path = (
        Path(argv[2])
        if len(argv) > 2
        else project_root
        / "data"
        / "annotation"
        / "Final_Annotated_STRG_DESeq2_Expression_Merged_Fixed.csv"
    )

    outdir = (
        Path(argv[3])
        if len(argv) > 3
        else project_root / "results" / "exports"
    )
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Reading ranked genes from: {ranked_path}")
    print(f"Reading annotation from: {annotation_path}")

    ranked_df = pd.read_csv(ranked_path, sep="\t")
    ann_df = pd.read_csv(annotation_path)

    # ---validate required columns---
    ranked_required = {"gene", "rank_metric"}
    ann_required = {"STRG_key", "Arabidopsis_ID"}

    missing_ranked = ranked_required - set(ranked_df.columns)
    missing_ann = ann_required - set(ann_df.columns)

    if missing_ranked:
        raise ValueError(
            f"Missing columns in ranked file: {sorted(missing_ranked)}")
    if missing_ann:
        raise ValueError(
            F"Missing columns in annotation file: {sorted(missing_ann)}")

    # ---build clean mapping table---
    map_df = ann_df[["STRG_key", "Arabidopsis_ID"]].copy()
    map_df = map_df.dropna(subset=["STRG_key", "Arabidopsis_ID"]).copy()

    map_df["STRG_key"] = map_df["STRG_key"].astype(str).str.strip()
    map_df["Arabidopsis_ID"] = map_df["Arabidopsis_ID"].astype(
        str).map(strip_tair_isoform)

    # remove empty IDs after cleaning
    map_df = map_df[
        (map_df["STRG_key"] != "")
        & (map_df["Arabidopsis_ID"] != "")
        & (map_df["Arabidopsis_ID"] != "nan")
    ].copy()

    # deduplicate STRG -> TAIR pairs
    map_df = map_df.drop_duplicates()

    # If one STRG maps to multiple TAIR IDs, keep the first one deterministically.
    multi_map = map_df.groupby("STRG_key")["Arabidopsis_ID"].nunique()
    n_multi = int((multi_map > 1). sum())
    if n_multi > 0:
        print(
            f"Warning: {n_multi} STRG IDs map to multiple TAIR IDs. Keeping first mapping per STRG.")

    map_df = map_df.sort_values(["STRG_key", "Arabidopsis_ID"]).drop_duplicates(
        subset=["STRG_key"], keep="first"
    )

    # ---merge ranked genes with mapping---
    ranked_df["gene"] = ranked_df["gene"].astype(str).str.strip()

    merged = ranked_df.merge(
        map_df,
        how="left",
        left_on="gene",
        right_on="STRG_key",
    )

    n_total = int(len(merged))
    n_mapped = int(merged["Arabidopsis_ID"].notna().sum())
    n_unmapped = n_total - n_mapped

    print(f"Total ranked genes: {n_total}")
    print(f"Mapped genes:       {n_mapped}")
    print(f"Unmapped genes:     {n_unmapped} ")

    tair_df = merged.dropna(subset=["Arabidopsis_ID"]).copy()

    # rename for output
    tair_df = tair_df.rename(columns={"Arabidopsis_ID": "gene_tair"})

    # If multiple STRG map to the same TAIR gene, keep the row with largest absolute rank_metric.
    tair_df["abs_rank_metric"] = tair_df["rank_metric"].abs()
    tair_df = tair_df.sort_values("abs_rank_metric", ascending=False).drop_duplicates(
        subset=["gene_tair"], keep="first"
    )

    # Sort descending or preranked GSEA
    tair_df = tair_df.sort_values("rank_metric", ascending=False)

    # ---outputs---
    tsv_path = outdir / "gsea_ranked_genes_TAIR.tsv"
    rnk_path = outdir / "gsea_ranked_genes_TAIR.rnk"
    unmapped_path = outdir / "gsea_unmapped_STRG.tsv"
    mapping_used_path = outdir / "strg_to_tair_mapping_used.tsv"

    tair_df[
        ["gene_tair", "rank_metric", "gene", "log2FoldChange", "pvalue", "padj"]
    ].to_csv(tsv_path, sep="\t", index=False)

    tair_df[["gene_tair", "rank_metric"]].to_csv(
        rnk_path, sep="\t", index=False, header=False
    )

    merged[merged["Arabidopsis_ID"].isna()][["gene", "rank_metric"]].to_csv(
        unmapped_path, sep="\t", index=False
    )

    map_df.to_csv(mapping_used_path, sep="\t", index=False)

    print(f"Wrote: {tsv_path}")
    print(f"Wrote: {rnk_path}")
    print(f"Wrote: {unmapped_path}")
    print(f"Wrote: {mapping_used_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
