# EwE species-to-group mapping procedure

This is a domain resource of the active [paper-to-PPR skill](../../SKILL.md), not a third skill. The [regional calculation contract](../../references/regional-calculation.md) and [validation guide](../../../../templates/instructions.md) govern current confidence, assumptions and adoption. Scripts and references resolve from this resource directory. The former stand-alone mapper's data/model_selection.xlsx, top10, work-order and builder paths are obsolete; they must not be recreated.

Ecopath groups and Sea Around Us taxa require an evidenced join. Measure both taxon coverage and the share of catch tonnage assigned to supported groups: a few coarse labels can carry most catch. Prefer near-complete coverage with transparent meaningful M10/M11 approximations; the former 95% target is not a pass criterion. Mapping coverage, coefficient availability, diagnostic health and researcher approval remain separate.

## Establish the exact inputs

Read the regional workbook through tools.project_core.workbooks.workbooks: Overview identifies the selected model; Catch contains taxa and annual bases; Selected model groups contains accepted group IDs/names. Resolve canonical JSON through tools.project_core.registry.discovery.resolve_model. Paper sources live in their paper's sources/, original catch under regional raw/catch/, and retained SPPR source/diagnostics under the model. A second selection workbook or work order is not authoritative.

Read exact group identifiers and accepted definitions before taxa. Names are joined literally, including punctuation and spatial prefixes. Verify taxon_descr in the actual model; an empty field differs from a completed search recorded as not documented. Source-faithful taxonomy is not overwritten with assumed analogue membership.

An evidenced group inventory can support mapping when the model is NOT_RUN or coefficients unavailable. Preserve that restriction and do not describe mapping controls as numerical eligibility. If group identity cannot be established, leave the affected mapping pending.

## Read membership evidence

Identify grouping axes: taxonomy, guild, habitat, spatial strata, life stage and size. Use [model structures](references/model-structures.md). Read paper/supplements for species-to-group tables, group definitions, size/depth boundaries, synonyms and explicitly adopted predecessors. Diet constrains a guild but does not establish exhaustive membership.

Transcribe source membership tables before decisions, retaining printed and verified accepted names, exact groups, source locators and table purpose. A diet-study list may be illustrative; reconcile dedicated groups and allocation tables before treating it as a constraint. Inspect every necessary candidate in a composite, not merely one overlapping member. Keep conflicts explicit.

Make real recovery attempts for identifiable missing supplements and record filename, URL, date and outcome. Distinguish direct adopted source, supporting regional evidence and analyst inference. Citation discovery alone does not establish that a source was read.

## Review taxa and weights

Work in catch-tonnage order while retaining all requested taxa, including zero-catch and unresolved rows. Evaluate explicit membership, verified synonyms, containment, habitat/size/guild, explicitly inherited classification and meaningful ecological analogues. TL corroborates but cannot select a feeding guild by itself. Use [coarse-taxa guidance](references/coarse-taxa-playbook.md) with current M10/M11 rules; offshore absence alone does not require Unresolved if a meaningful analogue is justified.

Establish eligible groups independently of coefficient availability. Prefer applicable direct caught-mass composition, then reviewed model-catch and model-biomass proxies. Both proxies retain Medium allocation confidence and transfer assumptions. Missing/default values do not become measured zeros. A justified W11 last resort is explicitly Very low. No automatic equal-share fallback, correction of erroneous totals by normalization, or silent candidate removal is allowed. Preserve genuine zero candidates in evidence.

Assess membership and allocation separately; the weaker necessary confidence governs High, Medium, Low, Very low or Unresolved. Weight one cannot strengthen unsupported membership. Nearby-model crosswalks require compatible definitions and actual donor evidence; donor weights and SPPR do not transfer automatically.

## Record, verify and integrate

Use [the current output contract](references/output-format.md). Adopted regional PPR / Matching has one exact taxon/group row per decision, numeric weights and evidence; unresolved group/weight stay blank. Preserve full precision, confidence, independent assumed flags and allocation evidence. Validate complete taxon coverage, duplicates, every composite member, nonnegative weights summing to one, basal-group errors, source contradictions and tonnage support for actual year/basis/method/scope. Structural success is not a source review or model approval.

For mapping-only work, finish requested evidence/decisions and state downstream work still required. For authorized adoption/arithmetic use the maintained regional API and python tools/cli/region.py --region regions/<type>/<unit>/<unit>.xlsx --stage calculate, then requested central/map integration. Preserve valid group coefficients, accepted model bytes, failures and independent Catch/Classic PPR/NPP. Selection changes use the single refresh command with complete snapshots and precise pending semantics.

Examples remain reference explanations, not cross-region assignment tables. Historical weak coverage or undisclosed stratum choices require assessment, never copying. Report taxon/tonnage coverage, confidence and assumption-dependent shares, composite weight bases, unresolved reasons, missing supplements and applicability. Keep extended source/numerical checks outside concise scientific report prose.
