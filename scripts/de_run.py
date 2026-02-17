from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats


from rnaseq_native.paths import project_root
from rnaseq_native.io import load_samples_tsv
from rnaseq_native.counts import load_count_matrix, align_counts_and_samples


def main(argv: list[str]) -> int:
    plan_path = Path(argv[1]) if len(argv) > 1 else project_root(
    ) / "results" / "analysis" / "de_plan.json"

    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    counts_path = Path(plan["inputs"]["counts_csv"])
    samples_path = Path(plan["inputs"]["samples_tsv"])

    samples_df = load_samples_tsv(samples_path, require_fastq=False)
    counts_df = load_count_matrix(counts_path)

    counts_df, samples_df = align_counts_and_samples(counts_df, samples_df)

    print("Loaded and aligned inputs for DE")

    # Prepare PyDESeq2 inputs
    counts_only = counts_df.set_index("Geneid").astype(int)
    coldata = samples_df.set_index("sample")[["condition"]].copy()

    print("coldata type:", type(coldata))
    print("coldata shape:", coldata.shape)

    print("Prepared PyDESeq2 inputs")
    print(f"counts_only shape: {counts_only.shape}")
    print(f"coldata shape: {coldata.shape}")

    dds = DeseqDataSet(
        counts=counts_only.T,
        metadata=coldata,
        design="~condition",
    )

    print("DeseqDataSet created")

    print("Running DESeq2...")
    dds.deseq2()
    print("DESeq2 finished")

    outdir = project_root() / "results" / "deseq2"
    outdir.mkdir(parents=True, exist_ok=True)

    print("Computing DE statistics...")
    stat_res = DeseqStats(dds, contrast=["condition", "Protzen", "Control"])
    stat_res.summary()
    res_df = stat_res.results_df

    # ---- summary report(quick sanity + insigt) ----
    n_total = int(res_df.shape[0])
    n_p_nan = int(res_df["pvalue"].isna().sum())
    n_padj_nan = int(res_df["padj"].isna().sum())
    n_p_lt_005 = int((res_df["pvalue"] < 0.05).sum(skipna=True))
    n_padj_lt_005 = int((res_df["padj"] < 0.05).sum(skipna=True))

    print("\nDE SUMMARY")
    print(f"genes total: {n_total}")
    print(f"genes pvalue NaN: {n_p_nan}")
    print(f"padj NaN: {n_padj_nan}")
    print(f"pvalue < 0.05: {n_p_lt_005}")
    print(f"padj < 0.05: {n_padj_lt_005}")

    top_p = res_df.dropna(subset=["pvalue"]).sort_values("pvalue").head(10)
    print("\nTop 10 genes by p-value:")
    print(top_p[["log2FoldChange", "pvalue", "padj"]])

    top_lfc = res_df.dropna(subset=["log2FoldChange"]).assign(
        abs_lfc=lambda d: d["log2FoldChange"].abs()
    ).sort_values("abs_lfc", ascending=False).head(10)

    print("\nTop 10 genes by |log2FoldChange|:")
    print(top_lfc[["log2FoldChange", "pvalue", "padj"]])


    print("Stats finished")
    print(res_df.head())

    all_path = outdir / "deseq2_all_results.csv"
    res_df.to_csv(all_path)
    print(f"Wrote: {all_path}")

    sig = res_df.dropna(subset=["padj"]).query("padj < 0.05").copy()
    sig_path = outdir / "deseq2_significant_results.csv"
    sig.to_csv(sig_path)
    print(f"Wrote: {sig_path} (n={sig.shape[0]})")


    print(f"Loaded plan: {plan_path}")
    print(f"Mode: {plan['mode']}")
    print(f"Counts: {plan['inputs']['counts_csv']}")
    print(f"Samples: {plan['inputs']['samples_tsv']}")
    print(f"Design factors: {plan['design']['factors']}")
    print(f"Contrast: {plan['design']['contrast']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
