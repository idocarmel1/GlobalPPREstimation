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
    assert "commercial_ppr_reconciled" in text
    assert "functional_ppr_reconciled" in text
    assert "Jensen" in text
    assert sum(cell.cell_type == "code" for cell in notebook.cells) >= 5


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
