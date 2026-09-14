"""Independent validation of the TE=0.05 release against the TE=0.10 release."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "global_output" / "tables"
CANDIDATE_ROOT = ROOT / "global_output_te005"
CANDIDATE = CANDIDATE_ROOT / "tables"


def _read_species(table_root: Path, unit_ids: list[str]) -> pd.DataFrame:
    frames = []
    for unit_id in unit_ids:
        frame = pd.read_csv(table_root / "regions" / unit_id / "species.csv")
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def _bool_validation_passed(frame: pd.DataFrame) -> bool:
    checks = frame.loc[frame["unit"] == "boolean", "value"].astype(str).str.lower()
    return bool((checks == "true").all())


def main() -> None:
    baseline_summary = pd.read_csv(BASELINE / "global_summary.csv").sort_values("unit_id")
    candidate_summary = pd.read_csv(CANDIDATE / "global_te005_summary.csv").sort_values("unit_id")
    unit_ids = candidate_summary["unit_id"].tolist()

    assert len(unit_ids) == 84
    assert unit_ids == baseline_summary["unit_id"].tolist()
    assert set(candidate_summary["year"]) == {2019}
    assert np.allclose(
        candidate_summary["total_catch_tonnes"],
        baseline_summary["total_catch_tonnes"],
        rtol=0,
        atol=1e-6,
    )
    positive_catch = candidate_summary["total_catch_tonnes"] > 0
    assert (candidate_summary.loc[positive_catch, "catch_tl_coverage_fraction"] == 1).all()
    assert (
        candidate_summary.loc[~positive_catch, ["matched_catch_tonnes", "missing_tl_catch_tonnes"]]
        == 0
    ).all().all()
    assert int((candidate_summary["total_catch_tonnes"] == 0).sum()) == 2

    baseline_species = _read_species(BASELINE, unit_ids).sort_values(["unit_id", "taxon"])
    candidate_species = _read_species(CANDIDATE, unit_ids).sort_values(["unit_id", "taxon"])
    key_columns = ["unit_id", "taxon", "year", "catch_tonnes", "tl"]
    pd.testing.assert_frame_equal(
        candidate_species[key_columns].reset_index(drop=True),
        baseline_species[key_columns].reset_index(drop=True),
        check_exact=False,
        rtol=0,
        atol=1e-10,
    )

    candidate_catch = pd.to_numeric(candidate_species["catch_tonnes"])
    candidate_tl = pd.to_numeric(candidate_species["tl"])
    candidate_ppr = pd.to_numeric(candidate_species["ppr"])
    baseline_ppr_rows = pd.to_numeric(baseline_species["ppr"])
    expected_ppr = candidate_catch * np.power(20.0, candidate_tl - 1.0)
    assert np.allclose(candidate_ppr, expected_ppr, rtol=1e-12, atol=1e-6)

    positive = candidate_catch > 0
    actual_ratio = (
        candidate_ppr.loc[positive].to_numpy()
        / baseline_ppr_rows.loc[positive].to_numpy()
    )
    expected_ratio = np.power(2.0, candidate_tl.loc[positive] - 1.0)
    assert np.allclose(actual_ratio, expected_ratio, rtol=1e-12, atol=1e-12)
    assert (candidate_ppr.loc[positive] > baseline_ppr_rows.loc[positive]).all()

    validation = pd.read_csv(CANDIDATE / "validation.csv")
    assert _bool_validation_passed(validation)

    with (CANDIDATE / "run_metadata.json").open(encoding="utf-8") as handle:
        metadata = json.load(handle)
    assert metadata["transfer_efficiency"] == 0.05
    assert metadata["unit_count"] == 84
    assert metadata["lme_count"] == 66
    assert metadata["highseas_count"] == 18

    with (CANDIDATE_ROOT / "spatial" / "LMEs.geojson").open(encoding="utf-8") as handle:
        lmes = json.load(handle)
    with (CANDIDATE_ROOT / "spatial" / "HighSeas.geojson").open(encoding="utf-8") as handle:
        high_seas = json.load(handle)
    assert len(lmes["features"]) == 66
    assert len(high_seas["features"]) == 18

    total_catch = float(candidate_summary["total_catch_tonnes"].sum())
    total_ppr = float(candidate_summary["ppr_species"].sum())
    baseline_ppr = float(baseline_summary["ppr_species"].sum())
    weighted_commercial = float(candidate_summary["ppr_commercial"].sum())
    weighted_functional = float(candidate_summary["ppr_functional"].sum())
    # (1 / te) ** (TL - 1) is convex, so exponentiating a group's catch-weighted mean
    # trophic level can never exceed the sum over its taxa. The group totals must sit
    # at or below the taxon-level total; anything above it is a weighting or sign error.
    convexity_bound = 1e-10 * abs(total_ppr) + 1e-8
    assert weighted_commercial - total_ppr <= convexity_bound
    assert weighted_functional - total_ppr <= convexity_bound
    report = {
        "status": "passed",
        "scope_label": "global_te005",
        "year": 2019,
        "transfer_efficiency": 0.05,
        "unit_count": 84,
        "lme_count": 66,
        "highseas_count": 18,
        "zero_catch_unit_count": 2,
        "species_row_count": int(len(candidate_species)),
        "total_catch_tonnes": total_catch,
        "total_ppr_te005": total_ppr,
        "total_ppr_te010": baseline_ppr,
        "total_ppr_ratio_te005_to_te010": total_ppr / baseline_ppr,
        "commercial_total_ppr": weighted_commercial,
        "functional_total_ppr": weighted_functional,
        # The group figures use the catch-weighted mean trophic level, so they sit
        # below the taxon-level total by the Jensen gap. The corrected value has not
        # gone anywhere - it is ppr_species, the taxon-summed total - so the fraction
        # of PPR lost by aggregating taxa into groups is still 1 - group / species.
        "commercial_underestimate_fraction": 1.0 - weighted_commercial / total_ppr,
        "functional_underestimate_fraction": 1.0 - weighted_functional / total_ppr,
        "tl_catch_coverage_fraction": float(
            candidate_summary["matched_catch_tonnes"].sum() / total_catch
        ),
        "polygon_feature_counts": {"LME": 66, "High Seas": 18},
        "checks": {
            "catch_identical_to_te010": True,
            "species_keys_catch_and_tl_identical_to_te010": True,
            "te005_formula_exact_within_tolerance": True,
            "cross_release_ppr_ratio_equals_2_power_tl_minus_1": True,
            "all_boolean_pipeline_validations_passed": True,
            "group_ppr_never_above_taxon_summed_ppr": True,
            "polygon_counts_match_scope": True,
        },
    }
    destination = CANDIDATE_ROOT / "te005_validation_report.json"
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
