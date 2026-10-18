# Seven-pair catch and trophic-level decomposition

This 18 October 2026 successor recomputes the 2019 aggregation analysis after the exact Guinea 1998 model-region pair lost researcher approval. The [16 October run](../2026-10-16_202757_trophic_aggregation/outputs/decomposition.json) remains unchanged historical evidence. This is a cross-model analysis stored in the authorized regional work location; its location does not make Guinea part of the current cohort.

The [cohort](inputs/cohort.json) is byte-identical to the manifest in the [new SPPR/TL study](../../../../../research/human/sppr_trophic_level_20261018_validated7/README.md). Registry and signed-report hashes, the published selected model identities, and each consumed regional workbook are checked. No calculator runs or scientific workbook changes occur.

The new calculation contains seven model-region pairs, 165 groups with positive allocated catch, 1,693 included region-taxon records and 39,684,336.471269056 tonnes of allocated catch. It retains total catch including discards, full payload precision, original allocation shares, review default exclusions and unavailable-value restrictions. Omitted shares are not renormalized.

The taxon simple-chain total divided by saved grouped classic PPR is **1.8512001942**. The pure Jensen factor is **1.2371218415** and the mean-TL/convention centering factor is **1.4963766156**. The saved all-source TE reconstruction is **3,051,528,527.3165097 tC**. Multiplying every group by its full residual Jensen factor gives **3,608,310,468.531145 tC**, an exploratory sensitivity factor of **1.1824600151**. This is not an identified correction: it can double-count heterogeneity already represented by network paths and does not approve restricted annual results.

## Results and verification

- [Full decomposition, groups and input checks](outputs/decomposition.json).
- [Replay of the functions embedded in the current published view](outputs/browser_compare.json).
- [Compact comparison](outputs/summary.json).
- [Script lineage](inputs/code_derivation.json).
- [Independent retained-row verification](../../../../../research/human/sppr_trophic_level_20261018_validated7/evidence/source_subset_verification.json).

All totals were recomputed from individual taxon allocations. The independent verification compares retained group and regional rows, rather than deriving a new total by subtracting Guinea from a previous aggregate.

## Reproduce

First run the new SPPR/TL analysis so that its cohort manifest records the current signed registry. From the repository root:

```powershell
$run = 'regions/LME/LME_028/work/2026-10-18_121535_trophic_aggregation_validated7'
node "$run/code/browser_compare.cjs" | Set-Content -Encoding utf8 "$run/outputs/browser_compare.json"
python "$run/code/decompose.py"
python research/human/sppr_trophic_level_20261018_validated7/code/verify_saved_subset.py
```

The browser replay requires Node.js. The Python decomposition reads saved tables and writes only this run's outputs and its cohort copy. It fails when registry, published view, review source, workbook or cohort identities disagree.
