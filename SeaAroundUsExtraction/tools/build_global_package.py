"""Package the global pipeline while leaving any open pilot workbooks untouched."""

from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent


def include(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    parts = relative.parts
    if parts and parts[0] == "output":
        return False
    if ".pytest_cache" in parts or "__pycache__" in parts:
        return False
    if path.name.endswith(".inspect.ndjson"):
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", default="PPR_pipeline_global_complete.zip")
    args = parser.parse_args()
    if Path(args.destination).name != args.destination or not args.destination.endswith(".zip"):
        raise ValueError("Destination must be a ZIP filename in the project directory.")
    destination = PROJECT / args.destination
    destination.unlink(missing_ok=True)
    count = 0
    with zipfile.ZipFile(
        destination,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
        allowZip64=True,
    ) as archive:
        for path in sorted(item for item in ROOT.rglob("*") if item.is_file()):
            if not include(path):
                continue
            archive.write(path, Path(ROOT.name) / path.relative_to(ROOT))
            count += 1
    print(f"{destination} ({count} files)")


if __name__ == "__main__":
    main()
