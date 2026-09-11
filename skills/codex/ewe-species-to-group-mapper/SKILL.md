---
name: ewe-species-to-group-mapper
description: "Use when mapping an ecosystem's catch taxa to the exact functional groups of an existing Ecopath/EwE model, including coarse taxa, composite splits, membership evidence and mapping validation. Requires a GlobalPPREstimation checkout with catch data and SPPR workbooks."
---

# Map catch taxa to Ecopath groups

Build one auditable mapping per model. Read [the full mapping workflow](references/workflow.md)
and [output-format.md](references/output-format.md) for inputs, evidence codes,
sidecar files and required reporting.

Resolve this skill's directory as the skill root and the checkout as the repository
root. Bundled `scripts/`, `references/`, `assets/` and `examples/` paths use the skill
root, including inside references. Use quoted absolute script paths. Set
`GLOBALPPR_ROOT` to the checkout for mapping scripts invoked from elsewhere;
run repository `tools/` commands from that checkout.

1. Run `scripts/prepare_mapping.py <unit>`. Check model usability, then read the
   resulting work order and exact `groups_df` names.
2. Read [model-structures.md](references/model-structures.md). Establish the
   grouping axis, geographic coverage, prefixes and life-stage/spatial splits.
3. Search papers and supplements for the model's species membership. Transcribe
   any member table to `<stem>.members.csv` before assigning taxa. Inspect actual
   `taxon_descr` values; older models may be blank, newer ones may be populated.
   Distinguish exhaustive composition from diet-study examples; absence alone
   neither excludes a species nor requires a composite weight.
4. Work in catch-tonnage order. A documented member or synonym takes precedence
   over Sea Around Us habitat/size classes. For coarse labels, read
   [coarse-taxa-playbook.md](references/coarse-taxa-playbook.md) and specify the
   supported candidate groups. Leave weights blank for the documented catch-based
   fallback, or give an evidenced basis. Never choose a feeding guild from TL alone.
5. Run `scripts/validate_mapping.py <unit>`. Address errors and inspect coarse
   candidate sets against the sources: a validator pass cannot prove ecological
   correctness. Keep genuinely unsupported/out-of-model taxa `Unresolved`.
6. Write the group dictionary and provenance notes. If PPR integration is requested,
   run repository `tools/build_model_workbook.py --units <unit>` and
   `tools/verify_model_workbook.py --units <unit>`.

For central **Final mappings**, exact numeric weights, annual NPP, independent
simple PPR, NPP-only/global-denominator views, provenance or discard sensitivity, read
[integration-contract.md](references/integration-contract.md). When workbook
integration is requested, rebuild central and model workbooks and verify their
mapping parity after mapping changes.
Independent catch/TL PPR and satellite NPP do not require a new model mapping.

Preserve every catch taxon and exact group strings. Follow the shared validator's
catch restrictions, including its harvested-algae exception; detritus and diet
import cannot take catch. Target 95% of catch tonnage without inventing
assignments to meet it. Keep models separate and preserve unknown SPPR as missing.
Report tonnage coverage, confidence tiers, composite bases, meaningful unresolved
catch and missing sources. Example workbooks show output shape, not transferable
assignments.
