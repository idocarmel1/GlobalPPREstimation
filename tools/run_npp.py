"""Run annual NPP from the active scientific package, regardless of working directory."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "scientific_code" / "NPPExtraction"))

from npp.annual import main


if __name__ == "__main__":
    raise SystemExit(main())
