from __future__ import annotations

import json
import sys
from pathlib import Path

from rnaseq_native.paths import project_root


def main(argv: list[str]) -> int:
    plan_path = Path(argv[1]) if len(argv) > 1 else project_root(
    ) / "results" / "analysis" / "de_plan.json"

    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    print(f"Loaded plan: {plan_path}")
    print(f"Mode: {plan['mode']}")
    print(f"Counts: {plan['inputs']['counts_csv']}")
    print(f"Samples: {plan['inputs']['samples_tsv']}")
    print(f"Design factors: {plan['design']['factors']}")
    print(f"Contrast: {plan['design']['contrast']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
