from pathlib import Path
import gseapy as gp


def main() -> None:
    rnk_file = Path("results/exports/gsea_ranked_genes_TAIR.rnk")
    gmt_file = Path("data/gene_sets/GO_BP_Arabidopsis_fixed.gmt")
    outdir = Path("results/gsea/go_bp")

    if not rnk_file.exists():
        raise FileNotFoundError(f"Ranked file not found: {rnk_file}")

    if not gmt_file.exists():
        raise FileNotFoundError(f"GMT file not fount: {gmt_file}")

    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Running preranked GSEA")
    print(f"Ranked file: {rnk_file}")
    print(f"Gene sets:   {gmt_file}")
    print(f"Output dir:  {outdir}")

    gp.prerank(
        rnk=str(rnk_file),
        gene_sets=str(gmt_file),
        outdir=str(outdir),
        permutation_num=1000,
        min_size=10,
        max_size=500,
        seed=42,
        threads=4,
        verbose=True,
    )

    print("GSEA finished successfully.")


if __name__ == "__main__":
    main()
