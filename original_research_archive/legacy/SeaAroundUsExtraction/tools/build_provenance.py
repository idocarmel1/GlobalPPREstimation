"""Build checksummed provenance for frozen inputs and inspected references."""

from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

from ppr_pipeline.download import load_units_from_spatial_index  # noqa: E402
from ppr_pipeline.provenance import unit_source_urls  # noqa: E402



def record(path: Path, *, source_url: str | None = None) -> dict[str, object]:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    item: dict[str, object] = {
        "path": path.relative_to(PROJECT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
    }
    if source_url:
        item["source_url"] = source_url
    return item


def main() -> None:
    base = "https://api.seaaroundus.org/api/v1"
    raw_dir = ROOT / "raw_data" / "SAU_downloads"
    url_by_name = {
        "lme_regions.json": f"{base}/lme/?nospatial=true",
        "lme_regions_spatial.json": f"{base}/lme/",
        "highseas_regions.json": f"{base}/highseas/?nospatial=true",
        "highseas_regions_spatial.json": f"{base}/highseas/",
    }
    units = load_units_from_spatial_index(ROOT / "spatial" / "spatial_units.csv")
    url_by_name.update(unit_source_urls(base, units))

    references = [
        PROJECT / "sources" / "1995_group2species(1).ipynb",
        PROJECT / "sources" / "Baltic_88-91_group2species(1).xlsx",
        PROJECT / "sources" / "2020 sup.xlsx",
        PROJECT / "sources" / "מאמר 1995.pdf",
        PROJECT / "sources" / "נספח 2020.docx",
        PROJECT / "sources" / "שיטת חישוב 2020.pdf",
    ]
    examples = sorted((ROOT / "input" / "examples").glob("*"))
    payload = {
        "generated_on": date.today().isoformat(),
        "notes": [
            "Reference files under sources are read-only and are not repackaged inside the pipeline directory.",
            "Sea Around Us downloads are frozen snapshots; rerunning with --overwrite may change checksums.",
        ],
        "inspected_references": [record(path) for path in references],
        "uploaded_examples": [record(path) for path in examples],
        "sea_around_us_inputs": [
            record(path, source_url=url_by_name[path.name])
            for path in sorted(raw_dir.glob("*"))
        ],
    }
    destination = ROOT / "input" / "provenance.json"
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
