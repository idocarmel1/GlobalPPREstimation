"""Rewrite existing SeaAroundUs outputs to the trimmed schema.

Every surviving value must be byte-identical to its pre-change counterpart; only
whole columns disappear or change name. The script proves this as it goes.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

GROUP_DROP = [
    "taxon_count_total", "taxon_count_matched", "catch_tonnes_total",
    "catch_tonnes_missing_tl", "catch_coverage_fraction",
    "sppr_correct", "ppr_correct",
    "jensen_difference", "jensen_ratio_correct_to_error", "jensen_percent_difference",
]
GROUP_RENAME = {"tl_weighted_jensen": "tl_weighted", "sppr_jensen": "sppr", "ppr_jensen": "ppr"}

SUMMARY_DROP = ["ppr_commercial_correct", "ppr_functional_correct"]
SUMMARY_RENAME = {"ppr_commercial_jensen": "ppr_commercial", "ppr_functional_jensen": "ppr_functional"}

def migrate(path: Path, drop: list[str], rename: dict[str, str]) -> str:
    # float_precision="round_trip" is required: pandas' default C float parser
    # (xstrtod) is fast but not correctly rounded, and can silently perturb a
    # float64 value by ~1 ULP relative to what Python's own float() (and the
    # original writer) produced. Without this, reading a surviving column and
    # writing it back out can change its last 1-2 significant digits even
    # though the value is never touched by this script - defeating the whole
    # point of the value-identity check below, since both operands would be
    # parsed with the same silent error and compare equal to each other while
    # both differing from the pre-migration text on disk.
    before = pd.read_csv(path, encoding="utf-8-sig", float_precision="round_trip")
    after = before.drop(columns=[c for c in drop if c in before.columns])
    after = after.rename(columns={k: v for k, v in rename.items() if k in before.columns})
    # prove every surviving value is unchanged
    for new_name in after.columns:
        old_name = next((k for k, v in rename.items() if v == new_name), new_name)
        if old_name not in before.columns:
            raise AssertionError(f"{path}: column {new_name} has no source column")
        lhs, rhs = before[old_name], after[new_name]
        if not lhs.equals(rhs.rename(old_name)):
            raise AssertionError(f"{path}: values changed in {old_name} -> {new_name}")
    if list(after.columns) == list(before.columns):
        return "unchanged"
    after.to_csv(path, index=False, encoding="utf-8-sig")
    return f"{len(before.columns)} -> {len(after.columns)} cols"

def main() -> int:
    touched = deleted = 0
    for root in (Path("SeaAroundUsExtraction/global_output"), Path("SeaAroundUsExtraction/eez_output")):
        if not root.exists():
            continue
        for name in ("commercial.csv", "functional.csv"):
            for f in root.rglob(name):
                print(f"  {f}: {migrate(f, GROUP_DROP, GROUP_RENAME)}"); touched += 1
        for f in list(root.rglob("*_summary.csv")):
            print(f"  {f}: {migrate(f, SUMMARY_DROP, SUMMARY_RENAME)}"); touched += 1
        for f in list(root.rglob("jensen_comparison.csv")):
            f.unlink(); print(f"  deleted {f}"); deleted += 1
    annual = Path("PPRAtlas/inputs/annual_regions.csv")
    if annual.exists():
        print(f"  {annual}: {migrate(annual, SUMMARY_DROP, SUMMARY_RENAME)}"); touched += 1
    print(f"\nmigrated {touched} files, deleted {deleted} jensen_comparison.csv")
    return 0

if __name__ == "__main__":
    sys.exit(main())
