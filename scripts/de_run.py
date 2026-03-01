from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats


from rnaseq_native.paths import project_root
from rnaseq_native.io import load_samples_tsv
from rnaseq_native.counts import load_count_matrix, align_counts_and_samples


def main(argv: list[str]) -> int:
    plan_path = Path(argv[1]) if len(argv) > 1 else Path(
        "results/analysis/de_plan.json")

    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    # --- outputs from plan---
    analysis_dir = Path(plan["outputs"]["analysis_dir"])
    outdir = Path(plan["outputs"]["deseq2_dir"])
    plots_dir = Path(plan["outputs"]["plots_dir"])
    outdir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    # --- design + filters from plan ---
    design = plan["design"]["formula"]
    contrast = plan["design"]["contrast"]
    alpha = float(plan["design"].get("alpha", 0.05))
    min_total = int(plan.get("filters", {}).get("min_total_count", 10))


    counts_path = Path(plan["inputs"]["counts_csv"])
    samples_path = Path(plan["inputs"]["samples_tsv"])

    samples_df = load_samples_tsv(samples_path, require_fastq=False)
    counts_df = load_count_matrix(counts_path)

    counts_df, samples_df = align_counts_and_samples(counts_df, samples_df)

    print("Loaded and aligned inputs for DE")

    # Prepare PyDESeq2 inputs
    counts_only = counts_df.set_index("Geneid").astype(int)

    # Filter low-count genes before DE
    keep = counts_only.sum(axis=1) >= min_total
    counts_only = counts_only.loc[keep]

    # Build metadata with tree + condition
    coldata = samples_df.set_index("sample")[["tree", "condition"]].copy()

    coldata["tree"] = pd.Categorical(coldata["tree"])
    coldata["condition"] = pd.Categorical(
        coldata["condition"], categories=["Control", "Protzen"])

    print("Condition categories:", coldata["condition"].cat.categories)
    print("Tree categories:", coldata["tree"].cat.categories)

    print("Prepared PyDESeq2 inputs")
    print(f"counts_only shape: {counts_only.shape}")
    print(f"coldata shape: {coldata.shape}")

    dds = DeseqDataSet(
        counts=counts_only.T,
        metadata=coldata,
        design=design,
    )

    print("DeseqDataSet created")

    print("Running DESeq2...")
    dds.deseq2()
    print("DESeq2 finished")

    print("Computing DE statistics...")
    contrast = plan["design"]["contrast"] # e.g. ["condition", "Protzen", "Control"]
    stat_res = DeseqStats(dds, contrast=contrast)
    stat_res.summary()
    res_df = stat_res.results_df

    # ---- summary report(quick sanity + insigt) ----
    n_total = int(res_df.shape[0])
    n_p_nan = int(res_df["pvalue"].isna().sum())
    n_padj_nan = int(res_df["padj"].isna().sum())
    n_p_lt_005 = int((res_df["pvalue"] < 0.05).sum(skipna=True))
    n_padj_lt_005 = int((res_df["padj"] < 0.05).sum(skipna=True))

    summary_path = outdir / "deseq2_summary.json"

    summary = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "plan_path": str(plan_path),
        "inputs": plan["inputs"],
        "design": plan["design"],
        "dataset": plan["dataset"],
        "summary": {
            "genes_total": n_total,
            "pvalue_nan": n_p_nan,
            "padj_nan": n_padj_nan,
            "pvalue_lt_005": n_p_lt_005,
            "padj_lt_005": n_padj_lt_005,
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote: {summary_path}")

    print("\nDE SUMMARY")
    print(f"genes total: {n_total}")
    print(f"genes pvalue NaN: {n_p_nan}")
    print(f"padj NaN: {n_padj_nan}")
    print(f"pvalue < 0.05: {n_p_lt_005}")
    print(f"padj < 0.05: {n_padj_lt_005}")

    top_p = res_df.dropna(subset=["pvalue"]).sort_values("pvalue").head(10)
    print("\nTop 10 genes by p-value:")
    print(top_p[["log2FoldChange", "pvalue", "padj"]])

    top_p_path = outdir / "top_10_by_pvalue.csv"
    top_p.to_csv(top_p_path)
    print(f"Wrote {top_p_path}")

    top_lfc = res_df.dropna(subset=["log2FoldChange"]).assign(
        abs_lfc=lambda d: d["log2FoldChange"].abs()
    ).sort_values("abs_lfc", ascending=False).head(10)

    print("\nTop 10 genes by |log2FoldChange|:")
    print(top_lfc[["log2FoldChange", "pvalue", "padj"]])

    top_lfc_path = outdir / "top_10_by_lfc.csv"
    top_lfc.to_csv(top_lfc_path)
    print(f"Wrote: {top_lfc_path}")


    print("Stats finished")
    print(res_df.head())

    all_path = outdir / "deseq2_all_results.csv"
    res_df.to_csv(all_path)
    print(f"Wrote: {all_path}")

    sig = res_df.dropna(subset=["padj"]).query("padj < @alpha").copy()
    sig_path = outdir / "deseq2_significant_results.csv"
    sig.to_csv(sig_path)
    print(f"Wrote: {sig_path} (n={sig.shape[0]})")


    print(f"Loaded plan: {plan_path}")
    print(f"Mode: {plan['mode']}")
    print(f"Counts: {plan['inputs']['counts_csv']}")
    print(f"Samples: {plan['inputs']['samples_tsv']}")
    print(f"Design formula: {plan['design']['formula']}")
    print(f"Contrast: {plan['design']['contrast']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
