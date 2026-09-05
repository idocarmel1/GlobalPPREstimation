"""Create a checksummed manifest for the completed global deliverables."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "global_output"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    summary = pd.read_csv(OUTPUT / "tables" / "global_summary.csv")
    validation = pd.read_csv(OUTPUT / "tables" / "validation.csv")
    boolean = validation.loc[
        validation["check"].isin(
            [
                "catch_reconciled",
                "commercial_ppr_reconciled",
                "functional_ppr_reconciled",
            ]
        ),
        "value",
    ].astype(str).str.lower().isin(["true", "1", "1.0"])
    violations = pd.to_numeric(
        validation.loc[
            validation["check"].str.endswith("jensen_violations"), "value"
        ]
    )
    files = []
    destination = OUTPUT / "deliverable_manifest.json"
    for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file()):
        if path == destination:
            continue
        files.append(
            {
                "path": path.relative_to(OUTPUT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "all Sea Around Us-defined LMEs and High Seas units",
        "year": int(summary["year"].iloc[0]),
        "unit_count": int(len(summary)),
        "lme_count": int((summary["region_type"] == "LME").sum()),
        "highseas_count": int((summary["region_type"] == "High Seas").sum()),
        "zero_catch_units": summary.loc[
            summary["total_catch_tonnes"].eq(0), "unit_id"
        ].tolist(),
        "total_catch_tonnes": float(summary["total_catch_tonnes"].sum()),
        "total_ppr_tonnes_primary_production_equivalent": float(
            summary["ppr_species"].sum()
        ),
        "validation": {
            "reconciliation_failures": int((~boolean).sum()),
            "jensen_violations": int(violations.sum()),
        },
        "workbook_count": sum(item["path"].endswith(".xlsx") for item in files),
        "files": files,
    }
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(destination)


if __name__ == "__main__":
    main()
