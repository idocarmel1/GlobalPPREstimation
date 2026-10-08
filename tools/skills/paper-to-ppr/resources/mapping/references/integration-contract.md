# Annual PPR, NPP and discard sensitivity in GlobalPPREstimation

Read for integration or publication after mapping. Paths below are relative to
the checkout, not the installed skill. Scientific rules below retain the original integration semantics. Current execution follows [project integration](../../../references/project-integration.md) and [regional calculation](../../../references/regional-calculation.md); obsolete historical API paths are not commands to recreate. Historical release counts and study availability below describe their cited snapshot; source availability and output counts must be checked from current
reports instead of inferred from an old example.

## Final mapping weights

Regional PPR / Matching contains the exact adopted model/taxon/group weights, confidence, evidence and explanation. Allocation assumptions retain all candidates, zero/rejected attempts and basis. Use full numeric precision, not a rounded CSV or preview. An authorized mapping change uses the maintained workbook/regional checks and dependent arithmetic; source-specific CSVs are evidence, not a second mapping authority.

Keep weights fixed across years and discard scenarios. Resolve biological and
spatial candidate sets before calculating weights. Source membership can establish
the biological group while leaving its regional split uncertain. Validate the
full weighted coefficient, not merely one overlapping member or rounded weights.

## Units and three catch bases

NPP is annual **tonnes carbon**, not wet or dry biomass. Existing PPR source
workbooks and ordinary annual PPR arrays use wet-weight-equivalent production.
The site converts PPR to carbon once using the retained project convention `/9`.
It then computes `100 * PPR_carbon / NPP_carbon`; do not divide by 9 again or add
an extra wet-to-dry conversion. This is an assumed wet:carbon factor, not a newly
measured conversion for every group. The owner's expanded Perplexity literature
review by organism group/TL remains deferred, as does new model coverage.

For each taxon/year, preserve full-precision total catch C, landings L and discards
D; check `C=L+D` where all are known. Landings include reported and unreported
retained catch. Evaluate `sum(selected_component * mapped_SPPR)/9` separately for
**landings** (map/graph default), **all catch**, and **discards only**. A regional
discard fraction cannot rescale an old taxon-composition-weighted PPR correctly.

Coverage and unidentified/NEI treatment use that same selected component. The
three unidentified treatments are the selected method, explicit zero PPR while
retaining its tonnage, and reference catch-taxon TL at TE=0.1 under All only.
`simple trophic chain` uses catch-taxon TL; `SPPR_1995_TE0.1` uses model-group TL.
An identical formula does not make those estimates interchangeable.

A known zero remains zero for a valid supported calculation. Missing selected
components remain unavailable; known landings can still be evaluated when D is
unknown, but the discard fraction and sensitivity cannot be inferred. Context
totals also retain nulls. A positive catch vector with no supported coefficients
is unavailable. These options cannot revive failed scientific methods.

Source workbook downloads retain total-catch calculations. The map's current
estimate CSV and graph's plotted-data CSV carry the selected basis, source scope,
model, NPP policy, coverage and sensitivity settings. Verify their agreement.

## Reproduce annual NPP from a fresh clone

Read [NPPExtraction/ANNUAL.md](../../../../../scientific_code/NPPExtraction/ANNUAL.md) for current engine setup. Current shared originals are common_reference_data/npp/raw/<product>/<year>/ with source_manifest.json; use python tools/workflow_checks/structure/verify_npp_sources.py for actual source bytes and python tools/cli/npp.py plan before an authorized run. Extraction does not adopt values into workbooks. New derived output/cache stays local until its necessary provenance is promoted to versioned evidence.

The retained September 2026 expansion described 366 identities, preserved 11,310 original rows, added 4,398 supported records, reused 14 cells and produced 25,211 rows with 8,050 supported rows plus two historical 2019 cells. These are frozen release facts, not current reorganization verification targets. Its expansion writer and execution snapshots are historical study evidence under research/agents/npp_extraction_2026_09/. Do not execute historical paths against live regional workbooks or recreate old output/data containers.

Preserve source-specific distinctions in any future reproduction: canonical npp_*_tC_yr fields were regional totals; the historical 2019 reference used scaled_* rather than unscaled npp_* totals. Never scale twice. Validate exact source/configuration/geometry/code provenance for the requested run; use isolated work and current engine instructions, not the obsolete tools/npp_data.py or expansion publication commands.

Unsupported, partial, pending, failed, missing and source-error statuses remain
distinct. Numeric missingness is blank, never zero. Ensemble median/min/max use
available algorithms; retain `n_models`, model identities and source year. A
one-model median/range is not a five-model uncertainty estimate. NPP algorithm
spread is not a confidence interval and remains separate from discard sensitivity.

By default, map and graph use the matching year's NPP. The optional **earliest**
display policy substitutes the earliest available ecosystem/method value only
for earlier missing years, labels it a constant proxy and preserves its source
year. Never overwrite canonical inputs, fill internal/later gaps, replace a true
zero, or describe the proxy as a historical satellite observation.

## Independent simple PPR and NPP-only views

Keep ecosystem identities, curated article membership and model selection as
separate sets. The historical source atlas described 366 identities, 167 curated members and ten selected models; current membership and selections must be read from saved Project/regional metadata. `network.simple_units` supplies
independent catch-taxon TL estimates for All-scope simple PPR and regional PPR/NPP.
Use the current regional/atlas implementation for shared catch components and independent simple PPR;
an absent article or failed Ecopath model does not gate those results. Model-group
methods, model-specific scopes and method comparisons retain their existing gates.

The two no-catch identities, HS_018 and LME_064, have NPP but unavailable PPR and
PPR/NPP. In graph NPP-only mode render one carbon-mass curve independently of
catch, models, PPR method or normalization baseline. Disable irrelevant controls
while retaining their preferences for the return to PPR. Preserve genuine zero,
unsupported years and source-year proxy labels in both views and exports.
Display polygons may be simplified; scientific integrations use the hashed full
source geometry. All-identity display membership does not establish article coverage.

## Fixed global atlas denominator

The graph's `atlas_lme_high_seas_union_v1` reference is one dissolved union of
66 LMEs and 18 high-seas identities, including the no-catch regions. EEZs are
not added. It is a fixed atlas geography, not the entire world ocean, and does
not change with selected ecosystems or available PPR. Use the retained atlas-reference provenance and current Project Definitions & build metadata for its calculation identity and annual support.

Integrate each scheduled model over that union, then take the median of the
union-wide model totals. This differs from summing selected regional medians;
for two regions with model vectors [100,400,900] and [900,400,100], the latter
is 800 while the median of model totals is 1000. Actual overlapping geometries
require union integration, not summing regional totals. Union-specific anomaly
factors and model ratios also prevent recovering regional NPP from union totals.
Require all models scheduled for each global reference year; keep regional
available-model ensembles and their partial support distinct.

Completed computation is not full satellite-water coverage. Preserve annual
water area, source-window support, observed/polar-night/fill contributions,
excluded far fills and model support. The source window can change while the
polygon remains fixed. Never convert an unobserved area to an observed zero or
describe algorithm spread as a confidence interval.

## Provenance, resumption and source-use records

Resolve canonical expansion provenance through its explicit `source_configuration`
parent path and SHA-256. The original same-year source run must be unique; reject
changed hashes, foreign-year parents and conflicting runs. A directory's presence
or a readable NPZ is insufficient to resume: validate the full expected input
identity, consumed arrays/dimensions, output hashes and execution snapshots.
Changed code, source configuration or geometry requires a new cache identity.
Keep one raster worker at a time unless memory has been reassessed; never alter
its frozen helper, numerical code, original provenance or canonical input mid-run.
Numerical completion and canonical publication are separate checked stages.

Hash actual raw bytes at validation boundaries: path, size and modification time can survive byte replacement. The frozen expansion helper used a metadata checksum cache; its separate September 11 audit reported 1,104 files/32,049,287,447 bytes. That historical audit does not prove present freshness or uncached checking at every past boundary. Current original-byte verification uses the canonical source manifest/verifier; a fresh scientific helper/run requires its own reviewed input/code identity. Never modify completed study code or provenance to match a new run.

When exact bytes are hashed, preserve them through Git using the repository's
scoped attributes and compare staged blob bytes with the audited working files.
Line-ending normalization can invalidate a scientifically unchanged source hash.
Retain original evidence and code snapshots; do not rewrite them to match a new run.

Maintain current paper source manifests, native input provenance and source roles rather than the removed root external/ log/builder. Distinguish candidate/contextual presence, selected sources, actual numerical use, isolated validation and rejected attribution. Catalog membership is not numerical use or fresh bibliography. Separately owned unfinished research needs explicit inclusion authorization.

## Transfer discard-routing responses

The original study integration used a separate discard reader. Its retained versioned response input is
`research/human/discard_sensitivity_2026_09_10/results/discard_responses.v1.json`.
Match model, method, scope, source JSON and upstream SPPR-workbook SHA-256, group
identity and weighted baseline coefficients. Preserve the existing production
failure and plausibility gates even if a private scenario has finite numbers.
On Windows use UTF-8 mode; resolve corrupted labels only through verified immutable
group identifiers, retaining original labels in provenance.

Exposure is regional annual `f=D/(L+D)`. Applying it uniformly within the source
model is an assumption, not measured group-specific discard allocation. Responses
reclassify a fraction of existing source-model catch; they do not add harvest or
rebuild a source model for each catch year. Native model-area PPR and regional
satellite-NPP ratios have different denominators and must stay labeled separately.

Evaluate every valid named route on the same actual landed taxon vector with the
same fixed full mapping weights and unidentified treatment. If any positive
central-supported taxon lacks its scenario coefficient, exclude that route with
a reason; never shrink its support or renormalize weights. Interpolate coefficients
only between explicitly allowed adjacent computed fractions. Do not cross an
invalid/missing point, extrapolate, or bridge the zero-catch weighting transition.

At least two compatible routes are needed for an assessed minimum–maximum
**discard-routing sensitivity** range. All-catch and discards-only views have no
range; landings allows show/hide. It is a hypothetical scenario envelope, not a
confidence interval or all ecological uncertainty. Retain excluded routes and
source evidence. Fixed-TL invariance means uncertainty was not assessed. A source
model with zero living harvest cannot supply a regional routing response.

For several ecosystems, sum the same named routes across the complete fixed PPR
cohort, then take their minimum and maximum. Require compatible responses for
every included ecosystem and at least two common routes. Do not sum unrelated
regional extrema or silently drop unsupported regions. Ratio bounds use the same
selected NPP denominator; if it is missing, ratio bounds are blank while valid
carbon bounds remain in the data/CSV. Hide/show must be recorded consistently.

The frozen 2026 study reported 31 production method/scope combinations: Humboldt 5,
Guinea 12 and Bay 14. Okhotsk has zero source-model harvest; other models are
untested. Humboldt's documented offal route does not establish an observed
experimental discard amount; Bay/Guinea lack a verified return destination.
No global proxy band is available. See the study's `METHODS_AND_FINDINGS.md`,
`NUMERICAL_NOTES.md` and `INTEGRATION_PROPOSAL.md` for quantitative findings.

## Coordinated rebuild and checks

Finish the canonical extraction before final publication. If parallel agents are
working, assign one owner per exporter/output; model and central builders have
separate output paths, but no reader should certify a workbook while it is being
replaced. Atomic temporary workbooks must not enter published model inventories.
Check built identities and explicit skip reasons, not exit code alone.
Use the existing atomic-save helpers for workbooks and atlas text outputs;
Windows can reject opening an existing destination for truncation. A failed
replacement must leave the previous complete artifact available.

Use the current regional/project/map commands and applicable workflow_checks for requested publication; no historical builder command is an active route. Recheck actual controls/exports and distinguish handler tests from an observed saved download. Full global scientific verification belongs to a requested global reproduction, not an administrative relocation or bounded selection.

Preserve both historical Jensen calculations and their source evidence. Fresh diagnostics obey the active direct GE/TE/With Egestion contract; broad inventories or Monte Carlo need their own authorization. Never execute the broad create_PPRS_excel.py CLI merely to fill evidence. Selection, adoption, scientific repairs, fresh runs and researcher approval remain separate; a documentation update does not authorize them.
