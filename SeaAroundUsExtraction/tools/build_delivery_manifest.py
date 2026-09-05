"""Create a checksummed manifest for the completed global deliverables."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

# Named, rather than inlined as string literals in main(), so a test can assert
# these are still checks that validate_region actually emits. When
# ppr_pipeline.validation.validate_region's check names change, that test - not a
# silently-narrowed pandas filter - is what should fail.
BOOLEAN_CHECK_NAMES = ("catch_reconciled", "tl_coverage_complete")
JENSEN_GAP_CHECK_NAMES = ("commercial_ppr_difference", "functional_ppr_difference")
QUERIED_CHECK_NAMES = BOOLEAN_CHECK_NAMES + JENSEN_GAP_CHECK_NAMES


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", default="global_output")
    parser.add_argument("--scope-label", default="global")
    args = parser.parse_args()
    if not args.output_directory.replace("_", "").replace("-", "").isalnum():
        raise ValueError("Output directory must be a simple relative name.")
    output = ROOT / args.output_directory
    summary = pd.read_csv(output / "tables" / f"{args.scope_label}_summary.csv")
    validation = pd.read_csv(output / "tables" / "validation.csv")
    boolean = validation.loc[
        validation["check"].isin(BOOLEAN_CHECK_NAMES),
        "value",
    ].astype(str).str.lower().isin(["true", "1", "1.0"])
    # commercial_ppr_difference / functional_ppr_difference are the group PPR minus
    # the taxon-summed PPR (see ppr_pipeline.validation.validate_region). With the
    # corrected group aggregation removed, these differences are the Jensen gap
    # itself, so their sums are what is worth reporting here now - not a violation
    # count against a comparison that no longer exists.
    commercial_check, functional_check = JENSEN_GAP_CHECK_NAMES
    commercial_ppr_gap = float(
        pd.to_numeric(validation.loc[validation["check"] == commercial_check, "value"]).sum()
    )
    functional_ppr_gap = float(
        pd.to_numeric(validation.loc[validation["check"] == functional_check, "value"]).sum()
    )
    files = []
    destination = output / "deliverable_manifest.json"
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        if path == destination:
            continue
        files.append(
            {
                "path": path.relative_to(output).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "all Sea Around Us-defined LMEs and High Seas units",
        "scope_label": args.scope_label,
        "transfer_efficiency": float(
            json.loads((output / "tables" / "run_metadata.json").read_text())["transfer_efficiency"]
        ),
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
            "total_commercial_ppr_difference": commercial_ppr_gap,
            "total_functional_ppr_difference": functional_ppr_gap,
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
