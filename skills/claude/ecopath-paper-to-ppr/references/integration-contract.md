# Annual PPR, NPP and discard sensitivity in GlobalPPREstimation

Read for integration or publication after mapping. Paths below are relative to
the checkout, not the installed skill. This contract describes the implemented
pipeline; source availability and output counts must be checked from current
reports instead of inferred from an old example.

## Final mapping weights

`data/<unit>/<unit>.xlsx` and `data/<unit>/models/<model-stem>.xlsx` both contain
**Final mappings**. Each row identifies unit, model, taxon and assigned group,
with the numerical weight actually used, basis, confidence, evidence and explanation.
Unresolved taxa remain visible. Central sheets keep model identities separate.

The input CSV may contain a basis name or blank fallback rather than resolved
numbers. The companion `.resolved.csv` formats weights to six decimals; use the
numeric **Final mappings** sheet for the complete persisted precision. Rebuild
both workbook types after an authorized mapping change and run
`python -X utf8 tools/verify_final_mappings.py`. The September 2026 audit matches
4,042 assignment rows across eight central and ten model workbooks; these are
verification counts, not a target for future models.

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

Use `NPPExtraction/ANNUAL.md` for current setup and source discovery. From
`NPPExtraction`, the tested Windows setup is:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[test]"
.venv/Scripts/python.exe -m pytest tests -q
```

Linux/macOS use `.venv/bin/python`. Python 3.13 matches the tested dependency
lock; the editable installation can resolve compatible dependencies for 3.11.
Native NetCDF/HDF readers have Unicode-path handling in this package. Retain
HTTPS verification. Raw and decoded caches need substantial disk and are ignored
by Git; a new clone downloads them from documented sources.

The published history covers all 366 identities for 1998–2019, including two
without catch. Check current `output/regional_expansion/publication_verification.json`
and `data/annual_npp_validation.json`; `output/extraction_coverage.json` describes
the earlier archived subset. The September 2026 expansion preserved all 11,310
original rows field-for-field, added 4,398 computed supported records and reused
14 original computed cells. The resulting 25,211-row CSV has 8,050 supported
rows plus the two retained legacy 2019 cells. These are release evidence, not
constants to force onto a different source inventory.

Validate shipped outputs before deciding to recompute. For a requested full
reproduction, use a separate output workspace or isolated checkout: the archive
`npp.annual plan --refresh-sources` / `npp.annual run` route constructs the original
base, followed by `tools/expand_regional_npp.py plan`, serial `extract --years
1998:2019`, and reviewed `publish`. Do not run the archive-only writer over an
expanded canonical release. The expansion plan binds its original CSV snapshot,
full geometry, raw sources and executed code; its extraction requires those
frozen inputs. Follow `docs/REGIONAL_NPP_EXPANSION_HANDOFF.md` for the applicable
run and `NPPExtraction/ANNUAL.md` for setup. Catch availability must not filter
the supported NPP history, and NPP-only rows must not manufacture catch.

`tools/npp_data.py` is the shared adapter. Canonical `npp_*_tC_yr` fields are already
regional totals on the supplied gap-filled baseline; read them directly. For the
legacy 2019 reference, the matching totals are `scaled_*`, not its unscaled
`npp_*` columns. Never apply the regional scaling twice. Original reference-run
statistics and the annual archive subset have different coverage.

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
separate sets. The current atlas displays 366 identities; 167 belong to its
curated archive and ten to its selected model set. `network.simple_units` supplies
independent catch-taxon TL estimates for All-scope simple PPR and regional PPR/NPP.
Use the shared catch components and simple calculation from `tools/simple_atlas_data.py`;
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
not change with selected ecosystems or available PPR. Read
`docs/GLOBAL_ATLAS_NPP_REFERENCE.md` for its calculation and annual support.

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

Hash actual raw bytes at validation boundaries: path, size and modification time
can all survive a byte replacement. The completed regional helper is frozen
historical code with a metadata-based checksum cache. Its separate uncached audit
`tools/verify_regional_npp_sources.py` checks all current planned monthly files
and binds its report to the plan, publication, annual CSV and yearly provenance.
The September11 audit passed1,104 files/32,049,287,447 bytes; it does not prove
uncached checking at every past extraction boundary. For a future extraction,
first harden a versioned helper to hash every validation boundary and create a
fresh plan/cache identity. Preserve the completed helper and execution snapshots.

When exact bytes are hashed, preserve them through Git using the repository's
scoped attributes and compare staged blob bytes with the audited working files.
Line-ending normalization can invalidate a scientifically unchanged source hash.
Retain original evidence and code snapshots; do not rewrite them to match a new run.

Maintain `external/ARTICLE_REFERENCE_USE_LOG.md` and its JSON through
`external/build_reference_use_log.py`, then run `--check`. Distinguish archived
candidates, selected sources, verified computational inputs, isolated validation,
rejected references and contextual methods. State what each reference supports;
catalog membership alone is not numerical use or fresh bibliographic verification.
Regenerate after hashed evidence changes, and exclude separately owned unfinished
research from integration unless its inclusion is explicitly authorized.

## Transfer discard-routing responses

The production reader is `tools/discard_data.py`; its versioned input is
`research/discard_sensitivity_2026_09_10/results/discard_responses.v1.json`.
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

The 2026 study supports 31 production method/scope combinations: Humboldt 5,
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

Unset `PPR_ANNUAL_NPP_PATH` for a canonical release; an override is only a named
immutable intermediate snapshot. From the checkout, rebuild base workbooks,
model workbooks, network atlas, then time series using their existing tools.
Run the relevant independent checks:

```text
python -X utf8 tools/verify_model_workbook.py
python -X utf8 tools/verify_annual_npp.py
python -X utf8 tools/verify_final_mappings.py
node tools/verify_unidentified.cjs
node tools/verify_discard_views.cjs
node tools/verify_simple_map.cjs
python -X utf8 tools/verify_global_npp_reference.py
node tools/verify_npp_graph.cjs
python -X utf8 tools/build_time_series.py --check
```

Require full global verification without partial-history flags for final delivery.
Recheck actual map/graph controls and exports after rendering; distinguish a
tested export handler from an observed browser-saved download. The old
`tmp/verify_task14.py` default-PPR comparison predates the authorized landings
default; it is superseded by three-basis and source-workbook audits. Preserve
both Jensen calculations and use `tools/run_sppr.py` with explicit model IDs if
SPPR regeneration is required. Never execute `PPREstimation/create_PPRS_excel.py`,
including for help. A skill update or integration check does not authorize
publishing a new model, changing source parameters, or completing deferred research.
