"""Tripwire test for build_delivery_manifest.py's validation-check name coupling.

build_delivery_manifest.py queries ppr_pipeline.validation.validate_region's output
by check name as string literals, with nothing tying those names to what
validate_region actually emits. When Task 6 renamed/removed
commercial_ppr_reconciled, functional_ppr_reconciled and the *_jensen_violations
checks, the manifest's pandas filters silently matched fewer (or zero) rows instead
of raising - reconciliation_failures undercounted and jensen_violations reported a
hardcoded-looking 0 for a check that no longer runs.

This test asserts every check name the manifest tool queries (exposed as module
constants, not buried string literals) is a name validate_region actually emits, so
a future rename breaks this test instead of silently degrading the manifest.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

from ppr_pipeline import calculations, validation


def _load_manifest_module():
    path = Path(__file__).parents[1] / "tools" / "build_delivery_manifest.py"
    spec = importlib.util.spec_from_file_location("build_delivery_manifest_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_region_result() -> pd.DataFrame:
    """A real validate_region() result, so tests read the current check names."""
    species = pd.DataFrame(
        {
            "commercial_group": ["Cod-likes", "Anchovies"],
            "functional_group": ["Large demersals", "Small pelagics"],
            "catch_tonnes": [10.0, 5.0],
            "tl": [4.0, 3.0],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    commercial = calculations.aggregate_groups(species, "commercial_group", te=0.1)
    functional = calculations.aggregate_groups(species, "functional_group", te=0.1)
    return validation.validate_region(
        "LME_003", species, commercial, functional, raw_filtered_tonnes=15.0
    )


def _validate_region_check_names() -> set[str]:
    """The real, current set of check names validate_region emits."""
    return set(_validate_region_result()["check"])


def _validate_region_boolean_check_names() -> set[str]:
    """Just the checks validate_region labels as boolean pass/fail results."""
    result = _validate_region_result()
    return set(result.loc[result["unit"] == "boolean", "check"])


def test_manifest_queried_check_names_are_all_emitted_by_validate_region():
    module = _load_manifest_module()
    known_checks = _validate_region_check_names()

    assert module.QUERIED_CHECK_NAMES, "the manifest must name at least one check it queries"
    missing = set(module.QUERIED_CHECK_NAMES) - known_checks
    assert not missing, (
        f"build_delivery_manifest.py queries checks validate_region no longer emits: {missing}. "
        "Update tools/build_delivery_manifest.py's BOOLEAN_CHECK_NAMES / "
        "JENSEN_GAP_CHECK_NAMES to match the renamed/removed check(s)."
    )


def test_manifest_boolean_check_names_cover_every_boolean_check_validate_region_emits():
    """reconciliation_failures must count *all* the boolean checks, not just some.

    The previous version of this test compared BOOLEAN_CHECK_NAMES against
    QUERIED_CHECK_NAMES, which is defined as BOOLEAN_CHECK_NAMES + JENSEN_GAP_CHECK_NAMES
    - a subset assertion that was true by construction and could never fail. This
    compares the manifest's list against the boolean checks validate_region actually
    emits, so adding a boolean check to validate_region without teaching the manifest
    about it (silently undercounting reconciliation_failures - the exact bug this file
    exists to prevent) fails here.
    """
    module = _load_manifest_module()
    emitted = _validate_region_boolean_check_names()

    assert emitted, "validate_region must emit at least one boolean check"
    assert set(module.BOOLEAN_CHECK_NAMES) == emitted, (
        "tools/build_delivery_manifest.py's BOOLEAN_CHECK_NAMES is out of step with the "
        f"boolean checks validate_region emits. Only in the manifest: "
        f"{set(module.BOOLEAN_CHECK_NAMES) - emitted}; only in validate_region: "
        f"{emitted - set(module.BOOLEAN_CHECK_NAMES)}."
    )


def test_manifest_reports_reconciliation_failures_and_no_bare_jensen_violations_field():
    """The manifest must not claim a jensen_violations result it never computes."""
    import inspect

    module = _load_manifest_module()
    source = inspect.getsource(module.main)
    assert '"jensen_violations"' not in source
    assert '"reconciliation_failures"' in source
