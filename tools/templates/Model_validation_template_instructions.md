# Model validation template filling guide

Template version 3, 29 September 2026. Use with `Model_validation_template.docx`.

This guide accompanies the reusable template. It is not a skill and is not part of the filled report. The report follows the researcher's edited `regions/LME_036/Model_validation.docx`, with the subsequently agreed mapping summary and appendix. Examples below illustrate rules; they are not newly verified classifications or results for LME036.

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
| Taxon mapping and coverage | Follow the summary specification below. |
| Geographic fit | Follow the approximation rules below. |
| Temporal fit | Model period, catch years, and the material consequence of transferring fixed coefficients or weights across years. |
| Other | Optional important additional issue only. Keep empty when none is warranted; do not restore deleted process/provenance paragraphs. |
| Open issues and next action | Manual researcher entries. |
| Review and reproducibility | Manual researcher identity, date, decision, limitations and relevant evidence. Never mark approval on the researcher's behalf. |

Diagnostics must refer to the same saved configuration and model. Do not routinely restore the removed overall-status paragraphs, maximum-group lists, configuration dumps or repeated diagnostic links. Include a short material failure or limitation when omitting it would make the reported result misleading. Preserve such evidence in supporting reports without crowding the summary.

For negative SPPR findings, inspect the **per-source SPPR matrix for the corresponding method**, preserving its source-column and group-row identities. Report each affected source column followed by the groups whose entries in that column are negative, for example `Source A (ID): Group X (ID), Group Y (ID); Source B (ID): Group Y (ID)`. Include every affected source–group pairing; a column count or an unpaired list of groups is insufficient. Do not infer this finding from a summed SPPR total or another matrix. Negative magnitudes may be included when useful. State `No negative SPPR values in any source column` only after checking the matrix; if the matrix is unavailable, state that the finding cannot be determined.

## Taxon mapping and coverage summary

The single merged row contains:

1. **Reference:** selected year and catch basis, including what the basis comprises.
2. **Totals:** number of model groups; number of catch taxa; total catch in tonnes; total simple-trophic-chain PPR in tonnes C.
3. A four-row table: **High, Medium, Low, Unresolved**, with columns **Taxa (n), Catch (%), Simple-chain PPR (%)**.
4. **Membership evidence:** concise source references and a detailed mapping report or appendix reference.
5. **Weights and assumptions:** short allocation rules, evidence references and affected confidence categories.
6. A missing-PPR note when needed: number of affected taxa and their catch share. Omit the note when all coefficients are available.

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

### Membership rules

| Rule | Confidence | Example and boundary |
|---|---|---|
| M1 Explicit source assignment | High | A source group-definition table explicitly includes Pennahia in Small croakers. The source must identify this model/version and the relevant taxon. |
| M2 Verified synonym | High | An authoritative taxonomic source establishes that the old model name and current catch name identify the same taxon. Synonym resolution alone does not resolve otherwise ambiguous group membership. |
| M3 Unambiguous documented group fit | High | The model defines a group as all members of a family; an authoritative source confirms the catch species belongs to that family. All relevant size, stage, habitat and geographic criteria must also be satisfied, with no competing group. |
| M4 Extension from listed representatives | Medium | A group lists several species from a family, and another related species is included on supported taxonomic/ecological grounds. The unlisted membership remains an explicit assumption. |
| M5 Supported ecological assignment | Medium | Documented size and habitat support Small demersal fish, but the model does not directly enumerate the species. State the assumed group boundary. |
| M6 Partial or conflicting ecological fit | Low | A benthopelagic species is assigned to a demersal group despite an equally plausible pelagic group or incomplete group definitions. If no defensible choice exists, use M8 instead. |
| M7 Broad catch category with assumed composition | Medium or low | Marine fishes nei is allocated using a regional composition study: medium for a representative matching study; low for a weak spatial/temporal proxy. Record the components and transfer assumption. Unsupported composition is M8. |
| M8 No defensible assignment | Unresolved | A mixed catch category spans several groups and no evidence supports its composition or a suitable group. Known candidates may be listed without claiming a resolved assignment. |

### Allocation-weight rules

| Rule | Confidence | Example and boundary |
|---|---|---|
| W1 No split required | High, no additional uncertainty | The entire catch taxon is assigned to one group with weight 100%. This does not raise a medium/low membership assignment to high. |
| W2 Directly measured allocation | High | Catch-at-age observations determine juvenile/adult proportions for the relevant taxon, area, period, catch basis and model stage threshold. |
| W3 Measured allocation transferred | Medium | Observed stage proportions for one suitable survey year are applied to nearby years with a documented representativeness assumption. |
| W4 Source-model catch proportions | Medium | Juvenile/adult hairtail group catches provide a proxy split for regional hairtail catch. It is an assumption about the target catch, not a direct observation of its composition. |
| W5 Indirect biological/fishery proxy | Medium or low | Biomass proportions inform catch allocation: medium with supporting selectivity evidence; low when similar catchability is weakly supported. Record why the proxy is informative. |
| W6 Weak transfer or substantial mismatch | Low | Weights from a distant fishery are transferred despite different practices, or stage definitions do not align well. An irreconcilable mismatch belongs under W8. |
| W7 Equal or judgment-based split | Low if defensible; otherwise unresolved | A 50:50 split has an explicit biological rationale but little quantitative evidence: low. Choosing equal weights only to complete a calculation: unresolved. |
| W8 No defensible complete allocation | Unresolved | Juvenile/adult membership is known, but no observations or justified proxy support the required proportions. Keep weights `?`. |

Document separately any transfer across years, areas, taxa, landings/discards or stage definitions. A source-model proportion fixed across all catch years is ordinarily W4 with a temporal assumption; a serious unsupported transfer can lower it to W6 or W8. Do not infer high confidence from numerical precision or from weights summing to one.

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

Use the landscape appendix and repeat its header on every page. One row per catch taxon, including unresolved and zero-catch records in the defined universe. **Sort numerically by simple-chain PPR in descending order**, using the unrounded values, with unavailable PPR last; use taxon name to break ties. State this ordering above the table along with the year, catch basis, PPR method, units and applicable source references.

| Column | Content |
|---|---|
| Taxon name | Exact catch-data label; explain synonyms in Reason. |
| TL | Taxon trophic level used for the simple-chain PPR calculation; `?` if unavailable. |
| Catch (t) | Catch in the selected reference year and basis. Unknown catch remains `?`, not zero, and prevents an unqualified complete total. |
| Simple-chain PPR (t C) | Independent simple-chain PPR, or `?` if unavailable. Genuine calculated zero remains zero. |
| Mapped group names and weights | Exact model-group names and percentages, for example `Juvenile hairtail (80%); Adult hairtail (20%)`. Resolved weights sum to 100%, allowing rounding. Use `Juvenile hairtail (?); Adult hairtail (?)` for known candidates with unresolved weights; use `Unresolved` when no candidate is established. Identify tentative candidates as such. |
| Confidence level | High, Medium, Low or Unresolved under the combined rules. |
| Reason | Brief membership justification and, where required, weight justification, with source IDs and the consequential assumption. |

Example reason: `Membership explicit in source [1, Table X]; weights use source-model catch proportions [2], assumed constant across years (M1/W4).`

Put full source references beneath the appendix table, using the same short IDs as the summary and reasons. Include TL/simple-chain method sources as well as membership and weight evidence. Preserve useful hyperlinks. Put extended uncertainty discussion in the detailed supporting report.

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
- Verify identifiers, model/version consistency, source targets, count totals, category shares, weight sums, missing values, units and appendix-summary agreement. Preserve manual fields and user edits. Read-only verification or report arithmetic does not authorize a scientific rerun.
- Render the final document and inspect every page. Check table widths, repeating headers, readable figures, captions, page flow and the landscape appendix. Keep QA renders outside the delivered report files.
- Follow the user's current review gate. A request to draft or revise a template or skill ends with that artifact for review; it does not itself authorize a regional test run.
