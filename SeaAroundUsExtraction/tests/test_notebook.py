from __future__ import annotations

import nbformat

from ppr_pipeline.notebook import build_scope_validation_notebook, build_validation_notebook


def test_validation_notebook_contains_required_scientific_checks(tmp_path) -> None:
    output = tmp_path / "pilot_validation.ipynb"
    build_validation_notebook(output)
    notebook = nbformat.read(output, as_version=4)
    text = "\n".join("".join(cell.source) for cell in notebook.cells)
    assert "SPPR = 10" in text
    assert "catch_reconciled" in text
    assert "tl_coverage_complete" in text
    assert sum(cell.cell_type == "code" for cell in notebook.cells) >= 5


def test_validation_notebook_has_no_jensen_comparison(tmp_path) -> None:
    output = tmp_path / "pilot_validation.ipynb"
    build_validation_notebook(output)
    notebook = nbformat.read(output, as_version=4)
    text = "\n".join("".join(cell.source) for cell in notebook.cells)
    assert "jensen_comparison.csv" not in text
    assert "jensen_violations" not in text
    assert "Jensen" not in text
    assert "ppr_correct" not in text


def test_scope_validation_notebook_has_no_jensen_comparison(tmp_path) -> None:
    output = tmp_path / "global_validation.ipynb"
    build_scope_validation_notebook(
        output,
        scope_label="global",
        output_directory="global_output",
        unit_description="all 66 LMEs and 18 High Seas units",
    )
    notebook = nbformat.read(output, as_version=4)
    text = "\n".join("".join(cell.source) for cell in notebook.cells)
    assert "jensen_comparison.csv" not in text
    assert "jensen_violations" not in text
    assert "Jensen" not in text
    assert "ppr_correct" not in text
    assert "tl_coverage_complete" in text


def test_global_validation_notebook_targets_global_outputs(tmp_path) -> None:
    output = tmp_path / "global_validation.ipynb"
    build_scope_validation_notebook(
        output,
        scope_label="global",
        output_directory="global_output",
        unit_description="all 66 LMEs and 18 High Seas units",
    )
    notebook = nbformat.read(output, as_version=4)
    text = "\n".join("".join(cell.source) for cell in notebook.cells)
    assert "global_output" in text
    assert "global_summary.csv" in text
    assert "rank_global_ppr" in text
    assert "all 66 LMEs and 18 High Seas units" in text


def _notebook_text(path) -> str:
    return "\n".join("".join(cell.source) for cell in nbformat.read(path, as_version=4).cells)


def _build_both(tmp_path):
    pilot = build_validation_notebook(tmp_path / "pilot_validation.ipynb")
    scope = build_scope_validation_notebook(
        tmp_path / "global_validation.ipynb",
        scope_label="global",
        output_directory="global_output",
        unit_description="all 66 LMEs and 18 High Seas units",
    )
    return pilot, scope


def test_notebook_builders_guard_against_an_empty_validation_check_selection(tmp_path) -> None:
    """Selecting checks by name and calling .all() passes vacuously on an empty frame.

    Both builders' reconciliation cells do exactly that, so a removed or renamed
    check would be reported as a pass. The generated cells must assert the expected
    names are present in validation.csv before evaluating them.
    """
    for output in _build_both(tmp_path):
        text = _notebook_text(output)
        assert "missing_checks" in text
        assert "assert not missing_checks" in text
        assert "assert not boolean_checks.empty" in text


def test_notebook_boolean_check_names_are_the_boolean_checks_validate_region_emits() -> None:
    """Tripwire: a renamed check must break here, not silently narrow a pandas filter."""
    import pandas as pd

    from ppr_pipeline import calculations, notebook, validation

    species = pd.DataFrame(
        {
            "commercial_group": ["Cod-likes", "Anchovies"],
            "functional_group": ["Large demersals", "Small pelagics"],
            "catch_tonnes": [10.0, 5.0],
            "tl": [4.0, 3.0],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    result = validation.validate_region(
        "LME_003",
        species,
        calculations.aggregate_groups(species, "commercial_group", te=0.1),
        calculations.aggregate_groups(species, "functional_group", te=0.1),
        raw_filtered_tonnes=15.0,
    )
    emitted = set(result.loc[result["unit"] == "boolean", "check"])

    assert emitted
    assert set(notebook.BOOLEAN_CHECK_NAMES) == emitted


def test_notebook_reconciliation_cells_assert_the_convexity_invariant(tmp_path) -> None:
    """Group PPR <= taxon-summed PPR is the invariant the notebooks must still gate on."""
    for output in _build_both(tmp_path):
        assert "group_ppr_within_convexity_bound" in _notebook_text(output)
