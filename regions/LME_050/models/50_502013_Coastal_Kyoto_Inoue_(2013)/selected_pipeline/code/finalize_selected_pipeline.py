from pathlib import Path
import json,hashlib,shutil
import pandas as pd
D=Path(__file__).resolve().parent;M=D.parent;MID='50_502013_Coastal_Kyoto_Inoue_(2013)';EV=M/MID/'selected_pipeline'
summary=json.loads((EV/'PIPELINE_SUMMARY.json').read_text());validation=json.loads((EV/'VALIDATION.json').read_text());assert validation['status']=='PASS'
p=json.loads((D/'CENTRAL_REGISTRATION_PROPOSAL.json').read_text(encoding='utf8'))
p['status']='queued_for_parent_serialized_registration_no_central_write_performed'
p['paper_fields_to_update']['selected']=True
p['paper_fields_to_update']['notes']='USER-PREFERRED/SPECIFIED SOURCE: only available paper. USER SELECTED 2013 because it is newer; 1985 is also a good model for comparison. Selection does not imply numerical superiority. Both original year-specific diet networks remain unverified. Direct GE, TE, With Egestion statuses WARN. Exact/synonym mapping19/253taxa;2019totalcatch support25.0500%; annual values are covered-catch subtotals, not complete LME estimates; production_eligible=False. See regions/LME_050/models/extraction_review_20260928/SELECTED_PIPELINE_REPORT.md.'
p['paper_fields_to_update']['recommendation']='User selected 2013 for recency; retain1985as good comparison. Coastal Kyoto applicability and incomplete whole-LME group coverage remain explicit.'
p['paper_fields_to_update']['documentation_evidence']='regions/LME_050/models/extraction_review_20260928/SELECTED_PIPELINE_REPORT.md; regions/LME_050/models/extraction_review_20260928/SPPR_DIAGNOSTICS_REPORT.md'
for r in p['models_to_append']:
 selected=r['model_id']==MID;r['selected']=selected
 r['selection_rationale']='User selected2013because it is newer;1985also a good model for comparison. No claim2013is numerically superior.' if selected else 'User explicitly retains1985as a good comparison model;2013selectedbecause newer.'
 r['availability']='Extracted canonical source; original year-specific diets unresolved; direct GE/TE/With Egestion all WARN. '+('Selected, supported-catch pipeline validated;19/253taxa,25.0500%2019totalcatch support; production eligibility false.' if selected else 'Retained good comparison candidate; no production adoption.')
p['production_model_selection']={'selected_model_id':MID,'reason':'2013 is newer','good_comparison_model':'50_501985_Coastal_Kyoto_Inoue_(1985)','regional_sha256':validation['regional_sha256'],'production_eligible':False,'whole_region_PPR':'Pending additional group-membership/proxy evidence; current numerical values are covered-catch subtotals'}
p['preserve']=['all existing scores','history region_rank (27 for paper)','atlas_region_rank (18 at last read; updater owns current rank)','all other region preferences/records','all13nativeExcel tables/filter controls','existingmodelrowsby(unit_id,model_id);appendonlyifabsent','paper key SOJ-2023__LME_050;update rather than duplicate','prior paper metadata in retained before-review evidence']
(D/'SELECTED_CENTRAL_REGISTRATION_PROPOSAL.json').write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf8')
a=pd.read_csv(EV/'supported_catch_annual_ppr.csv');r=pd.read_csv(EV/'supported_catch_ppr_npp_ratios.csv')
rows=[]
for method,label in [('new_GE','GE'),('new_TE_EEfix','TE'),('new_WithEgestion','With Egestion')]:
 val=float(a[(a.method==method)&(a.scope=='all')&(a.catch_basis=='catch')&(a.unidentified=='method')&(a.metric=='ppr')]['2019'].iloc[0]);ratio=float(r[(r.method==method)&(r.scope=='all')&(r.catch_basis=='catch')&(r.unidentified=='method')&(r.npp_method=='ens_median_tC_yr')]['2019'].iloc[0]);rows.append(f'| {label} | WARN | {val:,.2f} | {val/9:,.2f} | {ratio:.4f}% |')
report='''# Selected 2013 model: regional pipeline report

**Selection saved:** `50_502013_Coastal_Kyoto_Inoue_(2013)`, because the user prefers the newer model. **1985 remains a good comparison model.** This is not a finding that 2013 is numerically superior.

The regional Overview records the exact selection and rationale. Previous results were archived before `prepare_selection`; the original source models, comparison reports and evidence remain intact. The independently verified [GE group comparison](ge_year_comparison/GE_SPPR_GROUP_COMPARISON.md) is complete.

## Completed and verified

- Three bounded direct `diagnose_sppr()` calls: GE, TE, With Egestion only, with full returns. Each exactly reproduces its previous audited return; all remain WARN, with nonnegative finite source coefficients and convergent calculations. No global option, Monte Carlo or broad method suite was run.
- The loaded groups, diet and detritus fate match the original audit exactly. Canonical2013SHA256 remains `a3b008c0add95db106f9e10cf90907cc7f1f9d2ab1425cbf615745142e27330e`.
- Regional Selected model groups now contains all40sourcegroups plus diet import, with369coefficients covering3methods×3scopes×41groups.
-19of253catchtaxa have exact TableS3 membership or verified synonym evidence. All234remaining taxa retain explicit unresolved rows. Source and mapping spellings were not silently repaired; no invented proxy groups or coarse weights were used.
- Supported-catch annual PPR and available PPR/NPP ratios were calculated through the current regional calculation contract. Catch, NPP and Classic PPR taxon inputs are unchanged. Prior annual/sensitivity results remain in the archived workbook; current calculation invalidates old sensitivity bounds as required.

## Coverage is the remaining scientific limit

|2019basis|Confirmed mapped tonnes|All recorded tonnes|Coverage|
|---|---:|---:|---:|
|Total catch|648,029.94|2,586,941.84|25.0500%|
|Landings|640,137.59|2,258,481.01|28.3437%|
|Discards|7,892.36|328,460.82|2.4028%|

The source is coastal Kyoto, not the whole Sea of Japan. It supplies no supported pollock, cod, saury or Pacific herring group. Major unresolved2019catches include Alaska pollock494,220.49t, unidentified marine fish315,222.27t, Pacific herring109,934.89t, Scomber106,955.52t, Pectinidae86,406.07t and Pacific cod80,661.51t. Some coarse taxa may become resolvable with better group definitions; others lie outside the source model. Neither case justifies an invented mapping.

**Complete regional model PPR remains pending additional membership or explicitly reviewed proxy evidence. Production eligibility remains false.** Current annual values are confirmed mapped-catch subtotals, not full-LME totals; unresolved taxa are not assumed to require zero production. The standard zero/simple unidentified-treatment views remain separate from the method-treatment coverage shown here.

## Supported2019catch subtotal, all-source coefficients

These values apply2013coefficients to the19supported taxon series. They are separate from the paper's own modeled-area catch footprint. Carbon conversion divides wet-weight equivalent production by9once. The ratio denominator is existing regional ensemble-median NPP, while the numerator remains a partial catch subtotal.

|Method|Direct diagnostic|PPR wet-weight tonnes|PPR tonnes carbon|Subset PPR / existing regional NPP|
|---|---|---:|---:|---:|
'''+ '\n'.join(rows)+'''

## Caveats preserved

The paper describes different diets between1985and2013 but supplies only one complete matrix. Source admission is still unresolved. Loader diet normalization, missingGS/catch/migration/routing defaults and solved biomass accumulation are unchanged and remain separately audited. Numerical balance does not establish recovery of the original year-specific source model. The WARN statuses include EE=0 consequences; selection does not erase them.

The three synonym links were independently retrieved from the WoRMS API and retained with hashes: [Sardinops melanostictus → Sardinops sagax](https://www.marinespecies.org/rest/AphiaRecordByAphiaID/309913), [Crassostrea gigas → Magallana gigas](https://www.marinespecies.org/rest/AphiaRecordByAphiaID/140656), and [Dasyatis akajei → Hemitrygon akajei](https://www.marinespecies.org/rest/AphiaRecordsByName/Dasyatis%20akajei?like=false&marine_only=true). These resolve taxonomy; they do not establish whole-LME spatial representativeness.

## Validation and handoff

Independent checks passed for3780annual mapped-subset cells and7056supported ratio cells.26964unsupported ratio cells remain blank. Catch=landings+discards holds within7.5×10⁻¹⁰t. The current regional engine rounds taxon coefficients to6decimals; the largest resulting annual difference from unrounded group coefficients is0.22871wet-weight tonnes, retained in the audit. Regional selection/input/result fingerprints validate.

Evidence and full-precision outputs are under `../50_502013_Coastal_Kyoto_Inoue_(2013)/selected_pipeline/`: `VALIDATION.json`, `MAPPING_REVIEW.json`, all direct returns, source coefficients, membership/coverage tables, annual subtotals, ratios, code snapshots and provenance. Regional workbookSHA256: `'''+validation['regional_sha256']+'''`.

Central registration is queued in [SELECTED_CENTRAL_REGISTRATION_PROPOSAL.json](SELECTED_CENTRAL_REGISTRATION_PROPOSAL.json). The proposal updates the existing paper record, appends the two absent local models, derives the2013selection from Overview, retains1985comparison status, and preserves scores/ranks/other regions. No central workbook or map writes were performed by this selected-model run.
'''
# Keep user-facing prose legible even in compact numeric lists.
import re
report=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',report)
# Do not alter IDs, hashes, URLs, or filenames through prose spacing: undo within code/links.
report=report.replace('canonical2013','canonical 2013') if False else report
# Restore exact technical tokens after the readability pass.
for token in [MID,'a3b008c0add95db106f9e10cf90907cc7f1f9d2ab1425cbf615745142e27330e',validation['regional_sha256'],'../'+MID+'/selected_pipeline/']:
 spaced=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',token);report=report.replace(spaced,token)
report=report.replace('Table S 3','Table S3').replace('Wo RMS','WoRMS')
for a,z in [('-19','- 19'),('TableS 3','Table S3'),('sourcegroups','source groups'),('catchtaxa','catch taxa'),('regional workbookSHA','regional workbook SHA'),('%20 akajei','%20akajei'),('SHA 256','SHA256')]:report=report.replace(a,z)
(D/'SELECTED_PIPELINE_REPORT.md').write_text(report,encoding='utf8')
shutil.copy2(__file__,EV/'code'/Path(__file__).name)
hashes={x.relative_to(EV).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in EV.rglob('*') if x.is_file() and x.name!='DELIVERABLE_HASHES.json'}
(EV/'DELIVERABLE_HASHES.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
print('Selected pipeline report complete; central proposal queued; validation PASS.')
