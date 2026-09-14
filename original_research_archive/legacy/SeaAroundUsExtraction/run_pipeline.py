from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ppr_pipeline.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Sea Around Us five-region PPR pilot.")
    parser.add_argument("--year", type=int, default=None, help="Common year override; latest common year by default.")
    args = parser.parse_args()
    result = run_pipeline(ROOT, requested_year=args.year)
    print(f"Completed five-region pilot for {result['year']}.")
    print(result["summary"].to_string(index=False))


if __name__ == "__main__":
    main()

