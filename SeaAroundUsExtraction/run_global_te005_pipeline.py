from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ppr_pipeline.pipeline import run_analysis  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run all-unit Sea Around Us PPR with TE=0.05."
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Common year override; latest common year by default.",
    )
    args = parser.parse_args()
    result = run_analysis(
        ROOT,
        ROOT / "config" / "global_te005.yml",
        requested_year=args.year,
    )
    print(
        f"Completed {len(result['summary'])}-unit TE=0.05 global run "
        f"for {result['year']}."
    )
    print(result["summary"].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
