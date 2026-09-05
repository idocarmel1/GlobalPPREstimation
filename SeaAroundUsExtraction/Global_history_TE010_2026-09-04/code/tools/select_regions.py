"""Select fixed whole regions across all years and audit actual spatial overlaps."""
import argparse
import json
from pathlib import Path

from ppr_pipeline.selection import build_selection_outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--expected-count", type=int, default=366)
    args = parser.parse_args()
    result = build_selection_outputs(**vars(args), progress=lambda message: print(message, flush=True))
    print(json.dumps({k:v for k,v in result.items() if k not in ("scenarios", "scenario_details", "validation")}, indent=2))


if __name__ == "__main__":
    main()
