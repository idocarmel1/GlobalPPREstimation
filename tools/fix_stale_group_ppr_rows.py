"""Recompute the stale commercial_ppr/functional_ppr/*_ppr_difference rows.

These four rows in every validation.csv were last computed by a pipeline run
that predates the Jensen-only group aggregation: at that time
ppr_pipeline.validation._sum_ppr(commercial) effectively summed the old
"correct" (sum-of-matched-taxon) aggregation, so commercial_ppr/functional_ppr
came out equal to species_ppr exactly and the *_ppr_difference rows were all
0. Migrating the schema (tools/migrate_group_columns.py,
tools/migrate_validation_checks.py) did not touch these five numeric rows -
they were out of scope for that step - but left every validation.csv
asserting the group aggregation reconciles with the taxon sum, which is the
opposite of what commercial.csv/functional.csv's single Jensen-affected `ppr`
column now means. This script closes that gap by recomputing four of those
five rows directly from the migrated data sitting beside each validation.csv:

    commercial_ppr             = sum(commercial.csv['ppr'])
    functional_ppr              = sum(functional.csv['ppr'])
    commercial_ppr_difference   = commercial_ppr - species_ppr
    functional_ppr_difference   = functional_ppr - species_ppr

species_ppr itself is NOT recomputed or overwritten: it is the taxon-level
sum, untouched by the schema change, and is verified (not assumed) against
each unit's species.csv before use - if any unit disagrees, this script
raises rather than propagating a wrong number.

group_ppr_within_convexity_bound is then re-derived from the corrected
differences, using the same one-sided bound and tolerance (1e-10) as
ppr_pipeline.validation.validate_region, so it is computed from the same
inputs as the rows now beside it rather than independently.

float_precision="round_trip" is used on every read, for the same reason
tools/migrate_group_columns.py needs it: pandas' default C float parser is
not correctly rounded and can perturb an untouched value by ~1 ULP on a
read-then-rewrite round trip.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

TOLERANCE = 1e-10
TARGET_CHECKS = (
    "commercial_ppr",
    "functional_ppr",
    "commercial_ppr_difference",
    "functional_ppr_difference",
    "group_ppr_within_convexity_bound",
)


def unit_dir_for(validation_path: Path, unit_id: str) -> Path:
    if validation_path.parent.name == unit_id:
        return validation_path.parent
    return validation_path.parent / "regions" / unit_id


def fix_file(path: Path) -> dict:
    df = pd.read_csv(path, encoding="utf-8-sig", float_precision="round_trip")
    violations = []
    changed_units = 0
    for unit_id in df["unit_id"].unique():
        unit_dir = unit_dir_for(path, unit_id)
        species = pd.read_csv(unit_dir / "species.csv", encoding="utf-8-sig", float_precision="round_trip")
        commercial = pd.read_csv(unit_dir / "commercial.csv", encoding="utf-8-sig", float_precision="round_trip")
        functional = pd.read_csv(unit_dir / "functional.csv", encoding="utf-8-sig", float_precision="round_trip")

        matched = species.loc[species["tl"].notna()]
        recomputed_species_ppr = float(pd.to_numeric(matched["ppr"], errors="coerce").sum())
        mask_species = (df["unit_id"] == unit_id) & (df["check"] == "species_ppr")
        assert mask_species.sum() == 1, f"{path}/{unit_id}: expected exactly one species_ppr row"
        stored_species_ppr = float(df.loc[mask_species, "value"].iloc[0])
        if abs(stored_species_ppr - recomputed_species_ppr) > 1e-6 + 1e-9 * abs(recomputed_species_ppr):
            raise AssertionError(
                f"{path}/{unit_id}: species_ppr disagrees with species.csv: "
                f"stored={stored_species_ppr} recomputed={recomputed_species_ppr}"
            )
        species_ppr = stored_species_ppr  # use the existing, verified-non-stale row as-is

        commercial_ppr = float(pd.to_numeric(commercial["ppr"], errors="coerce").sum())
        functional_ppr = float(pd.to_numeric(functional["ppr"], errors="coerce").sum())
        commercial_diff = commercial_ppr - species_ppr
        functional_diff = functional_ppr - species_ppr
        convexity_bound = TOLERANCE * abs(species_ppr) + 1e-8
        convexity_ok = bool(commercial_diff <= convexity_bound and functional_diff <= convexity_bound)

        new_values = {
            "commercial_ppr": commercial_ppr,
            "functional_ppr": functional_ppr,
            "commercial_ppr_difference": commercial_diff,
            "functional_ppr_difference": functional_diff,
            "group_ppr_within_convexity_bound": convexity_ok,
        }
        for check, value in new_values.items():
            mask = (df["unit_id"] == unit_id) & (df["check"] == check)
            assert mask.sum() == 1, f"{path}/{unit_id}/{check}: expected exactly one row, found {mask.sum()}"
            df.loc[mask, "value"] = value
        changed_units += 1

        if not convexity_ok:
            violations.append((unit_id, commercial_diff, functional_diff, convexity_bound))

    df.to_csv(path, index=False, encoding="utf-8-sig")
    return {"units": changed_units, "violations": violations}


def main() -> int:
    total_units = 0
    all_violations = []
    for root in (Path("SeaAroundUsExtraction/global_output"), Path("SeaAroundUsExtraction/eez_output")):
        if not root.exists():
            continue
        for f in sorted(root.rglob("validation.csv")):
            result = fix_file(f)
            print(f"  {f}: recomputed 5 rows for {result['units']} unit(s)")
            total_units += result["units"]
            all_violations.extend((f, *v) for v in result["violations"])
    print(f"\nrecomputed rows for {total_units} unit-file entries")
    if all_violations:
        print(f"CONVEXITY VIOLATIONS FOUND ({len(all_violations)}):")
        for f, unit_id, cdiff, fdiff, bound in all_violations:
            print(f"  {f} {unit_id}: commercial_diff={cdiff} functional_diff={fdiff} bound={bound}")
    else:
        print("no convexity violations - group_ppr_within_convexity_bound holds for every unit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
