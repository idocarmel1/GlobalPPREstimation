# Project skill knowledge refresh — 2026-09-11

The three project skills now carry the knowledge needed to move from Ecopath
source evidence to annual PPR/NPP integration without reconstructing the recent
research and integration decisions from task history. The refresh covers six
agent distributions and their six `.skill` archives. It documents existing
scientific and production boundaries; it does not establish new ecological
conclusions or extend model coverage.

The final follow-up refresh began after both 22-year raster extractions and the
implementation agents finished. It adds all-366 independent simple PPR, NPP-only
without catch, fixed-union global ensembles, physical support, exact cache/source
lineage and the root article reference/use log. The sections below retain the
preceding integration review; the follow-up evidence is recorded separately here.

## All-ecosystem follow-up

The pre-refresh review identified missing guidance for NPP without catch, the fixed
global denominator, annual physical support, canonical run/cache selection and
Git byte preservation. The guide also still described only the original 166-region
NPP scope. The shared integration reference now covers those decisions, the
published 366-region history, safe isolated recomputation and independent simple
PPR without article/model gates. Entry points route those tasks directly to it.
The extraction source-bundle guide distinguishes reference-use roles and keeps
new paper extraction separate from simple PPR/NPP availability.

An independent reader inspected all six distributions and answered six realistic
requests using only the skills and linked documentation: model-free simple PPR;
NPP-only/no-catch and earlier-year proxy behavior; selected versus fixed-union
ensemble aggregation; changed code/provenance; fresh-clone reproduction; and
catalog-only/unresolved references with line-ending changes. All six scenarios
were answerable. The review exposed an unconditional mapping-to-workbook step;
it was corrected in the source and copied workflows so mapping-only requests
stop at validated mapping files. Linked reproduction/run-status documentation was
also updated. This tests retrievable decisions, not a new scientific replication.

All six distributions passed structural validation and package/source parity.
The existing installed extraction skill was backed up and refreshed with 29
verified resource files while preserving its interface bytes. Current evidence
is in `data/installed_skill_refresh.json` and `data/skill_forward_validation.json`.

## Scope and deliverables

| Project skill | Claude distribution and archive | Codex distribution and archive | Requested scope |
| --- | --- | --- | --- |
| `ecopath-extraction` | [Skill](../skills/claude/ecopath-extraction/SKILL.md), [archive](../skills/claude/ecopath-extraction.skill) | [Skill](../skills/codex/ecopath-extraction/SKILL.md), [archive](../skills/codex/ecopath-extraction.skill) | Source parameters, EwE imports, database JSON and provenance |
| `ewe-species-to-group-mapper` | [Skill](../skills/claude/ewe-species-to-group-mapper/SKILL.md), [archive](../skills/claude/ewe-species-to-group-mapper.skill) | [Skill](../skills/codex/ewe-species-to-group-mapper/SKILL.md), [archive](../skills/codex/ewe-species-to-group-mapper.skill) | Catch taxa, supported model groups, mapping weights and PPR integration |
| `ecopath-paper-to-ppr` | [Skill](../skills/claude/ecopath-paper-to-ppr/SKILL.md), [archive](../skills/claude/ecopath-paper-to-ppr.skill) | [Skill](../skills/codex/ecopath-paper-to-ppr/SKILL.md), [archive](../skills/codex/ecopath-paper-to-ppr.skill) | Extraction, taxonomy, SPPR and mapping, or the requested subset |

Claude retains its detailed standalone workflows in `SKILL.md`; Codex uses concise
entry points with the complete workflows in `references/` and its interface
metadata in `agents/openai.yaml`. Shared scripts, scientific references, templates
and examples are copied from the common sources. The combined skill bundles its
own resources rather than depending on a sibling installation.

## Baseline gaps and retrieval checks

The baseline gaps were missing integration guidance and places where broad
instructions could be misread. The refresh does not claim that every workflow
below was previously absent: the four-stage chain already existed. A read-only
review used only `skills/codex/` and bundled resources to answer these seven
realistic requests, without consulting current scientific implementation or
running pipelines. All seven decisions were recoverable; numerical results that
require source records or response data remained explicitly unsupported.

| Retrieval scenario | Baseline gap or ambiguity | Supported answer after the refresh |
| --- | --- | --- |
| 1. Does full paper-to-PPR include taxonomy when extraction and taxonomy are separate? | The separate artifacts could be confused with an instruction to omit taxonomy; the chain already contained stage 2. | Full paper-to-PPR includes taxonomy, captured during source reading. Extraction-only stops at stage 1. JSON-only models use the taxonomy CSV/application route. See [workflow](../skills/codex/ecopath-paper-to-ppr/references/workflow.md) and [taxonomy](../skills/codex/ecopath-paper-to-ppr/references/group-taxonomy.md). |
| 2. Is a diet-study appendix exhaustive membership, and do all absent catch taxa need weights? | A generic species-table instruction did not distinguish composition, catch allocation and selected diet examples. | Preserve table purpose and source precedence. Absence alone neither excludes a taxon nor requires weights. Several supported biological groups or spatial pools require a split; an explicitly named member can still have uncertain regional weights. Bay of Bengal A3.1 is distinguished from A1.1/A1.3. See [taxonomy](../skills/codex/ecopath-paper-to-ppr/references/group-taxonomy.md) and [mapping format](../skills/codex/ecopath-paper-to-ppr/references/mapping-output-format.md). |
| 3. How should source natural mortality of 0.17/year be compared with B=0.202, PB=0.249, EE=0.582 and loaded M0 near 0.02102? | The standard Ecopath rate notation did not explain the calculator attribute with the same name; source units were stated too broadly. | Calculator M0 is the flow `B*PB*(1-EE)=0.021024564`; its corresponding other-mortality rate is `0.104082/year`. Source natural mortality may include predation. Reconcile source definitions and model versions before judging a discrepancy; do not overwrite EE to force equality. Verify each source's biomass units. See [mortality and discards](../skills/codex/ecopath-paper-to-ppr/references/mortality-and-discards.md). |
| 4. How does a fresh clone collect archive/catch-year NPP, and handle units and early years? | The skills lacked the annual reproduction route, canonical/legacy scaling distinction and missing-year display policy. | Use the NPP package setup, source plan and annual run documented in the [integration contract](../skills/codex/ecopath-paper-to-ppr/references/integration-contract.md). Canonical annual NPP is regional tonnes carbon; the legacy 2019 reference uses `scaled_*`. Missing values stay blank. Optional `earliest` substitution is only a labeled constant proxy for earlier missing years, with source year retained. |
| 5. Where can a reviewer find complete final mapping weights centrally? | Mapping output documentation did not expose the central full-precision review route. | Both central and model workbooks contain **Final mappings** with the numeric weights and provenance. The resolved CSV displays six decimals. Rebuild both workbook types and verify parity after an authorized mapping change. See [mapping format](../skills/codex/ecopath-paper-to-ppr/references/mapping-output-format.md). |
| 6. How do three catch bases and optional uncertainty preserve taxon composition? | The skills lacked the integrated catch-component and sensitivity contract. | Calculate landings, all catch and discards separately from their own taxon/year vectors, checking `C=L+D` where known. Apply the existing PPR `/9` conversion once; use the same selected component for coverage and unidentified treatments. Routing sensitivity uses landings and fixed mappings; NPP algorithm spread stays separate. Neither is a confidence interval. See [integration contract](../skills/codex/ecopath-paper-to-ppr/references/integration-contract.md). |
| 7. What happens with invalid fractions, unknown discards, an unassessed region, a failed method or zero source harvest? | Transfer eligibility, interpolation, complete-cohort support and source/production failure boundaries were not available in the skill. | Never cross an invalid/missing fraction, extrapolate or bridge the zero-catch transition. Known landings remain usable when discards are unknown, but exposure/sensitivity do not. A regional band requires compatible responses for the complete fixed cohort and at least two common routes. Keep production failure gates; zero source living harvest cannot supply a response. See [integration contract](../skills/codex/ecopath-paper-to-ppr/references/integration-contract.md). |

The NPP and response references point to repository tools and current provenance
reports for execution. The retrieval check established that an agent can find the
decision rules; it did not independently reproduce NPP downloads, model results
or a numerical discard envelope. Historical output counts in the skill are
labeled as release/audit evidence, not targets for future runs.

## Mapping validator limitation

The review found one remaining mechanical limitation: `members.csv` has no
evidence-scope or precedence field. Its validator treats each nonblank supplied
group placement as a membership constraint, and its composite check can accept a
mapping when only one candidate overlaps the documented set. Passing that check
does not validate every candidate or its spatial weights.

This is now explicit in the authoritative [mapping output format](../skills/claude/ewe-species-to-group-mapper/references/output-format.md),
[integration contract](../skills/claude/ewe-species-to-group-mapper/references/integration-contract.md)
and [combined taxonomy reference](../skills/combined-src/references/group-taxonomy.md),
and their generated copies. Keep unreconciled diet-study transcriptions in a
separate source-audit table. Populate `members.csv` only after reconciling placement
for the exact model; a broad diet-study label must not override a supported
dedicated group. Review every candidate and the full weighted coefficient
independently. This refresh documents the limitation; it does not add a new schema
or strengthen the validator's algorithm.

## Source editing and rebuilding

| Knowledge or interface change | Authoritative editing location |
| --- | --- |
| Extraction workflow, source accounting, mortality/discards, scripts and templates | `skills/claude/ecopath-extraction/` |
| Mapping, membership format, annual PPR/NPP integration, scripts and examples | `skills/claude/ewe-species-to-group-mapper/` |
| Combined router and taxonomy stage | `skills/combined-src/` |
| Codex entry points and interface metadata | `skills/codex-src/<skill>/` |

`skills/claude/ecopath-paper-to-ppr/` and all of `skills/codex/` are generated.
Correct the authoritative source once, then rebuild from the repository root:

```text
python skills/build_combined_skill.py
python skills/build_combined_skill.py --check
```

The builder assembles both agent distributions and all six archives with stable
archive metadata. The read-only `--check` detects missing/stale resources,
unexpected skills and stale archives. `skills/build_skill.py` is the compatibility
entry point. Bundled paths resolve from the skill directory; repository tools and
data resolve from the checkout. `GLOBALPPR_ROOT` locates mapping data and does not
change the shell working directory.

Historical validation for the preceding refresh: the distribution/archive parity check
passed after the validator-limit clarification was propagated, and 49 JavaScript
tests passed after the final download regression fix. The seven-scenario retrieval review above supplied the behavioral
check. These are distinct checks; they are not a claim that the scientific
pipeline was rerun during this documentation phase.

## Existing installed skill

The [installation record](../data/installed_skill_refresh.json) reports `status:
ok` for the deliberately refreshed existing `ecopath-extraction` installation:

| Record field | Value |
| --- | --- |
| Installed path | `C:\Users\idoca\.agents\skills\ecopath-extraction` |
| Backup path | `C:\Users\idoca\.codex\skill-backups\globalppr-20260911-030525\ecopath-extraction` |
| Existing interface metadata preserved | `true` |

The record includes per-file SHA-256 values for the verified installed resources.
No new global skills were installed. Repository rebuilds do not automatically
refresh other installed copies; the six project distributions remain available
for deliberate future installation.

## Deferred work

The final review added one source-validation scenario after finding that preserved
size/timestamps can bypass the frozen regional helper's checksum cache. The shared
integration contract and linked reproduction guides now distinguish the completed
run from a future hardened version and fresh plan. An independent uncached audit
passed1,104 files/32,049,287,447 bytes; the seventh forward scenario passed without
contradictions. All six distributions were regenerated and checked again. The
installed extraction package was unaffected by this mapper/shared-chain addition.

The expanded carbon-conversion literature review by organism group/trophic level
and new Ecopath model extraction remain deferred. Independent simple PPR and
regional NPP coverage now span all 366 identities. The retained wet-weight to
carbon factor is the existing `/9` convention, not a new group-specific empirical
finding. The refresh does not authorize source-parameter changes, new ecological
claims, a global discard proxy band or extension of model-specific response
results to untested models.
