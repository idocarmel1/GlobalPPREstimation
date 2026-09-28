# LME049: model decisions and remaining limitations

Updated 28 September 2026. The selected model is **49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)**. This is an adopted assumption variant of Watari et al. (2019), representing 2013. It is selected in the regional workbook, while model-based annual PPR remains pending scientific review. Selection does not turn every method or undocumented input into a validated result.

## Decisions in order

| Date | Decision | Reason and boundary |
|---|---|---|
| 2026-09-28 | Extract both Watari 2019 and Chen 2025 | Preserve the available alternatives, source evidence, taxonomy and numerical limitations. Each source supports one published parameterization. |
| 2026-09-28 | Prefer the Watari source | The user preferred its finer 41-group structure. This initial source preference did not select an exact model. |
| 2026-09-28 | Retain the original Watari model as extracted | Its 35 consumers, three regional phytoplankton groups and three detritus pools form one linked spatial model. The available source did not specify detritus routing. The original failed loading before any SPPR methods ran. |
| 2026-09-28 | Approve a separate detritus-only pooling experiment | Merge only the three detritus pools; retain all consumers and all three phytoplankton groups. Preserve the original model and sources. Do not invent the missing spatial routing. |
| 2026-09-28 | Select the exact 39-group experimental model named above | The user explicitly chose the altered model because detritus-routing data were unavailable. This adopts a documented assumption scenario; it does not establish that the assumed routing was observed. |
| 2026-09-28 | Defer investigation of the TE failure | The user wants the reason investigated later. The request is recorded; no new repair, sensitivity experiment or diagnosis of its cause has been undertaken. |

## Authorized alteration

Original groups 1–38 retain their identifiers. Original detritus groups 39, 40 and 41 map to experimental group 39. All 35 consumer scalar parameters and catches, the three phytoplankton records, and all non-detritus diet fractions are unchanged in the derived canonical JSON.

The published **total-model-area** detritus biomasses are summed: **9.58 + 6.04 + 28.50 = 44.12 t/km²**. Habitat fractions are not applied again. The pooled habitat area of 1.00 defines the derived whole-domain representation. The source model covers 913,102 km²; these are model-area quantities, not a newly verified percentage of the LME.

For each consumer, the three detritus prey fractions are summed exactly. Every consumer's full diet total is preserved, including the source's rounding discrepancies. Detritus EE is left unknown, not averaged. No extra catch, import or undocumented internal detritus transfer is added.

The new shared pool assumes mixing across OYC, KC and offshore blocks. The existing single-pool loader routes all living other-mortality and egestion flows to that pool, with full internal retention. **Missing routing data are not evidence for observed 100% retention.** The actual spatial recycling and external losses remain unknown. Habitat fractions 0.2/0.2/0.6 do not establish those routes.

See the [exact group map](original_to_derived_group_map.csv), [diet aggregation](detritus_diet_aggregation.csv), [unchanged diet totals](consumer_diet_totals.csv), [changes-only audit](changes_only_audit.json) and [derivation manifest](derivation_manifest.json).

## Incidental calculation transformations, not additional source corrections

The canonical source and derived JSON retain published precision and missingness. The computational loader additionally:

- Normalizes 83 diet cells across consumers 2, 3, 5, 6 and 8. Their printed totals are 0.995, 1.012, 1.002, 1.002 and 1.005.
- Defaults missing catches, migration and imports to zero and regular-group unassimilated consumption to 0.2. Seventeen source groups have missing catches represented as zero in the loaded table. Five source catches are censored as `<0.01`; none is a measured zero.
- Replaces the censored seabird biomass `<0.01` with 1 t/km² and changes its printed PB 0.12 and QB 36.67 to zero in the completed table. These consequential artifacts remain unresolved; they are not published values or a new user-authorized repair.
- Adds a zero-flow diet-import bookkeeping group and solves missing flows, including biomass accumulation. The source contains no numerical BA values for these groups.

All 299 mapped scalar differences/completions, the full raw-to-completed field inventory and diet changes are retained in [the loader audit](loader_audit_summary.json), [scalar transformations](all_loader_scalar_transformations.csv), [diet transformations](all_loader_diet_transformations.csv) and [full field inventory](all_raw_to_completed_fields.csv).

## What the calculations establish

Pooling removes the original multiple-detritus loading obstacle. All 22 method workers completed in about 80.47 seconds with no timeouts. The budget was 180 seconds per method and 100 draws for each Monte Carlo method; no seed was fixed. Existing audited outputs were retained after checking the exact model hash, rather than generating another stochastic realization just to record selection.

| Configuration | Numerical health | Living spectral radius | Recycling gain | Relative SPPR balance gap | Monte Carlo |
|---|---|---:|---:|---:|---|
| GE | OK under configured thresholds | 0.33343023 | 0.04017288 | 0.00676480 | 100 accepted / 100 requested |
| TE | FAIL | 0.54627838 | 0 | 0.03354352 | 0 accepted; 100 rejected as diverged |
| With Egestion | OK under configured thresholds | 0.26674419 | 0.04571817 | 0.00387648 | No separate MC method in this run |

GE and With Egestion provide finite **conditional estimates for the completed assumption scenario**. Their health label does not establish complete source evidence. Both have `balance_is_balanced=False` under the strict equality check, although their gaps are below the warning threshold. TE remains excluded: a living spectral radius below one does not erase negative basal-source coefficients.

Completed production and consumption balances have maximum absolute residuals near 1.14×10⁻¹³, but unknown BA absorbs residual flows. The pooled detritus receives 1,075.514299 t/km²/year and has direct predation of 53.887700, leaving **solved BA +1,021.626599 t/km²/year** with assumed external loss zero. That large accumulation is not source evidence of steady state. The three phytoplankton BA values are −1.373122, +0.299280 and −1.496462. Source-level balance remains indeterminate for seven groups. The detritus utilization ratio 0.0501041 is a diagnostic budget ratio; loader EE=1 is a bookkeeping convention, not its published EE.

At the user's request, the [current SPPR report](../../extraction_review_20260928/SPPR_DIAGNOSTICS_REPORT.md) contains only direct `diagnose_sppr()` outputs. All four advertised TE options were called; `global` raised an exception in the current implementation and returned no diagnostic object. No fix was attempted. The [archived full research evidence](../../extraction_review_20260928/EXTRACTION_AND_FULL_METHOD_EVIDENCE_20260928.md) retains all methods and scopes, negative groups including unfished groups, MC counts and the separate Chen candidate. [Settings](../diagnostic_settings.json), [code hashes](../diagnostic_code_hashes.json), [coefficients](../all_source_group_sppr_diagnostics.csv) and [basal-source coefficients](../all_basal_source_coefficients.csv) preserve the evidence.

## Deferred TE investigation requested by the user

The cause is **not yet established**. Recorded symptoms are:

- Four negative basal-source coefficients for seabird group 3: detritus 39 and primary producers 36, 37 and 38. Their magnitudes are approximately 6×10¹⁵ to 1.45×10¹⁷. That group's catch is defaulted to zero, which does not make the negatives irrelevant.
- Two near-singular TE cases and a 3.354% SPPR balance gap.
- Zero accepted TE Monte Carlo draws out of 100, all recorded as diverged.
- Living spectral radius below one, alongside the failures above.

The seabird input/completion artifacts are relevant observations, not a proven explanation of the TE failure. No causal conclusion, corrective value, larger MC run or sensitivity scenario has been supplied. The next investigation should distinguish source missingness, loader completion, transfer-efficiency definitions and numerical singularity while retaining the existing evidence.

## Downstream status and remaining evidence

The regional selection is saved, the previous workbook is archived, and stale model outputs were cleared with the supported prepare-selection workflow. Catch, independent classic PPR and NPP blocks are preserved. Model-based annual PPR and PPR/NPP remain pending; no coefficient from a failed configuration is published.

Independent catch-taxonomy preparation uses exact published membership despite the TE failure. [Seven catch labels](source_supported_matching_preparation.csv) exactly match unambiguous single-species source groups, out of 253 catch taxa; the other 246 remain explicitly unresolved. These seven represent 638,235.18 tonnes, or 20.65% of available 2019 total catch (21.03% of landings). This is membership-evidence coverage, not approved numerical PPR coverage. [Annual coverage and all three catch bases](exact_membership_coverage.csv) and the [largest unresolved taxa](matching_preparation_summary.json) are retained. Detailed membership for pooled groups remains incomplete because the Watari supplement could not be archived (HTTP 401). Coarse taxa and spatially split groups require evidence-supported memberships and weights, not matching by name or TL alone.

The mapper's scientific workflow says, “Check `usable` first” and “If it is not usable, say so and stop.” Here that limits promotion of mappings into accepted annual calculations while source-admission concerns remain; it does not invalidate exact independent membership evidence or imply that every numerical method failed. Existing executable gates also exclude negative group coefficients and failed exact configurations. GE/Egestion results remain explicitly conditional because the seabird/default and accumulation artifacts have not been resolved. The user selected the pooling assumption, not unspecified further numerical repairs.

Central registration and map refresh are coordinated separately to preserve concurrent regional work. The experimental candidate must be added alongside, not replace, the [original 41-group JSON](../../49_20192013_Western_North_Pacific_Watari_(2013)/model.json). The [selected experimental JSON](../model.json), [frozen source](source_model_frozen.json), [publication manifest](source_publication_manifest.json) and [selection verification](selection_verification.json) identify the exact artifacts used. No original source bytes were changed.
