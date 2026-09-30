# Model validation template filling guide

Template version 5, 30 September 2026. Use with `Model_validation_template.docx`.

This guide accompanies the reusable template. It is not a skill and is not part of the filled report. The report follows the researcher's edited `regions/LME_036/Model_validation.docx`, with the subsequently agreed mapping section and linked Excel appendix. Examples below illustrate rules; they are not newly verified classifications or results for LME036.

## Scope and evidence

- Fill a record for the specified region and exact selected model version. Read the relevant project instructions and current paper-to-PPR workflow for definitions. Use the regional selection record, article inventory, original sources, model files, saved diagnostics and mapping evidence. Do not invent a selection when none is recorded.
- Filling this report does not authorize extraction, regeneration of model coefficients, changes to mappings or scientific inputs, or another scientific pipeline run. Use existing results and the arithmetic needed to summarize them. Report missing evidence explicitly.
- Preserve researcher text, deletions and edited hyperlinks when updating an existing filled record. The SPPR calculation, Open issues and next action, and Review and reproducibility cells are manual. Do not infer that a note about excluded groups proves the exclusion has been applied in saved outputs.
- Keep the main report concise. Replace placeholders with findings; remove unused optional prompts. Do not include this guide, AUTO labels, a process narrative, the old completion-instructions section, a template version line or repetitive provenance caveats in the filled report.
- Keep the template general: do not copy the LME036 numerical results, group exclusions or selection choices into every region's report.

## Report fields

Use the template's field order, allowing tables to flow over pages. Repeat table headers and avoid clipping. Preserve its fonts, margins and restrained table formatting.

| Field | Filling rule |
|---|---|
| Region | Name, identifier and regional workbook link. |
| Catch source | Provider, catch-year range, catch basis, concise available date/version, region and local catch links. Do not add routine hash-check prose. |
| Selected article | Authors, year, title, DOI, local PDF and paper-folder links where available. |
| Other known articles | Short bibliographic entries and useful DOI/local links from the known inventory. Do not claim an exhaustive search. |
| Selected model | Exact model ID/name, period, domain, source-group count and useful model folder/JSON/runtime links. Link JSON to the actual selected model file; identify an archived snapshot explicitly if one is needed instead. |
| Other models from the same article | Briefly describe each known alternative by name, period, area and distinguishing model features. Keep source models separate from scenarios or extraction variants. For the current example, the 1970s counterpart belongs here. An unreviewed article inventory is not evidence that no alternatives exist. |
| Selection rationale | Separate **Article** and **Model** reasons. State documented reasons for choosing this article among articles and this model among alternatives. A description of what was selected is insufficient. Preserve the researcher's reason; use `?` for an unrecorded reason. |
| Model extraction | Short findings on source conflicts, diet-sum discrepancies and their treatment, missing/default GS, derived BA, or other material transformations. Distinguish source facts, defaults and derived values. Include directly useful reconstruction/conflict links. Do not label a discrepancy rounding-only unless supported. |
| SPPR calculation | Preserve researcher choices and reasons, excluded groups and the scope of exclusion, and any adjustments. Leave manual placeholders when unfilled. |
| GE diagnostics | Identify every SPPR source column containing negative values and list the affected groups for each column, using source/group names and IDs. Also report rho_living, b, and detritus SPPR by named pool. |
| TE diagnostics | Identify every SPPR source column containing negative values and list the affected groups for each column, using source/group names and IDs. Also report rho_living and detritus SPPR by named pool. Do not interpret an omitted or conventionally zero recycling term as evidence of no recycling. |
| Taxon mapping and coverage | A separate section after the main validation tables. Follow the specification below. |
| Geographic fit | Follow the approximation rules below. |
| Temporal fit | Model period, catch years, and the material consequence of transferring fixed coefficients or weights across years. |
| Other | Optional important additional issue only. Keep empty when none is warranted; do not restore deleted process/provenance paragraphs. |
| Open issues and next action | Manual researcher entries. |
| Review and reproducibility | Manual researcher identity, date, decision, limitations and relevant evidence. Never mark approval on the researcher's behalf. |

Diagnostics must refer to the same saved configuration and model. Do not routinely restore the removed overall-status paragraphs, maximum-group lists, configuration dumps or repeated diagnostic links. Include a short material failure or limitation when omitting it would make the reported result misleading. Preserve such evidence in supporting reports without crowding the summary.

For negative SPPR findings, inspect the **per-source SPPR matrix for the corresponding method**, preserving its source-column and group-row identities. Report each affected source column followed by the groups whose entries in that column are negative, for example `Source A (ID): Group X (ID), Group Y (ID); Source B (ID): Group Y (ID)`. Include every affected source–group pairing; a column count or an unpaired list of groups is insufficient. Do not infer this finding from a summed SPPR total or another matrix. Negative magnitudes may be included when useful. State `No negative SPPR values in any source column` only after checking the matrix; if the matrix is unavailable, state that the finding cannot be determined.

## Taxon mapping and coverage summary

Use a separate Word section, outside the main validation tables. It contains:

1. **Reference:** selected year and catch basis, including what the basis comprises.
2. **Totals:** number of model groups; number of catch taxa; total catch in tonnes; total simple-trophic-chain PPR in tonnes C.
3. A five-row table: **High, Medium, Low, Very low, Unresolved**, with columns **Taxa (n), Catch (%), Simple-chain PPR (%)**.
4. **Group assignment rules:** a table with the exact columns **Plain-language rule | Confidence | PPR percentage**.
5. **Allocation weight rules:** a separate table with the same exact columns. Include every actually used rule, split by its component confidence when one rule occurs at multiple levels. Use full human-readable descriptions, without M/W codes or numbered-reference shorthand. Put descriptive source links nearby. Link the Excel appendix and its Sources sheet.
6. A missing-PPR note when needed: number of affected taxa and their catch share. Omit the note when all coefficients are available.

Each rule-table percentage is the share of known independent simple-chain PPR for taxa using that rule. Ecopath allocation weights do not generate classic PPR. Each table partitions the same complete known-PPR universe once; unresolved or not-applicable records must be explicit. Each table sums to 100% independently; never add the tables together. The confidence column describes the assessed component (membership or weights), while the five-category summary uses the weakest necessary component. Use at least four decimal places when useful; show a smaller positive share as a nonzero value or a stated threshold.

**Map reconciliation is a completion gate.** Trace the current generated payload and the actual browser controls/result for the same region, year, basis, units, source scope, unidentified treatment, taxon/group filters and missing-value policy. Record the unrounded value and visible rounding. A workbook annual match alone does not verify the UI. If a group subset is active, distinguish its allocated simple-chain view from the independent all-taxon universe and select/record the intended view explicitly. Diagnose and fix the underlying authorized data/display mismatch; never paste a map number into prose. Use the same verified denominator in Word and Excel.

Counting and denominator rules:

- Count source ecological model groups once. Exclude a synthetic computational import group from that count and, if present, identify it separately, for example `38 source groups (+1 computational import)`. This total is the model inventory, not just the groups receiving catch or retained in a particular calculation.
- Define one catch-taxon universe for the selected year and basis and use it for the summary and appendix. Include all recorded taxon labels for that basis, including zero-catch labels; do not silently filter unresolved labels. Count each label once, even if it maps to several groups. Resolve duplicate records within the same label before counting; do not silently merge different labels just because they are synonyms.
- Each taxon belongs to exactly one overall confidence category. Counts sum to the total number of taxa.
- Catch share for a category is 100 times its catch divided by total catch across that universe, including unresolved mappings. Use the same year, basis and units throughout. With total catch zero, percentages are unavailable, not zero.
- Simple-chain PPR is independent of Ecopath group mapping and of the selected GE/TE coefficients. Use the configured classic/simple-chain method and its documented taxon TL or coefficient, transfer-efficiency assumptions and carbon conversion. Do not silently substitute model TL or GE/TE PPR. Avoid a second carbon conversion when saved values are already in tonnes C.
- Simple-chain PPR share is 100 times the category's available simple-chain PPR divided by the total available simple-chain PPR. Unresolved model mappings can still have known simple-chain PPR and must remain in this denominator.
- If simple-chain coefficients are missing, label the total and percentages as **known simple-chain PPR** and disclose the missing taxa count and catch share. Missing values are not zero. If no positive PPR denominator is available, show `?` for the shares and explain why.
- These are category shares, including for Unresolved; do not call its share "covered." Catch and PPR category shares each sum to 100% when their denominators are available, allowing displayed rounding.
- Use sufficient precision for consequential small shares; a positive share below display precision can be shown as `<0.1%`. Do not hide a positive unresolved share as zero.

## Confidence rules and examples

Assess **membership confidence** and **allocation-weight confidence** separately in the supporting record. The report and appendix show the weaker required confidence. An online search is a way to obtain evidence; it does not by itself establish high confidence. Researcher approval does not raise evidential confidence.

### Coverage preference and the Very low category

Prefer approaching 100% catch coverage through transparent assumptions over leaving taxa unresolved merely because a mapping is uncertain. A practical taxonomic or ecological connection is sufficient for a provisional **Very low** assignment when stronger evidence is unavailable. This is a coverage preference, not a claim of greater scientific correctness. Never change group SPPR, fabricate observations or classify a weak analogue as a documented source member.

For broad labels, include compatible named groups as well as residual pools; do not restrict them to residual pools without justification. For an absent explicit species or habitat compartment, use the closest represented taxonomic/ecological analogue and record the mismatch. Source-model catch proportions, then biomass, can weight those candidate sets. Preserve better-supported existing mappings. Use Unresolved only when no meaningful group/analogue can be chosen, source evidence contradicts every candidate, or no usable numerical allocation can be justified. An arbitrary group selected solely to reach 100% is not an analogue.

Very low is below Low and above Unresolved. Apply the weakest-component rule in the order High > Medium > Low > Very low > Unresolved. Record actual source membership separately from assumed analogue membership and report the share of coverage dependent on Very low assignments.

### Membership rules

| Rule | Confidence | Example and boundary |
|---|---|---|
| M1 Explicit source assignment | High | A source group-definition table explicitly includes Pennahia in Small croakers. The source must identify this model/version and the relevant taxon. |
| M2 Verified synonym | High | An authoritative taxonomic source establishes that the old model name and current catch name identify the same taxon. Synonym resolution alone does not resolve otherwise ambiguous group membership. |
| M3 Unambiguous documented group fit | High | The model defines a group as all members of a family; an authoritative source confirms the catch species belongs to that family. All relevant size, stage, habitat and geographic criteria must also be satisfied, with no competing group. |
| M4 Extension from listed representatives | Medium | A group lists several species from a family, and another related species is included on supported taxonomic/ecological grounds. The unlisted membership remains an explicit assumption. |
| M5 Supported ecological assignment | Medium | Documented size and habitat support Small demersal fish, but the model does not directly enumerate the species. State the assumed group boundary. |
| M6 Partial or conflicting ecological fit | Low | A benthopelagic species is assigned to a demersal group despite an equally plausible pelagic group or incomplete group definitions. If only a weak but meaningful analogue exists, use M11 Very low; use M8 only when no meaningful choice exists. |
| M7 Broad catch category with assumed composition | Medium or low | Marine fishes nei is allocated using a regional composition study: medium for a representative matching study; low for a weak spatial/temporal proxy. Record the components and transfer assumption. When only a broad model-pool composition proxy is available, use M10 Very low; do not require measured composition to avoid Unresolved. |
| M9 Assumed eligible group set | Medium | Taxonomy, ecology and exact model definitions establish the eligible groups for an explicitly authorized model-proportion fallback. Record included/excluded groups and any material membership uncertainty. Use M6 Low for partial evidence or M10/M11 Very low for a weak but meaningful approximation; use M8 only when no meaningful placement exists. |
| M10 Broad-category approximation | Very low | The label spans named and residual groups; allocate among a recorded taxonomically/ecologically plausible set using a stated composition proxy. The exact catch composition remains unknown. |
| M11 Closest represented analogue | Very low | Map an oceanic or deep-water fish to the closest represented functional fish group when the model lacks its exact habitat. State the habitat/geographic mismatch and why this group is the closest usable analogue. |
| M8 No meaningful assignment | Unresolved | No taxonomic/ecological connection or usable analogue can be established, every candidate is contradicted, or no allocation can be justified. Name the taxon and specific remaining obstacle. |

### Allocation-weight rules

| Rule | Confidence | Example and boundary |
|---|---|---|
| W1 No split required | High, no additional uncertainty | The entire catch taxon is assigned to one group with weight 100%. This does not raise a medium/low membership assignment to high. |
| W2 Directly measured allocation | High | Catch-at-age observations determine juvenile/adult proportions for the relevant taxon, area, period, catch basis and model stage threshold. |
| W3 Measured allocation transferred | Medium | Observed stage proportions for one suitable survey year are applied to nearby years with a documented representativeness assumption. |
| W4 Source-model catch proportions | Medium | Juvenile/adult hairtail group catches provide a proxy split for regional hairtail catch. It is an assumption about the target catch, not a direct observation of its composition. |
| W5 Indirect biological/fishery proxy | Medium or low | A proxy outside the approved model-proportion fallback has a documented biological or fishery basis. Explain its applicability; do not use this older rule to downgrade the approved biomass fallback automatically. |
| W9 Approved model-biomass fallback | Medium | If model catch cannot supply complete usable proportions for the independently established eligible set, use model biomass proportions under the explicit composition/catchability assumption. Retain raw values, total, weights and rejected catch attempt. |
| W6 Weak transfer or substantial mismatch | Low | Weights from a distant fishery are transferred despite different practices, or stage definitions do not align well. An irreconcilable mismatch belongs under W8. |
| W7 Supported judgment-based split | Low | A 50:50 split has a specific biological rationale but little quantitative evidence. If only a weak last-resort judgment can be justified, use W11 Very low; use W8 only when no numerical assumption is defensible. |
| W10 Direct source geographic allocation | High | Applicable source data quantify the taxon’s caught mass across geographic strata corresponding to model groups: 80 t and 20 t give 80% and 20%. Record area boundaries, group correspondence, period, basis and quantities. Document any density-to-mass or area-weighted conversion. Geographic range overlap or visual map overlap alone is not measured catch composition; transfers or approximations receive lower confidence. |
| W11 Explicit last-resort allocation | Very low | No usable measured/catch/biomass proportions exist, but a transparent expert allocation can still be justified among meaningful candidates. Record its numerical rule and reason, including any justified equal-share assumption. Never present it as observed. |
| W8 No usable allocation | Unresolved | No observed or assumed numerical split can be justified even under W11. Keep weights `?`. |

### Approved fallback for unresolved taxa

Under explicit adoption authorization, establish eligible groups from taxonomy, ecology and model definitions before allocating. Do not use all groups indiscriminately, infer membership from numerical availability or silently drop a candidate with missing values. Prefer supported direct composition evidence, including source geographic allocation under W10. For the approved assumption route, first use **model catch proportions**, and only if they cannot provide complete usable weights use **model biomass proportions**. Both allocation routes are **Medium**, explicitly assumption-based; approval is authorization to use the assumption, not independent scientific validation.

A usable field has finite nonnegative values for every candidate and a strictly positive total. Preserve genuine zero candidates; missing sentinels and defaults are not observed zeros. Record candidate IDs/names, inclusion/exclusion rationale, exact source fields/values/units, period/basis, total, proportions, fallback trigger and transfer assumptions. If direct membership is uncertain, assess the M10/M11 Very low alternatives before leaving it unresolved; if both numerical source fields fail, assess a documented W11 allocation. Retain `?` only when no meaningful assignment/allocation can be justified. Other material membership uncertainty still lowers overall confidence under the weakest-component rule. The helper `tools/skills/original_skill_resources/combined-src/scripts/assumed_allocation.py` computes only reviewed proportions and never infers membership or edits model coefficients.

Document separately any transfer across years, areas, taxa, landings/discards or stage definitions. A source-model proportion fixed across all catch years is ordinarily W4 with a temporal assumption; for proxies outside the approved fallback, a serious unsupported transfer can lower it to W6 or W8. For the approved catch/biomass fallback, retain Medium allocation confidence and assess material group or stage-boundary conflicts separately as membership uncertainty; an incomplete strict-membership set can instead use a disclosed M10/M11 Very low approximation when a meaningful candidate set is available. Do not infer high confidence from numerical precision or from weights summing to one.

### Short report findings

List every unresolved taxon with a brief specific reason, or state that none remain. Clearly flag Very low decisions, grouping taxa that share the same assumption and naming all affected taxa in the short grouped table or its linked Excel rows. Report their catch/PPR share so high coverage is not mistaken for high confidence. Keep this section concise and scientific: no skill-edit history, approval narrative, integration status, tool/test logs, hashes or other internal workflow details. Detailed provenance and verification belong in supporting evidence.

### Combining confidence and preserving uncertainty

| Rule | Example |
|---|---|
| C1 Use the weakest necessary membership or weight confidence. | High membership plus medium allocation gives Medium overall; low membership plus high weights gives Low. |
| C2 Apply the rule across every required part of a split. | A two-group mapping with one necessary low-confidence assignment is Low overall. |
| C3 A required unresolved component makes the taxon unresolved. | Both stage groups are known but their weights are not: Unresolved overall. Preserve any genuinely known partial weights and mark only unresolved ones `?`. |
| C4 Count the split taxon once and classify all its catch/PPR under that overall confidence. | A taxon allocated to two groups does not add two taxa to the summary or have its catch double-counted. |
| C5 Missing TL/PPR is separate from mapping confidence. | A securely mapped taxon with no simple-chain coefficient remains High for mapping, while its PPR is `?` and its missing-coefficient catch share is disclosed. |
| C6 Stored provisional numbers do not prove resolved weights. | A numerical equal-split placeholder without a defensible basis is displayed as unresolved `?`; explain the stored placeholder in supporting evidence without silently changing the scientific data. |

For each taxon retain membership rule/source/confidence; allocation rule/source/confidence; assumptions and their applicability; overall confidence; and the supporting taxon-to-group decision. Source references must identify the page/table, dataset field or specific online entry and what it supports. Record retrieval dates for online evidence. One reference may support both membership and weights, but explain each use.

## Appendix of all taxon mappings

The full appendix is a linked Excel workbook, not a Word table. Use frozen headers, an autofilter, deliberate column widths, wrapped text and readable row heights. Include a separate descriptive Sources sheet as requested. One row per catch taxon, including unresolved and zero-catch records in the defined universe. **Sort numerically by simple-chain PPR in descending order**, using the unrounded values, with unavailable PPR last; use taxon name to break ties. State this ordering above the table along with the year, catch basis, PPR method, units and applicable source references.

| Column | Content |
|---|---|
| Taxon name | Exact catch-data label; explain synonyms in Reason. |
| TL | Taxon trophic level used for the simple-chain PPR calculation; `?` if unavailable. |
| Catch (t) | Catch in the selected reference year and basis. Unknown catch remains `?`, not zero, and prevents an unqualified complete total. |
| Simple-chain PPR (t C) | Independent simple-chain PPR, or `?` if unavailable. Genuine calculated zero remains zero. |
| Mapped group names and weights | Exact model-group names and percentages, for example `Juvenile hairtail (80%); Adult hairtail (20%)`. Resolved weights sum to 100%, allowing rounding. Use `Juvenile hairtail (?); Adult hairtail (?)` for known candidates with unresolved weights; use `Unresolved` when no candidate is established. Identify tentative candidates as such. |
| Confidence level | High, Medium, Low, Very low or Unresolved under the combined rules. |
| Reason | Brief membership justification and, where required, weight justification, with source IDs and the consequential assumption. |

Example reason: `Membership is explicit in Cheung Appendix 6.1; weights use the selected model group catches, assumed constant across years. See Sources and the allocation evidence.`

Put full descriptive source references and links on the separate Sources sheet. Avoid numbered-reference shorthand in the readable coverage section. Include TL/simple-chain method sources as well as membership and weight evidence. Preserve useful hyperlinks. Put extended uncertainty discussion in the detailed supporting report.

## Geographic fit and figures

- Define R as the target region and S as the selected model study area. A = 100 × area(R ∩ S) / area(R); B = 100 × area(R ∩ S) / area(S).
- Prefer compatible digital boundaries and an appropriate area calculation when available. When coordinates or a verified polygon are absent, use available figure boundaries, coastlines, landmarks, map grids and approximate tracing or georeferencing to make a defensible estimate.
- Identify the result as calculated, approximately digitized, or visually estimated. Use `≈` or a justified range for approximate values. Describe the source figure/page, interpreted study boundary and method briefly; retain more detail in supporting evidence if needed.
- Compare geographic areas using compatible scale/projection; do not compare the raw pixel sizes of differently scaled screenshots. Account for land exclusion and obvious boundary mismatches. Do not invent statistical confidence intervals or spurious decimal precision.
- The researcher's current LME036 example is A ≈ 20% and B ≈ 90–95%, as a visual estimate. These are an example, not universal defaults or a new independent measurement.
- Use `Not determined` only when the available evidence cannot support a defensible approximation, explaining the specific ambiguity. Missing digital coordinates alone are insufficient reason to stop.
- Include the target-region image and the article study-area figure, with readable boundaries, figure/page references and useful source links. Images may occupy separate pages when necessary. If an image is unavailable, retain the labeled space with a short reason.
- Captions and nearby text must allow documented approximate overlap estimates. Remove the old blanket statements that figures cannot establish numerical overlap or that visual estimation is prohibited.

## Links, output and verification

- Keep the user's edited destinations and purposeful deletions. Use concise descriptive link labels and avoid repeated links with no additional value. Preserve URL fragments such as a regional view or a PDF page.
- For a new filled report, use working relative local links to the regional workbook, actual selected model, paper and needed evidence. If supporting reports must be copied into `validation_reports/<model_id>/`, copy rather than move originals; keep referenced assets and record their source paths. Do not fabricate a pre-existing report.
- Save a new filled report beside the regional workbook as `Model_validation_<model_id>.docx`, unless the user chooses another path. Do not overwrite researcher documents without authorization. A template revision updates the template, not a regional report.
- Save the final Excel taxon-mapping appendix in that same region directory, beside the report and regional workbook. Link to it by relative filename. Do not place final regional deliverables under a project-root `outputs` directory; keep temporary builders and QA artifacts separate.
- Verify identifiers, model/version consistency, source targets, count totals, category shares, weight sums, missing values, units and appendix-summary agreement. Preserve manual fields and user edits. Read-only verification or report arithmetic does not authorize a scientific rerun.
- Render the final document and inspect every page. Check table widths, repeating headers, readable figures, captions, page flow and the linked Excel appendix. Verify its numeric types, complete taxon set, full-precision sort order, filters/frozen headers, weights, totals, formula results if any, and readability. Keep QA renders outside the delivered report files.
- Follow the user's current review gate. A request to draft or revise a template or skill ends with that artifact for review; it does not itself authorize a regional test run.

Sort group-assignment rule rows by unrounded PPR percentage, highest first. Add a final Sum row only if the unrounded total differs from 100% beyond numerical rounding tolerance (1e-8 percentage points); show and explain the actual shortfall/overcount rather than changing the denominator. Omit the Sum row when the total is 100%. In a blank template, request descending order without inventing values.
