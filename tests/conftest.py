from __future__ import annotations

import sys
from pathlib import Path

# Add the <project_root>/src to python import path for all tests
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))
