# SPPR and trophic level across reviewed ecosystem models

Researcher-owned exploration requested on 16 October 2026, with agent assistance.
It compares saved group SPPR coefficients against trophic level across eight
registered researcher-validated model-region pairs, with selected LME_027 groups
overlaid. Placement in human research does not confer scientific approval.

## Figures and results

- [GE versus TE, side by side](results/sppr_ge_te_side_by_side.png)
  ([scalable SVG](results/sppr_ge_te_side_by_side.svg)).
- [GE, EwE with EE multiplication, EwE without EE multiplication, and TE](results/sppr_methods_side_by_side.png)
  ([scalable SVG](results/sppr_methods_side_by_side.svg)).
- [Original TE comparison](results/sppr_vs_tl.png).
- [Per-group values for the four panels and retained restrictions](results/method_panel_data.json).
- [Trophic-level comparison, model summaries and LME_027 loop decomposition](results/comparison.json).
- [Original GE/TE/With Egestion group records](results/group_records.json).

The cohort comprises Eastern tropical Pacific (HS_077), Northern Humboldt
(LME_013), Guinea (LME_028), Arabian Sea off Karnataka (LME_032), Bay of Bengal
(LME_034), Gulf of Thailand (LME_035), Northern South China Sea (LME_036), and
East China Sea (LME_047). All 261 consumer groups, including unfished groups,
remain in the data. Positive finite values are shown on shared logarithmic axes;
zeros and unavailable coefficients remain explicit in the data and captions.

## Definitions and interpretation

The figures use the `all` basal-source scope and the saved floor-enabled
configurations, with floor 0.1. Trophic level is recovered from each group's
saved fixed-10% coefficient using `TL = 1 + log10(SPPR_1995_TE0.1)`. This matches
the engine's cycle-broken TL with detritus treated as basal. The dashed reference
is `s = 10^(TL - 1)`; it is a comparison curve, not an ecological acceptance limit.

GE and TE use the full network solver. The EwE variants use the engine's
simple-path methods, respectively with and without final EE row multiplication.
These are the saved `new_GE`, `new_TE_EEfix`, `EwE_TE_EE` and `EwE_TE_noEE`
variants; no new coefficient calculation was performed for this study.

The Bay of Bengal EwE-with-EE result is unavailable after a saved method timeout,
so that panel omits 44 groups. LME_027 has matching floor-ON GE/TE evidence but no
matching saved EwE results; its overlays appear only in the GE/TE panels.
Existing WARN, FAIL, provisional, implausibility and other restrictions are
retained. Researcher registration and transformed-result eligibility are separate.

SPPR generally increases with TL, but group efficiencies and feedback produce
large departures. In LME_027, group 13 (Mesopelagic predators, TL about 3.93) has
floor-ON TE SPPR about 1.06 million and GE SPPR about 254. Its TE self-loop gain
0.99071698 gives a feedback multiplier about 107.7. Group 7 (Beaked whales) has
floor-ON TE SPPR about 85.4 million. Other registered models also contain very
large coefficients; absolute SPPR alone is not the recycling diagnostic.

## Inputs and preservation

Canonical scientific inputs, result manifests, snapshots and signed reviews stay
model-local. [Source hashes](inputs/source_hashes.json) and the source references
inside the panel data identify the exact bytes used. Snapshots were checked
against manifests and their group coefficients reconciled with the plotted values.
These are pointers to existing sources, not frozen copies; changed hashes require
review before reproducing an updated comparison.

The [LME_027 floor-OFF/ON diagnostic package](../../../regions/LME/LME_027/papers/CAN-2009/models/27_118_Northwest_Africa_(1987)/model_validation/work/2026-10-15_091756_ee_floor_comparison/summary.md)
remains with that model. Its original signed review, registered disqualification,
regional workbooks, saved production results and map were preserved.

This package was moved intact from the regional comparison work folder at the
researcher's request. `outputs/` became `results/`, and `qa/` became `evidence/`.
The only changes to the three existing scripts are output-directory paths. All
original result, figure, input-hash and verification bytes are retained.
The [relocation inventory](inputs/relocation_source_inventory.json) records prior
paths and hashes; the central [source disposition ledger](../../../common_reference_data/provenance/source_paths.csv)
records the retained paths and hashes.

## Reproduce the saved-data analysis

Use Python 3.11 or newer with NumPy, SciPy and Matplotlib, from the repository root:

```powershell
python research/human/sppr_trophic_level_20261016/code/analyze.py
python research/human/sppr_trophic_level_20261016/code/plot_method_panels.py
python research/human/sppr_trophic_level_20261016/code/plot_ge_te.py
```

These commands read current saved source files and overwrite only this study's
derived results and evidence. They do not run a scientific calculator, migrate
floor settings, alter scientific inputs or update researcher decisions. Preserve
the recorded version in Git before intentionally regenerating against changed
sources. The unchanged plot-generation logic was visually inspected before the
relocation; hash and path checks verify the relocated package.
