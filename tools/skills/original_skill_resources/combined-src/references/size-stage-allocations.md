# Size, stage and cohort allocations

Apply the [evidence, execution and adoption contract](evidence-handoff.md) to this stage: explain fresh runs and honor existing scoped authorization, retain the applicable portable evidence, and verify completeness before handoff.

Use with regional-calculation.md when caught taxa occur in multiple source groups. Repository paths below start at `<repo-root>`. This procedure implements the user-authorized assumption workflow; do not infer permission to select another model or repair its biology. Existing session authorization remains sufficient.

## Scope and evidence

1. Inventory selected model-region pairs from Project.xlsx, then verify selection in each regional Overview. Review every selected pair requested, including cases with no applicable split. Keep one mapping per pair; alternative models do not receive mappings. Save baseline workbooks and source hashes before adoption.
2. Read the source definitions and exact group IDs, not just names. Record size/age boundaries, units (fork/total/mantle length), cohort definitions, membership, source period, and conflicting definitions. Juvenile/adult groups must describe the same supported taxon or pool. Geographic strata and distinct species named “large/small” are not stage splits. Representative species lists do not establish exhaustive containment. Resolve historical aliases with evidence. If the exact alias remains ambiguous, preserve that uncertainty and assess a meaningful M10/M11 analogue before leaving the mapping unresolved.
3. **Search online before using model catch as a proxy.** Target the species, exact cutoff, region, fishery/gear and source period; check primary assessment reports, observer data, regional fisheries organizations, catch-at-length/age datasets and source supplements. Record query, search date, URL, what was actually read, geographic/fleet/year/catch-basis coverage and adoption/rejection reason. Log inaccessible, registration-gated or failed retrievals honestly. A search snippet or gear description is not an observed catch-size mass fraction. A failed bounded search does not show that raw sampling data do not exist.

## Coverage preference

Apply the validation guide’s five confidence levels and explicit preference for near-complete catch coverage. Broad labels may use a recorded set of named and residual groups (M10 Very low); taxa missing an exact compartment may use a meaningful closest ecological/taxonomic analogue (M11 Very low). Unknown composition or a geographic mismatch alone is not a reason to stop. Unresolved remains appropriate when no meaningful placement or usable numerical assumption can be justified. Preserve separate assumption flags and do not promote scientific validity.

## Allocation hierarchy

- Prefer applicable geographic source data that quantify taxon catches across areas corresponding to the model groups (W10 High allocation confidence). Record boundaries, quantities, source/group correspondence, period and catch basis. Mere geographic overlap or transferred spatial proxies do not qualify automatically as High.
- Prefer observed **caught mass** matching the groups and regional fishery. Length/age frequencies in numbers require appropriate weight-at-length/age conversion and sampling/fleet weighting before summing mass either side of a cutoff. Do not use population biomass proportions, species maximum size, a legal minimum, mesh opening or an L50 value directly as caught-mass shares. Selectivity curves describe capture probabilities; the encountered population composition also matters. Retention and discards differ.
- If compatible observed mass shares cannot be recovered, use source-model catches as an explicitly assumed historical proxy: `weight_g = catch_g / sum(catch_candidates)`. Identify whether these are landings, discards or total removals and the fleets included. Compare source/native values, canonical JSON and loaded groups. For a species inside a pooled group, record the extra assumption that the pooled stage ratio transfers to that species. Preserve already documented cohort-landings ratios rather than silently switching their basis.
- Normalize only when all effective catches are finite and nonnegative and their sum is strictly positive; individual zeros are valid (for example, `[0, 3]` gives `[0, 1]`). Reject negative catches. With a zero sum or unresolved missing values, normalization is undefined. An adult-only assumption may be used only for an unambiguous same-taxon split under the user's authorization, with its evidentiary weakness explicit. An unknown numerical cutoff remains unknown. If complete model catches are unusable, use complete model biomass proportions under the approved Medium allocation assumption, retaining the rejected catch attempt. If both fail, assess an explicit W11 Very low numerical assumption; otherwise leave unresolved.
- Missing sentinels/defaults are not observed zeros. If an infant stage has missing raw catch but is explicitly assumed uncaught, retain raw `source_catch=null`, the sentinel and loaded value; record `effective_source_catch=0` and a separate `catch_assumption`. Keep that zero-weight candidate in the ledger.
- When documenting an existing stage assumption layered over a taxonomic composite, preserve its exact positive mapping weights and existing taxonomic basis. Do not replace taxonomic composition with stage-model catch ratios. Use `preserved_stage_assumption`, which rejects numerical changes. Broader unresolved taxonomic weights require a separate review.

All fixed proxies are assumptions across the retained years and landings/catch/discards bases. Even an observed source-period size composition becomes a temporal/geographic/basis assumption when reused as a fixed mapping; distinguish `weight_evidence` from overall `confidence=assumed`. “Large” need not mean sexually mature. Adult-only does not assert that every actual landed or discarded individual was adult.

During confidence reassessment, reproduce every stored weight from the exact candidate IDs and source fields, including zeros. Arithmetic agreement establishes reproducibility, not stronger empirical confidence. Distinguish an author's assumed percentage (for example an assumed juvenile share used to construct the model) from an observed caught-mass split; the former remains a model proxy. Reuse a relevant retained search record explicitly rather than implying it is a new or exhaustive search. Raise allocation confidence only when newly verified evidence actually meets the observed/geographic allocation criteria.

Assess membership of a combined juvenile/adult pair separately from uncertainty about its internal cutoff or split. Conflicting 18-month and two-year definitions may weaken the split without weakening eligibility in the pair. A maximum-size boundary selecting different species pools is a membership issue instead; verify the source's length convention before changing that classification.

## Record and apply

Use `tools/size_allocations.py` after scientific review for its supported size/stage rules; it does not research or infer membership. W9 biomass, W10 geographic, W11 last-resort weights and broad M10/M11 mapping revisions are outside that CLI's current rule enum. Do not relabel them as `model_catch_proxy` to bypass validation. For those authorized cases, retain the same evidence fields and exact W/M rules in `PPR / Mapping review` and the allocation ledger, apply the reviewed weights through the regional workbook contract, and use the existing regional recalculation and project-update functions. The unified allocation helper calculates applicable geographic/catch/biomass proportions; W11 remains an explicit reviewed numerical rule. Prepare one plan per selected pair with `unit_id`, `model_id`, reviewed `workbook_sha256`, portable `evidence_path`, and `proposals`. Each supported size/stage proposal requires:

- `taxon`, `rule` (`observed_catch_size`, `model_catch_proxy`, `adult_only_assumption`, or `preserved_stage_assumption`), definition, evidence, limitations and source period/basis;
- exact candidate `group` and `seq`, nonnegative `weight`, source catch/raw/loaded values and any explicit effective-catch assumption; include zero weights;
- online-search records with query, date, primary URL and result/applicability. Source hashes and table/page locators belong in evidence.

For observed number-to-mass conversions, retain the count bins, length/age-to-weight equation and parameters, fleet/sample raising factors, units, cutoff-boundary treatment, and resulting mass numerator/denominator so another reviewer can reproduce the weights.

For a single reviewed pair:

```text
python tools/size_allocations.py --region regions/UNIT/UNIT.xlsx --plan reviewed-plan.json --backup retained-study/baseline/UNIT.xlsx
```

The CLI requires matching reviewed bytes and a fresh backup path. For batches, validate and prepare all pairs first, serialize live writes, and retain a versioned run manifest. Research plans are evidence, not replacement configuration/status sidecars.

The regional workbook is the active record:

- `PPR / Matching`: positive weights only, one taxon/group row, `confidence=assumed`, evidence and explanation; each resolved taxon's weights sum to one.
- `PPR / Allocation assumptions`: all candidates, including zero weights, source values, rule, definition, source/search evidence, prior mapping, limitations, and years/bases applied. Zero-weight groups do not need a coefficient to compute a positive-weight assignment.
- `Diagnostics / Size allocation impact`: per scope, method, basis and year, baseline and new PPR/covered catch, total catch and assumed covered catch. `Diagnostics / Size allocation review` records authorization and evidence path.
- Batch reviews also record `Size allocation scope review`, `Size allocation unresolved`, and, where necessary, `Blocked size allocation proposals`. When groups or numeric SPPR are absent, preserve proposed evidence as blocked; do not create a fake active mapping/result.

When calculation is within the authorized scope, recalculate with the helper, which retains diagnoses, makes affected numeric results explicitly provisional and preserves independent catch/classic/NPP data. For matching-only work, retain the reviewed proposals/mapping evidence and report the downstream refresh still required; do not invoke this calculating helper without calculation authorization. A pre-existing FAIL stays FAIL in diagnostic tables. Authorized provisional numeric display does not imply model validation; missing coefficients remain missing. Do not run a solver or silently repair model parameters for a mapping task.

## Verify and report

Independently check exact group membership, catch provenance, weights, coefficients, catch mass balance and annual PPR. Preserve selected IDs/rationales, source-model bytes, all existing diagnostic tables, Catch, Classic PPR and NPP. Check saved-byte input/result hashes and ensure previously numeric source scopes remain numeric: an unavailable `simple` unidentified treatment for PP/inner must not overwrite the base method status. Keep negative coefficients/diagnosis flags visible where provisional display was authorized.

Catch coverage for a given scope/method/year/basis is `sum(catch with finite taxon SPPR) / sum(total catch)`; numerator and denominator use that same basis. PPR is `sum(catch_t * sum(weight_tg * SPPR_g))`. Existing taxon coefficients are rounded by the regional calculator. Annual PPR is wet-weight equivalent; divide by nine exactly once for displayed tonnes C.

Report baseline versus final coverage and PPR, coverage-point improvement, and the fraction of total catch dependent on recorded stage assumptions. Assumption-dependent coverage is not the same as newly gained coverage: documenting an existing assumption may change no number. Coverage excluding these assumptions is not a claim that all remaining mappings are validated. Do not sum overlapping region catches into a global improvement.

After authorized project integration, update Project.xlsx using the standard updater, rebuild the map/trends, and verify their embedded values and visible provisional/diagnostic flags. The 2026-09-29 review is retained at `original_research_archive/research/size_allocation_20260929/`; treat its allocations as pair-specific evidence, never a universal species lookup.

The unified skill’s `scripts/assumed_allocation.py` helper accepts optional applicable geographic caught-mass data with source, area boundaries, group correspondence, period, basis, units and applicability. It returns High allocation confidence for documented direct quantities, then falls back to model catch/biomass at Medium. It does not choose groups or infer scientific applicability.
