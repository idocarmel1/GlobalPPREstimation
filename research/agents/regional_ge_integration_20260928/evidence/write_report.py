from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
r=json.loads((HERE/'FINAL_INTEGRATION_VERIFICATION.json').read_text(encoding='utf-8'))
g=json.loads((HERE/'generated_regions_verification.json').read_text(encoding='utf-8'))
selected=r['selected_regions'];numeric=[x for x in selected if x['ge_ppr_tC_2019'] is not None]
lines=['# Regional provisional PPR integration','',
f"Reviewed {r['regional_count']} regions: {len(selected)} have selected models. Updated {len(r['updated_regions'])} regional workbooks; {r['unselected_preserved']} unselected regions were preserved. {len(numeric)} selected regions have numerical 2019 GE PPR. Existing model selections and rationales were preserved.",'',
'The user explicitly requested numeric SPPR, taxon-to-group mappings and PPR display before later model validation. New results use explicit provisional statuses. Diagnostic FAIL/WARN, strict balance failures and unresolved source or regional applicability remain visible. Numerical output is not an assertion that the model is scientifically valid. Negative contributions from failed methods are retained rather than silently discarded. Provisional outputs are excluded from validated common-catch comparisons.','',
'## Updated regions','',
'2019, GE, all sources, total catch (landings plus discards), existing method treatment of unidentified taxa. PPR is in tonnes carbon; source wet-mass PPR is divided by 9 exactly once.','',
'| Region | Selected model | PPR (tC) | Catch coverage | Mapped catch labels |','|---|---|---:|---:|---:|']
for x in selected:
    if x['updated']:lines.append(f"| {x['unit_id']} — {x['name']} | {x['model_id']} | {x['ge_ppr_tC_2019']:,.2f} | {x['coverage_pct']:.4f}% | {x['mapped_taxa']} |")
lines+=['','Catch coverage = catch tonnage with a usable mapped coefficient / total catch tonnage for the same region, year and catch basis. It is not the fraction of species, model area, or scientific validity. For HS_077: 415,664.8921 / 860,671.2076 × 100 = 48.2954%. The supported labels are skipjack, albacore, Pacific bluefin and Carangidae.','',
'Unsupported size splits remain unresolved. Mesh and gear selectivity do not justify a blanket adult-only allocation. See [size-allocation research](SIZE_ALLOCATION_RESEARCH.md) for online evidence, the HS_077 size thresholds and a proposed mass-weighted allocation approach.','',
'## Diagnosis and applicability flags','']
for x in selected:
    if not x['updated']:continue
    lines += [f"### {x['unit_id']}",'',x['source_note'] or x['ge_status'],'']
    lines += ['- '+flag for flag in x['review_flags'] if not flag.startswith('new_')]
    lines.append('')
lines+=['## Remaining unavailable','']
for x in selected:
    if x['ge_ppr_tC_2019'] is None:lines.append(f"- {x['unit_id']}: {x['ge_status']}. Selection retained; no numerical PPR invented.")
lines+=['','## Verification','',
'- 37 workflow tests passed, including signed provisional results, warning retention, missing-data gates, method-specific diagnostic schema and exports.',
'- All updated regional workbooks passed input/result freshness checks. Separate regional evidence retains exact runtime reproduction, matching reviews and independent annual arithmetic.',
'- Central paper/model metadata, unrelated regional records, selected IDs and rationales were preserved. Updated regional annual tables match the combined workbook.',
f"- Generated map and trend evaluators independently match all {len(g['checked'])} updated regions’ 2019 GE values and coverage, with one carbon conversion and visible provisional/diagnostic metadata.",
'- Full generated-page annual/NPP and fingerprint verification is recorded in html_verification.txt. Browser inspection is recorded separately in browser_verification.json.',
'- Representative regional workbook Overview rendering: LME022_overview.png. Original workbook backups and complete per-region evidence are retained.','',
'## Evidence','',
'- FINAL_INTEGRATION_VERIFICATION.json: central preservation, selected-region inventory, hashes and flags.',
'- generated_regions_verification.json: generated map/trend calculations.',
'- health_schema_verification.json: metadata-only diagnostic normalization.',
'- Other regions: other_regions_audit.md / .json; each changed LME has models/.../integration_20260928 or models/regional_ge_integration_20260928.',
'- HS_077 and WCPO: regional evidence folders; HS_077 PROVISIONAL_INTEGRATION.md supersedes earlier withholding notes while retaining their original audit findings.',
'- LME_022: models/regional_ge_integration_20260928/INTEGRATION_REPORT.md.',
'',f"Final Project.xlsx SHA-256: `{r['project_sha256']}`",'']
(HERE/'INTEGRATION_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
print(f"Report written: {len(numeric)}/{len(selected)} selected regions have 2019 numeric GE, {len(r['updated_regions'])} newly updated.")
