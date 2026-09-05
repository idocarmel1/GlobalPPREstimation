"""Download the frozen Sea Around Us inputs for the configured pilot."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ppr_pipeline.download import download_pilot_inputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true", help="replace existing frozen downloads")
    args = parser.parse_args()
    outputs = download_pilot_inputs(
        ROOT / "config" / "pilot.yml",
        ROOT / "raw_data" / "SAU_downloads",
        overwrite=args.overwrite,
    )
    print(f"Ready: {len(outputs)} Sea Around Us input files")


if __name__ == "__main__":
    main()
