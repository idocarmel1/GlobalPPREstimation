# HS_077 diet-entry misplacement hypothesis tests

Date: 2026-10-08. Status: **five corrections adopted in model.json by explicit researcher instruction**.

Five intact entries moved between adjacent predator columns bring all nine material diet discrepancies to exactly **1.000**. This is the unique minimum solution within the bounded adjacent-entry search described below. It is arithmetic evidence for local placement errors, not confirmation of the authors' intended diets or ecological validity.

## Scope and source

The researcher requested different misplaced-table-entry hypotheses and excluded rounding errors. Tests used exact integer thousandths, retained diet imports, and excluded Albacore (group 18, 1.001) from both scoring and changes. No normalization, value adjustment, splitting or merging was tested. During the hypothesis-test stage, no canonical model, validation DOCX, workbook, result, selection or map was edited. The subsequent authorized adoption is recorded below.

Input: [preserved pre-correction model](original_model.json). Publication: [Olson and Watters (2003)](../../sources/Olson_Watters_2003_ETP-c037fcbc.pdf), Table 3a, printed pp. 158–159 / PDF pages 28–29. Table 3b, pp. 160–161 / PDF pages 30–31, repeats the placements. The source images were inspected; the suspicious placements are printed in the publication, rather than introduced by JSON conversion.

Only the sum of printed numeric diet entries plus the known import is evaluated. Printed blank positions are available destinations in the placement hypotheses. Unknown `-9999` entries are excluded from relocation and remain unknown; this test does not resolve their missingness.

## Hypotheses tested

| Family | Trials | Finding |
|---|---:|---|
| Move an intact entry to another prey row within the same predator column | 2,340 | No diet total changes; cannot explain a non-unit total. |
| Move one same-prey entry into a blank among the nine affected predators | 368 | Exactly three candidates restore two diets each: the 0.022, 0.575 and 0.070 moves below. No single move resolves all cases. |
| Swap adjacent same-prey cells, including blanks | 416 | The same three pair solutions; no alternative single swap resolves the swordfish–dorado–wahoo trio. |
| Permute one prey row within affected blocks 11–12, 22–23 or 25–29 | 936 | Each block has exactly one full-block solution: row 22 for 11–12; row 32 for the other two blocks. |
| Shift a whole prey row one column left/right within a printed 18-column panel, preserving numeric mass | 82 | No complete solution. The best shift (row 32, predators 19–36, right) restores five material cases but changes seven balanced controls. |
| Combine five adjacent intact-entry relocations | Six possible five-edge sets; one admissible cell assignment | One complete solution, listed below. All nine become exactly 1.000; every other consumer remains unchanged. |

Counts include different hypothesis families that can describe the same placement change. They are not counts of independent scientific evidence. The five-edge search uses exact conservation to reject infeasible edge sets before choosing cells.

## Adopted moves

| Prey row | Value | From predator | To predator | Source locator |
|---|---:|---|---|---|
| 22 — Small bigeye tuna | 0.022 | 11 — Large sailfish | 12 — Large swordfish | Table 3a, p. 158 / PDF 28, row 22 |
| 32 — Misc. mesopelagic fishes | 0.575 | 23 — Small marlins | 22 — Small bigeye tuna | Table 3a, p. 159 / PDF 29, row 32 |
| 32 — Misc. mesopelagic fishes | 0.121 | 25 — Small swordfish | 26 — Small dorado | Same row |
| 32 — Misc. mesopelagic fishes | 0.030 | 26 — Small dorado | 27 — Small wahoo | Same row |
| 32 — Misc. mesopelagic fishes | 0.070 | 28 — Small sharks | 29 — Miscellaneous piscivores | Same row |

The 0.121 and 0.030 moves are simultaneous: the existing 0.030 moves out of predator 26, and 0.121 takes its place. They are replacements of positions, not addition of the two values. All other destinations are printed blank.

For predators 25–29, the row-32 sequence changes from `[0.121, 0.030, blank, 0.070, blank]` to `[blank, 0.121, 0.030, blank, 0.070]`. Predators 21 and 24 and their already balanced diets remain unchanged. The pattern requires local displacements rather than shifting the entire row.

## Resulting totals

| Predator | Pre-correction total | Corrected model total |
|---|---:|---:|
| 11 — Large sailfish | 1.022 | 1.000 |
| 12 — Large swordfish | 0.978 | 1.000 |
| 22 — Small bigeye tuna | 0.425 | 1.000 |
| 23 — Small marlins | 1.575 | 1.000 |
| 25 — Small swordfish | 1.121 | 1.000 |
| 26 — Small dorado | 0.909 | 1.000 |
| 27 — Small wahoo | 0.970 | 1.000 |
| 28 — Small sharks | 1.070 | 1.000 |
| 29 — Miscellaneous piscivores | 0.930 | 1.000 |

The excesses and deficits sum to exactly zero. The trio closes as follows: swordfish loses 0.121; dorado gains 0.121 and loses 0.030, a net gain of 0.091; wahoo gains 0.030. Albacore remains 1.001 and was not tested as an error to repair. All 26 initially balanced consumers remain exactly 1.000.

## Minimality and limits

One relocation affects at most two consumer totals, so nine affected consumers require at least five relocations. For adjacent moves among the affected columns there are six available edges: 11–12, 22–23, 25–26, 26–27, 27–28 and 28–29. Every five-edge subset was evaluated by conservation of each connected component and the exact required flow across each edge. Only the subset omitting 27–28 is feasible. Each required flow has a unique matching intact source entry; the joint destination occupancy check gives one solution.

The unique/minimum claim is limited to unchanged-value, same-prey moves between adjacent material-discrepancy columns, with no splitting, merging or alteration of imports, controls or Albacore. It is not an exhaustive uniqueness claim for arbitrary nonadjacent multi-entry exchanges, row-and-column rearrangements or numerical edits. The single-move search did allow nonadjacent destinations among affected consumers, but did not exhaust arbitrary combinations of such moves.

Additional historical support for the strongest pair: Appendix Table 2a (initial ETP1 model), p. 215 / PDF 85, assigns mesopelagic fishes 0.570 to **Small bigeye tuna** and leaves **Small marlins** blank for this prey. IDs differ between model versions; this comparison uses group names. It supports the proposed destination but does not establish that the final ETP7 value 0.575 was intended there. It is not a rounding test or an adopted reconstruction.

## Verification and reproduction

The computation verified exact unit totals for all nine material cases, unchanged totals for every other consumer, unchanged prey-row totals, and an unchanged multiset of positive numerical entries. Imports and unknowns remain untouched. The canonical model and original PDF hashes were identical before and after execution.

- Model SHA-256: `9cc8a41414194be6f40f4fafd9d6ed23c38a1c5812acd55e6e39824e783c2998`
- Original PDF SHA-256: `c037fcbcc0ac55852fdf73ed8c24801b57b40c5ef5be7124360557f911f0179b`
- [Reproduction script](model_validation/work/2026-10-08_135441_diet_misplacement/code/test_hypotheses.py): run with Python from any working directory; its project-root lookup is anchored to this model-local run.
- [Machine-readable summary](model_validation/work/2026-10-08_135441_diet_misplacement/outputs/test_summary.json)
- [All scored trials](model_validation/work/2026-10-08_135441_diet_misplacement/outputs/hypothesis_trials.csv)
- [Proposed moves and source locators](model_validation/work/2026-10-08_135441_diet_misplacement/outputs/proposed_moves.csv)
- [All consumer totals](model_validation/work/2026-10-08_135441_diet_misplacement/outputs/consumer_totals.csv)

No loader, SPPR, ecological diagnostics or downstream calculation was run in the hypothesis-test stage. The CSV trial outputs retain that historical stage and its proposal labels.


## Researcher-authorized adoption — 2026-10-08

The researcher explicitly instructed: “change the current model.json to original_model.json” and “create a new model.json with these corrections”. The former canonical bytes are preserved as [original_model.json](original_model.json). The five moves above are now applied to [model.json](model.json) within the existing model folder and identity, as requested. Adoption records the researcher's decision; it does not establish author confirmation.

- Preserved original SHA-256: `9cc8a41414194be6f40f4fafd9d6ed23c38a1c5812acd55e6e39824e783c2998`
- Corrected model SHA-256: `86cd1a54316e1cdd401e49355a2a75f65f462e15d21c287b55f9894ec54c6e84`
- All nine material totals are exactly 1.000. Albacore remains 1.001.
- All non-diet fields, imports, unknown markers, group names/IDs and metadata were verified unchanged; the complete multiset of diet entries is preserved.
- [Exact before/after cell ledger and verification](model_validation/work/2026-10-08_135441_diet_misplacement/qa/adoption_verification.json)

This report was moved to the model root at the researcher's request and its relative links were rebased. The existing Word validation, SPPR, diagnostics, regional results and map remain historical pre-correction artifacts. They have not been refreshed or certified equivalent to the corrected input.
