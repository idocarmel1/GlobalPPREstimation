"""Build ewe-species-to-group-mapper.skill from the source directory."""
from __future__ import annotations
import zipfile
from pathlib import Path

SRC = Path(__file__).resolve().parent / "ewe-species-to-group-mapper"
OUT = SRC.parent / "ewe-species-to-group-mapper.skill"

# Excluded by design: artifact-template.json and agents/ are artifact-template and
# OpenAI packaging scaffolding that a Claude skill never reads. They stay in the
# repository for the later GPT adaptation.
EXCLUDE_NAMES = {"artifact-template.json", ".DS_Store"}
EXCLUDE_DIRS = {"agents", "__pycache__"}


def included(path: Path) -> bool:
    rel = path.relative_to(SRC)
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return False
    if path.name in EXCLUDE_NAMES:
        return False
    if path.name.startswith("~$"):
        return False
    return path.is_file()


def main() -> None:
    files = sorted(p for p in SRC.rglob("*") if included(p))
    if not files:
        raise SystemExit(f"no files found under {SRC}")
    OUT.unlink(missing_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = Path(SRC.name) / path.relative_to(SRC)
            zf.write(path, arcname.as_posix())
    print(f"wrote {OUT.name} with {len(files)} files")
    for path in files:
        print("   ", (Path(SRC.name) / path.relative_to(SRC)).as_posix())


if __name__ == "__main__":
    main()
