"""Build advisory EEZ spatial flags without changing existing LME/HS outputs."""
import argparse
import json
from pathlib import Path

from ppr_pipeline.eez_spatial import build_eez_spatial_outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--low-overlap-threshold",type=float,default=.10)
    parser.add_argument("--containment-threshold",type=float,default=.90)
    parser.add_argument("--prefer-ratio",type=float,default=1.20)
    parser.add_argument("--review-ratio",type=float,default=1.10)
    args = parser.parse_args()
    result = build_eez_spatial_outputs(**vars(args))
    print(json.dumps({key:value for key,value in result.items() if key != "source_geometry_audits"},indent=2))


if __name__ == "__main__":
    main()
