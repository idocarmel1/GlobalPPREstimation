# Hernvann et al. (2020): Celtic Sea 1985 extraction and diagnostic review

**Status: source extraction completed; numerical SPPR admission blocked.** Model ID: `Hernvann_2020_Celtic_Sea_1985`. No selection, regional PPR publication or workbook changes were made.

## Sources and model identity

Hernvann P.-Y., Gascuel D., Grüss A., Druon J.-N., Kopp D., Perez I., Piroddi C. and Robert M. (2020), *The Celtic Sea Through Time and Space: Ecosystem Modeling to Unravel Fishing and Climate Change Impacts on Food-Web Structure and Dynamics*, Frontiers in Marine Science 7:578717. DOI: 10.3389/fmars.2020.578717.

The 26-page article and the complete 70-page Word supplement were inventoried and hashed alongside metadata and README. The article is `pdf-fbcccb63.pdf`; the supplement is `Data_Sheet_1_TheCelticSeaThroughTimeandSpa-165f24b6.docx`. Exact hashes are in `source_inventory.json`. The skill renderer failed because bundled LibreOffice is unavailable; read-only Microsoft Word export produced `supplement_word_render.pdf`. Its printed page numbers match the page locators below. XML table-cell extraction retained decimal text, blank cells, explicit zeros and bold runs. Relevant table layouts and prose were checked in rendered images in `visual_evidence/`.

The sole fully tabulated Ecopath parameterization is the **1985 baseline**. B4 combines its input parameters and post-balancing estimates (bold); it is not a second initial model. B2 is explicitly the 1985 diet, derived from 2016 EcoDiet information using relative prey-abundance changes (supplement pp. 7–8). Neither the 2016 diet prior nor the inherited 1980/2013 Moullec models is a complete separate parameterization in this bundle. The 1985–2016 simulation is not 32 independent Ecopath models.

The article p. 6 reports six additional Ecosim-generated mean-period Ecopath snapshots, used for Ecospace. The supplied supplement contains environmental maps, dispersal parameters and vulnerabilities, but no complete B/PB/QB/EE/diet/fishery sets for those six snapshots. These are recorded as unavailable parameterizations in `model_inventory.json`; no synthetic model.json is made for them. Source period labels conflict: article p. 6 says 2005–2010 and 2011–2016; maps/table 8 use 2005–2009 and 2010–2016. This conflict remains recorded.

## Source tables and mapping

| Source | Rendered page | Structure and extraction |
|---|---|---|
| B1, DOCX table 1 | 9–13 | 214 body rows, species composition and guild definitions; 54-row Taxonomy.xlsx after explicit group-name/life-stage crosswalk |
| B2, tables 2–3 | 14–15 | Prey rows 1–54 and Import; predator columns 1–25 and 26–50; all 2,750 source cells retained |
| B3, table 4 | 16 | Landings/discards, 54 groups; Anglerfish/Hake/Cod aggregate headings and final Sum are not groups |
| B4, table 5 | 17 | ID, group, TL, B, P/B, C/B, EE, P/C, BA, Unassim; C/B→QB, P/C→PQ, BA(y−1)→BA rate, Unassim→GS |
| B5/B6 and Fig. B1–B8 | 18–26 | Pedigree and PREBAL context; not additional final input matrices |
| F1–F3; G1 | 61–66; 68 | Ecosim controls, time-series inventory, vulnerabilities and Ecospace dispersal; not additional Ecopath baselines |

Biomass is printed t/km²; annual rates are kept as printed. B3 omits units in its local caption; its values are carried as the Ecopath fishery density inputs, conventionally t/km²/year, without conversion. This unit interpretation is distinguished from an explicit caption statement. No numeric study area or wet/dry conversion was supplied, so none was invented. B4 sometimes labels rates redundantly as /y−1; their intended annual-rate interpretation follows the table and model context.

Exact numerical precision is kept in the eight import tables. Decimal commas were converted to decimal points only. `0.00` bird biomass is a **printed zero**, not an unknown solved to an arbitrary positive number. All catch rows include explicit zeros. Source spelling differences are retained in `group_name_crosswalk.json`, including carnivorous/piscivorous demersal elasmobranchs.

## Biomass accumulation, assimilation and deliberate blanks

B4 supplies BA rate for every group: zero except Plaice −0.01/year, Discards 0.40/year and Detritus 3.88/year. Those rates stay in the rate column; the converter's absolute BA is an explicitly derived rate × printed B (Plaice −0.0004, Discards 0.1, Detritus 481.12 t/km²/year). No balance-check suggested BA was adopted. The large detritus value follows the published BA column and is not reclassified as an import. Article and complete supplement prose, tables and PREBAL figures were searched for alternatives.

All 50 consumers have source GS values; no default GS was needed. B4 PB is blank for six adult/juvenile groups 9–14, EE is blank for Megrim (18), producer/detritus QB is blank, and habitat-area fractions, detritus imports and numeric detritus-fate fractions are absent. B1–B6, SA equations, SF stability discussion and SG were checked. SF p. 57 links the discard pool to fishing, but does not provide a numeric mortality/egestion routing matrix; this qualitative statement is not expanded into invented fractions.

`computable_unknowns.json` and `computational_copy.json` document Megrim EE from the production equation, and the algebraic PB=PQ×QB candidates for six life stages. There are **no missing biomasses** for a coupled B/EE solve; all B values are present, including the printed zeros. These derivations do not replace source fields. Multistanza transfers and the consistency of rounded source PQ remain unresolved, so the computational copy is not a validated EwE reconstruction.

## Source balance and internal conflicts

The import validator reports **0 errors and 54 warnings**, all for missing detritus fate. The independent source mass-balance check reports **2 errors, 15 warnings and 44 notes**; full per-group values are in `source_massbalance.log` and `independent_source_balance.json`.

With the published diet, catch and BA, reconstructed EE is **1.0124673643 for Haddock** and **1.0264833333 for Plaice**. Printed B4 values were visually confirmed and retained. Eleven printed/recomputed EE differences exceed 0.05; the largest is Carnivores/Necrophages, about 0.247. These are reconstruction findings, not evidence that the authors' full-precision native model necessarily failed. Missing transfers/migration, precision and differing source parameter stages can matter. No rates, catches or diets were changed to force balance.

Printed PQ is also inconsistent with PB/QB beyond simple two-decimal rounding for groups 46–48 and Bacteria (50): bacteria prints 0.31 but PB/QB=0.40. PREBAL figures have additional apparent differences from B4 (for example juvenile hake PB). Graph axes are logarithmic and were not digitized into replacements. Both source forms remain available for review.

## Converter and round-trip checks

The maintained writer produced all eight EwE import files and the maintained converter generated its original JSON and reconstructed workbook. `converter_raw.json` preserves that result. The converter normalizes rounded diets, defaults habitat area to 1, drops PQ/TL and explicit-zero diet cells, and combines landings+discards. These transformations are not accepted as source data. `model.json` restores source diets, explicit zeros, source PQ/TL and unknown habitat/routing sentinels; each restoration is recorded in `converter_source_restoration.json`.

A second reconstructed workbook was generated from the restored source database JSON. Automated checks compare every source parameter, all 2,750 diet/import cells, all total catches, reconstructed basic parameters, taxonomy and TL, and unchanged source hashes. See `verification_summary.json` and `verification_checks.json`. The converter's workbook still collapses blank diets to zeros, merges landings/discards into export and omits PQ: it is a numerical cross-check, not a lossless replacement for the authoritative eight tables and evidence. The local serialization number 2402020 is not an EcoBase accession; its filename is solely required by the loader. Run reconstruction and diagnostics with Python UTF-8 mode (python -X utf8) because the preserved loader/converter use the Windows default text encoding; an initial taxonomy-encoding mismatch was detected by verification and corrected by rerunning in UTF-8 mode.

## Requested direct diagnostics

| Requested call | Outcome | Raw return |
|---|---|---|
| diagnose_sppr(TE_option='GE', short=False, flat=False) | NOT_RUN: constructor admission failed | None |
| diagnose_sppr(TE_option='TE', short=False, flat=False) | NOT_RUN: constructor admission failed | None |
| diagnose_sppr(TE_option='With Egestion', short=False, flat=False) | NOT_RUN: constructor admission failed | None |

Strict source admission and standard defaults both raise on diet sums, which range **0.996–1.002**. At a 0.001 tolerance the actual loader flags 19 consumers, including floating-point boundary cases. A separate, explicitly documented use of the loader's `normalize_DC=True` option confirms the deeper blocker. Its exact exception is:

> det_fate carries no detritus routing for any living group. For a multi-DET model the per-pool split cannot be inferred -- supply DetritusFate data for model with detritus groups [53, 54].

`loader_audit.json` retains exact exceptions/tracebacks; `diagnostics_results.json` retains the three NOT_RUN records. Loader tables document sentinel conversion, synthetic import group 55 and forced detritus self-routing identity. The source JSON remains unchanged. No full calculator exists after this exception, so convergence, residuals, negative coefficients/contributions and configuration health are unavailable rather than zero or passing. No global diagnostic, broad 22-method inventory or Monte Carlo was run. No detritus pooling/routing repair was attempted.

## Eligibility and registration

Extraction is complete for what is published; the candidate is **not production eligible**. The first missing numerical requirement is the authors' detritus routing; native/full-precision parameters and life-stage configuration would also resolve remaining source conflicts. The model covers the Celtic Sea shelf part of LME_024 only, with no supported coverage percentage. Taxonomy was captured for future matching, not matched to regional catches. `central_registration_proposal.json` contains one paper update and one candidate model row for the parent's controlled central registration. Selected model and regional results remain untouched.
