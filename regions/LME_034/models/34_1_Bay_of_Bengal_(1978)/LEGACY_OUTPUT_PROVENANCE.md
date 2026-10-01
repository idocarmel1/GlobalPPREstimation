# Historical legacy workbook

`legacy_ppr.xlsx` is retained historical output from the earlier regional-workbook migration. It contains prior taxon mappings, annual PPR formulas, group coefficients and recycling diagnostics. It is not the active output for the current canonical model and must not be used as the final corrected result.

The migration code copies earlier `data/<region>/models/*.xlsx` workbooks to this filename (`tools/migrate.py`, line99). Current calculation refreshes write `sppr_source.xlsx` (`tools/run_region.py`, line57), and the atlas checks that active file (`tools/original_atlas_data.py`, line307). The exact original migration checkout is no longer present at the recorded pre-reorganization path; archived sensitivity snapshots are separate releases and have different checksums.

The historical workbook is retained unchanged, SHA256 `6d3de24f90203dc69086560d55f7e01e36809f898f88e7ec8d7c5c91324b487a`. It is a previous generated result, not an author-native balanced Ecopath database.

Use the current `sppr_source.xlsx`, regional `../../LME_034.xlsx`, central `../../../../Project.xlsx`, and [final correction summary](../../validation_reports/34_1_Bay_of_Bengal_(1978)/detritus_completion_20261001/handoff_summary.md) for the final researcher scenario. The original printed diets and the earlier raw reconstruction remain separate evidence layers.
