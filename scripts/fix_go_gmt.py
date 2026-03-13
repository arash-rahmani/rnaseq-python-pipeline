from pathlib import Path
from collections import OrderedDict

in_file = Path("data/gene_sets/GO_BP_Arabidopsis.gmt")
out_file = Path("data/gene_sets/GO_BP_Arabidopsis_fixed.gmt")

gene_sets = OrderedDict()
descriptions = {}

with in_file.open("r", encoding="utf-8", errors="ignore") as f:
    for raw_line in f:
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split("\t")

        # Expecting: TERM, DESCRIPTION_FIELD, GENE
        if len(parts) != 3:
            continue

        term = parts[0].strip()
        desc = parts[1].strip()
        gene_block = parts[2].strip()

        genes = [g.strip().upper() for g in gene_block.split(",") if g.strip()]

        if term not in gene_sets:
            gene_sets[term] = []
            descriptions[term] = desc

        for gene in genes:
            if gene not in gene_sets[term]:
                gene_sets[term].append(gene)


with out_file.open("w", encoding="utf-8") as f:
    kept = 0
    for term, genes in gene_sets.items():
        if not genes:
            continue
        desc = descriptions[term]
        line = "\t".join([term, desc] + genes)
        f.write(line + "\n")
        kept += 1

print("Fixed GMT written to:")
print(out_file)
print("Total gene sets:", kept)
