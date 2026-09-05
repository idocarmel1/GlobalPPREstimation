"""Run resumable PPR calculations for all frozen regions and available years."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from ppr_pipeline.history import run_history_pipeline


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chunksize', type=int, default=250_000)
    parser.add_argument('--output-root', type=Path)
    arguments = parser.parse_args()
    result = run_history_pipeline(ROOT, chunksize=arguments.chunksize, output_root=arguments.output_root)
    print(json.dumps(result['metadata'], indent=2))


if __name__ == '__main__':
    main()
