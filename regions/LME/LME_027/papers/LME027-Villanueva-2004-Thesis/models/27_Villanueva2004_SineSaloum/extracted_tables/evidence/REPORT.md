# Sine-Saloum (1991-1992): partial evidence imports

This package preserves Table 6.5 and Annex II.A of Villanueva's downloaded 2004 thesis. It is a blocked reconstruction, not an admitted full model. Original source values are retained in `../literal_source_extraction.json`, the numbered diet CSV and companions.

## Source tables

Table 6.5: PDF page 138, printed page 114, 37 numbered rows. Printed columns map NT to TL, B to wet-weight biomass, P/B and Q/B to annual rates, EE to ecotrophic efficiency, P/Q to production/consumption and Y to annual wet-weight catch density. Parentheses denote model-estimated outputs; source letter markers identify methods/citations. Comma decimals become dot decimals without changing precision. Source footnotes, parentheses and asterisks remain in companions. The published detritus P/B of 1.700 is retained as evidence; it does not establish supported biological detritus production in the project calculator.

Annex II.A: PDF pages 235-236, printed pages 211-212. Header Proie / Prédateur establishes prey rows and consumer columns. Both blocks contain all 37 prey; predator columns run 1-17 then 18-34. Exact source column sums are 0.999 for consumers 2, 5 and 10 and 1.000 for the other 31 consumers. Source value 0,0010 (prey 16, consumer 6) retains four decimal places. The percent caption is inconsistent with the fraction-like numeric cells and sums. No numerical correction, normalization or percent conversion was introduced.

## Biomass accumulation

Methods, parameter footnotes, chapter 6, source figures and the thesis full text were searched for numeric BA and assimilation/egestion. No numerical BA or GS was established for this model. BA stays unknown, even though the general Ecopath method describes a balanced state. Qualitative ecological stability does not provide a group-specific numerical BA input.

## Values from prose

Group definitions are retained in `MODEL_PROFILE.md` and the method/membership evidence excerpt. No numerical GS, routing, migration, discard or habitat-fraction input was supplied from prose. Table 3.3 supports reconciling group 27 as a pooled Mugilidés compartment, but does not reconcile the group 20 identity conflict.

## Conventions applied

Published Y is carried as a single `Reported total catch` column in Landings.csv. This label is a format convention, not evidence that separate discards are zero or total removals complete. Source diet blanks are retained as blanks, with their structural absence distinguished in the full source cell ledger. The writer's `(1 - Sum)` row uses its fixed schema placeholders and is not an ecological source observation. Unknown diet imports are explicit nulls, so the writer does not invent zero imports.

## Deliberate blanks

Habitat fractions, Z, GS, detritus import, BA, migration, separate discards and detritus routing are not established source values. All remain blank/unknown. Y is unknown for group 12 and groups 31-37; group 22 Y = 0.000 is known. GS blanks may become 0.2 in EwE, BA blanks may become zero and habitat fractions may become one; those software defaults are not accepted source inputs here.

## Unresolved and flagged

Table 6.5 group 20 is Epinephelus aeneus*, while Annex II.A group 20 is Hemichromis fasciatus. Table 3.3 treats them separately. The canonical matrix therefore withholds both prey row 20 and consumer column 20, 70 cells in total, while the full original 1,258-cell annex is retained. The source-numbered matrix must not be joined to the basic table by position alone. Group 27 is the same documented Mugilidés pool despite the differing representative names; spelling conflicts remain visible in the crosswalk. Other Table 3.3/Table 6.5 grouping conflicts are not silently resolved.

## Validation

The structural validator reports four errors and 40 warnings. The four known-subtotal deficits (columns 3, 5, 8 and 10) arise from withheld canonical prey-20 values, not from a published diet matrix that sums to those deficits. Warnings identify missing GS, missing BA, empty consumer-20 diet and absent routing. Exact source sums are independently retained in the source audit.

The standard-table/JSON/reconstructed-workbook fidelity check passes: eight standard tables plus four source companions, 23,172 checked cells, exact and numeric values and missing masks match, maximum numerical difference zero. Fidelity verifies preservation of the partial evidence; it does not establish scientific readiness.

## Mass balance

Scientific model health and direct GE/TE/With Egestion diagnostics are NOT_RUN: no admissible full source model or loaded computational state exists. The database converter automatically produced an indicative partial-input check (one error for consumer 20, 109 indeterminate entries, no warnings and two notes). Those results are preserved as converter evidence and do not judge the author's native model. The final generated database JSON preserves unknown habitat area as -9999 for all groups after source-fidelity restoration, but labels preserved structural diet blanks as unknown. See `../converter_transformation_ledger.json`. No such state was loaded for regional calculations.
