"""Download or reuse catch and trophic inputs for every LME and High Seas unit."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ppr_pipeline.download import download_unit_inputs, load_units_from_spatial_index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true", help="replace existing downloads")
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "config" / "global.yml").read_text(encoding="utf-8"))
    units = load_units_from_spatial_index(ROOT / config["scope"]["unit_index"])
    outputs = download_unit_inputs(
        units,
        config["sea_around_us"]["api_base_url"],
        ROOT / config["scope"]["raw_directory"],
        overwrite=args.overwrite,
    )
    print(f"Ready: {len(units)} units and {len(outputs)} unit input files")


if __name__ == "__main__":
    main()
