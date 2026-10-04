# Mapping records and supporting evidence

Regional PPR / Matching is the adopted mapping authority. Use the [regional contract](../../../references/regional-calculation.md) and [agent project contract](../../../../../../explainers/agents/project_contract.md). CSV transcriptions/proposals are evidence until authorized adoption, not a second mapping registry. Former data/<unit>/mapping, top10, builder and selection-workbook paths are obsolete.

## Adopted rows

One exact taxon/group row contains model_id,taxon,group,weight,confidence,evidence,explanation. Preserve full persisted precision, source/catch spelling and model identity. Resolved nonnegative weights sum to one within established tolerance; unresolved group/weight stay blank. Do not normalize erroneous totals or infer fallback from a blank weight. There is no automatic catch-to-biomass-to-equal cascade.

Keep one mapping per distinct model-region pair, including models sharing group lists. Period, area, scenario, season, strata and structure identities remain separate. Fixed weights across years/bases are an extrapolation, not evidence of invariant composition.

Membership/weight confidence and independent assumption flags belong in PPR / Mapping review and PPR / Allocation assumptions as applicable. Overall confidence is the weaker necessary component under High > Medium > Low > Very low > Unresolved. Direct applicable composition supports High allocation; reviewed model-catch/biomass proxies remain Medium assumptions. M10/M11 placement and W11 allocation retain Very low. Preserve zero candidates and rejected attempts. Numerical availability cannot establish membership.

## Source transcriptions and group dictionaries

Extraction membership evidence belongs in model-local extracted_tables/evidence/; validation assessment in model_validation/evidence/mapping/. Temporary proposal/import CSVs use work/<run_id>/inputs or outputs and are promoted or removed after checks. Use purpose-specific filenames, not a parallel permanent model-notes registry.

A membership transcription includes printed_name,accepted_name,group_name,source_page,table_purpose,evidence_scope. Preserve printed names separately from independently verified accepted names. State whether a list is exhaustive, illustrative, catch-allocation or diet evidence. Absence from an illustrative list does not prove exclusion. Reconcile broad diet-study placement with dedicated compartments and inspect every composite member. Bay of Bengal A3.1 diet-study versus A1.1/A1.3 allocation/composition is a source-specific example requiring version checks.

A dictionary retains every accepted group, including unfished groups: group_id,group_name,model_tl,grouping_basis,explicit_members,supporting_taxa,membership_source,source_relationship,source_location,source_url,notes. Grouping basis includes taxonomy, guild, habitat, size/life stage, stock, residual/nonliving pool and spatial stratum. Relationship distinguishes direct adopted source, supporting regional source and analyst inference. not documented means a completed search; blank means missing evidence. Preserve table purpose and source precision.

## Explanation and verification

State a decisive checkable fact with exact source locator: explicit membership, verified synonym, or described habitat/size/guild match. A coarse mixture requires eligible candidates, weight basis and applicability assumptions. Avoid unsupported best-match or similar-species claims. Never present inference as publication prose.

Link decisions from adjacent model_notes.md or the applicable evidence index. Record citation/DOI, period/area, grouping axes, available/missing supplements, judgments and limitations. Model area differs from target region; filename alone cannot establish coverage. Okhotsk NE is an identity label, not proof of northeastern-only scope.

Verify exact keys, all requested taxa, duplicates, sums, rejected/zero candidates, confidence/assumptions, missingness and numerical support. The old standalone mapper validator assumes an obsolete repository schema and is not a current workbook validator. Use maintained workbook/regional checks and independent source review.
