"""Promote the faithful publication extraction and record constructor-only admission."""
from pathlib import Path
import csv, hashlib, json, math, os, shutil, sys, re
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
STAGE=RUN/'outputs/Aydin2007_Gulf_of_Alaska_1990-1994'
PAPER=ROOT/'regions/LME/LME_002/papers/GOA-2007'
MID='Aydin2007_Gulf_of_Alaska_1990-1994'
MODEL=PAPER/'models'/MID
TABLES=MODEL/'extracted_tables'
EV=TABLES/'evidence'
for p in (TABLES,EV):p.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def rel(p,base=ROOT):return os.path.relpath(p,base).replace('\\','/')
SOURCE=PAPER/'sources/noaa_22894_DS1-9dadd884.pdf'
source_sha=sha(SOURCE)
assert source_sha=='9dadd884031657e9a51741ef32a824083acf93a78c217a3a5b271fe83f3161d3'
candidate=next(STAGE.glob('2_*.json'))
data=json.loads(candidate.read_text(encoding='utf-8'))
assert len(data['group'])==133
fidelity=json.loads((STAGE/'SOURCE_FIDELITY_CHECK.json').read_text(encoding='utf-8'))
assert fidelity['numeric_value_and_missing_mask_match'] and not fidelity['errors']
if (MODEL/'model.json').exists():assert sha(MODEL/'model.json')==sha(candidate),'Existing differing canonical requires review'
shutil.copy2(candidate,MODEL/'model.json')
imports=['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx','Taxonomy.xlsx']
for name in imports:shutil.copy2(STAGE/name,TABLES/name)
shutil.copytree(STAGE/'companions',TABLES/'companions',dirs_exist_ok=True)
for name in ['SOURCE_FIDELITY_CHECK.json','MASS_BALANCE.md','DIET_SOURCE_SUMS.json']:
    shutil.copy2(STAGE/name,EV/name)
qa_names=['publication_tools.json','publication_assembly.json','source_review.json','preference_diets.json','numeric_extraction_audit.json','independent_numeric_review.json','native_recovery.json','publication_validate.log','publication_massbalance.log','publication_conversion.log','publication_writer.log']
for name in qa_names:
    p=RUN/'qa'/name
    if p.exists():shutil.copy2(p,EV/name)
output_names=['numeric_cell_evidence.json','numeric_cell_evidence.csv','canonical_groups.json','union_group_crosswalk.json','direct_diet_source_grids.json','direct_diet_cell_evidence.csv','direct_diet_issues.json','direct_diet_sums.json','source_taxonomy.csv']
for name in output_names:
    p=RUN/'outputs'/name
    if p.exists():shutil.copy2(p,EV/name)
CODE=EV/'extraction_code';CODE.mkdir(exist_ok=True)
for name in ['extract_numeric.py','assemble_publication.py','preference_records.py','build_publication.py',Path(__file__).name]:
    shutil.copy2(RUN/'code'/name,CODE/name)
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
before=sha(MODEL/'model.json')
loaded=ModelData(str(MODEL/'model.json'),model_name='Gulf of Alaska — published full model',model_year='1990-1994')
assert sha(MODEL/'model.json')==before
def number(v):
    if v in (None,'','-9999',-9999):return float('nan')
    return float(v)
def val(v):
    if isinstance(v,(float,np.floating)) and not math.isfinite(v):return None
    return v.item() if hasattr(v,'item') else v
def same(a,b):
    a,b=number(a),number(b)
    return (math.isnan(a) and math.isnan(b)) or (math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,rel_tol=1e-14,abs_tol=1e-12))
ledger=[];diet_checks=[];fate_checks=[]
mapping={k:k for k in ['biomass','pb','qb','ee','gs','ge','respiration','immigration','emigration','biomass_accum','tl']}
mapping['export']='catch'
for g in data['group']:
    seq=int(g['group_seq'])
    assert loaded.seq2name[seq]==g['group_name']
    for source_key,runtime_key in mapping.items():
        actual=loaded.groups_data.loc[seq,runtime_key]
        passed=same(g.get(source_key),actual)
        ledger.append({'group_seq':seq,'group_name':g['group_name'],'source_field':source_key,'source_literal':g.get(source_key),'loaded_field':runtime_key,'loaded_value':val(actual),'source_missing':math.isnan(number(g.get(source_key))),'loaded_missing':bool(np.isnan(actual)),'matches':passed,'transformation':'numeric coercion; explicit missing sentinel to NaN; export renamed catch' if source_key=='export' else 'numeric coercion; explicit missing sentinel to NaN'})
    actual=loaded.groups_data.loc[seq,'detritus_import']
    expected=number(g.get('detritus_import')) if g['pp']=='2' else 0.0
    ledger.append({'group_seq':seq,'group_name':g['group_name'],'source_field':'detritus_import','source_literal':g.get('detritus_import'),'loaded_field':'detritus_import','loaded_value':val(actual),'matches':same(expected,actual),'transformation':'source retained for DET; non-DET forced structural zero by loader'})
    import_seq=max(loaded.seq2name)
    actual=loaded.DC.loc[seq,import_seq]
    expected=number(g.get('diet_imp')) if g['pp']=='0' else 0.0
    ledger.append({'group_seq':seq,'group_name':g['group_name'],'source_field':'diet_imp','source_literal':g.get('diet_imp'),'loaded_field':'DC external-import column','loaded_value':val(actual),'matches':same(expected,actual),'transformation':'consumer unknown import remains NaN; nonfeeding import structurally zero'})
    for d in (g.get('diet_descr') or {}).get('diet',[]):
        prey=int(d['prey_seq']);actual=loaded.DC.loc[seq,prey]
        diet_checks.append({'predator_seq':seq,'prey_seq':prey,'source_literal':d['proportion'],'loaded_value':val(actual),'matches':same(d['proportion'],actual)})
    for pool,value in g.get('detritus_fate_by_pool',{}).items():
        try:pool_id=int(pool)
        except ValueError:pool_id=loaded.name2seq[pool]
        actual=loaded.det_fate.loc[seq,pool_id]
        fate_checks.append({'group_seq':seq,'pool_seq':pool_id,'source_literal':value,'loaded_value':val(actual),'matches':same(value,actual)})
def csvout(name,records):
    if not records:return
    with (EV/name).open('w',encoding='utf-8',newline='') as f:
        keys=list(dict.fromkeys(k for row in records for k in row));w=csv.DictWriter(f,keys);w.writeheader();w.writerows(records)
csvout('loader_parameter_ledger.csv',ledger)
csvout('loader_diet_ledger.csv',diet_checks)
csvout('loader_fate_ledger.csv',fate_checks)
loaded.groups_data.to_csv(EV/'loader_parameter_view.csv',index_label='group_seq')
loaded.DC.to_csv(EV/'loader_diet_view.csv',index_label='predator_seq')
loaded.det_fate.to_csv(EV/'loader_fate_view.csv',index_label='group_seq')
checks=ledger+diet_checks+fate_checks
admission={'constructor_admitted':True,'source_groups':133,'loaded_groups':len(loaded.groups_data),'synthetic_import_seq':max(loaded.seq2name),'canonical_sha256':before,'loader_path':'tools/scientific_code/PPREstimation/ModelData.py','loader_sha256':sha(ROOT/'tools/scientific_code/PPREstimation/ModelData.py'),'cell_checks':len(checks),'all_declared_transformations_match':all(x['matches'] for x in checks),'failed_checks':[x for x in checks if not x['matches']],'diet_nan_count':int(loaded.DC.isna().sum().sum()),'fate_nan_count':int(loaded.det_fate.isna().sum().sum()),'normalization_applied':False,'PPRCalculator_executed':False,'source_unchanged':sha(MODEL/'model.json')==before,'derived_fields':{'p':'B*PB','q':'B*QB','M0':'B*PB*(1-EE)','egestion':'B*QB*GS','net_migration':'emigration-immigration','predation':'production*EE-catch-BA-net_migration','flow_to_det':'egestion+M0'},'retained_only':'Fields not mapped in ledger (e.g. source pedigree, VBK, biomass_accum_rate, habitat metadata, raw taxon and companion evidence) remain in canonical JSON; constructor admission does not certify their scientific use. No loaded JSON replaces the canonical source. Source missingness is retained in explicit matrix entries; only structurally absent entries are zero-filled.','scope':'Schema admission and representation audit only; no diet normalization, parameter repair, diagnostics suite, SPPR or annual PPR.'}
dump(EV/'constructor_admission.json',admission)
assert admission['all_declared_transformations_match'],admission['failed_checks'][:8]
profile='''# Published Gulf of Alaska model profile

The annual base represents 1990–1994, with adjacent-period inputs where required; many mammal and bird estimates are from 1997–2002 (PDF p.13, printed p.3). Modeled area is 291,840 km², shelf and slope depths 50–1000 m, nine strata, excluding nearshore depths below 50 m (PDF pp.15–16, printed pp.5–6). No measured overlap ratio with LME_002 is available.

The published GOA parameter rows comprise 133 groups: 124 consumers, four producer/outside-production rows, and five detrital pools. This inventory retains the zero-biomass Mud skate and Black skate rows, explaining a difference from descriptions using 131 groups. Taxonomic guilds and species pools coexist with juvenile/adult divisions; generally juvenile groundfish are under 20 cm with species-specific ages in Appendix A. Pinniped stages use their own source definitions. Incoming and outmigrating salmon are separate unlinked groups; linked stanzas are not inferred.

Spatial strata weight the regional inputs; the extracted group values are whole-model-area densities. Biomass is t/km²; PB/QB are annual rates; landings, discards and BA are t/km²/year; diets are biomass fractions. The taxonomy workbook records source membership and locators, not an authority-resolved species or catch crosswalk.

Appendix C supplies biomass, rates, EE, TL, catches and direct fish/invertebrate diets. Tables C4–C10 retain source preference pools and juvenile/adult restrictions. Final pooled shares lacking the original availability denominator remain unknown. Table B8 bird category evidence and Table B9 dynamic split-pool parameters are retained in companions; neither is asserted to be the missing final static diet matrix.
'''
(TABLES/'MODEL_PROFILE.md').write_text(profile,encoding='utf-8')
notes='''# Aydin2007 Gulf of Alaska — full published extraction

## Source identity

Aydin, K., Gaichas, S., Ortiz, I., Kinzey, D. and Friday, N. (2007). *A comparison of the Bering Sea, Gulf of Alaska, and Aleutian Islands large marine ecosystems through food web modeling*. NOAA Technical Memorandum NMFS-AFSC-178. [NOAA source](https://repository.library.noaa.gov/view/noaa/22894). The original 309-page PDF is retained in ../../sources/. Main numerical evidence is Appendix C, with Appendix A and main-text/Appendix B rules.

## Modeled period and area

Annual base 1990–1994, using some adjacent-period observations; 291,840 km² covering the Gulf of Alaska shelf and slope at 50–1000 m. Nearshore waters shallower than 50 m are excluded. Geographic overlap with the complete LME_002 boundary has not been measured. See extracted_tables/MODEL_PROFILE.md for stage, guild, unit and spatial details.

## Extraction and departures

The canonical JSON contains 133 reported groups (including two zero-biomass skate rows), with all eight standard import files, 13 published evidence companions and source-derived taxonomy. Original numeric values, explicit zeros, trace literals and unknowns are retained. No diet normalization, fitted parameter adjustment, inferred zero BA, or reconstruction from the later aggregate has been applied.

The full published model cannot be reconstructed completely from the recovered report. Preference allocations among multiple eligible prey require unpublished availability denominators, and the bird tables do not specify all final group-level diets. Singleton eligible pools are resolved exactly; multi-member pools remain unknown. Four overlaps between direct amounts and unresolved pools remain unknown in the final matrix. Three BA values are explicit: adult pollock −1.35, herring −0.11, greenlings −0.002 t/km²/year; the other 130 BA cells are unknown. Adult-pollock detrital routing is not explicitly covered by the printed group-range rule and remains unknown.

Published Flathead sole and Southern rock sole diet columns total 105.46% and 106.93%; these were checked against rendered source pages and retained. The Large sculpins table allocates 3.09% to juvenile Yellowfin sole and juvenile Northern rock sole, which are absent from the GOA group inventory; the allocations are preserved as unresolved source evidence rather than reassigned to adults. Source preference-column rounding discrepancies and 0.00% trace cells are also preserved.

Validation reports 29 diet-sum errors and 20 warnings. The maintained conversion mass-balance check reports **NOT BALANCED: 14 errors, 190 indeterminate, 31 warnings, two notes**. These are properties of the incomplete published reconstruction, not proof that the original authors' executable model was unbalanced. Generic checker headings and inferred explanatory BA values are diagnostic messages, not extracted parameters. The source deficits have not been repaired.

Round-trip verification checked 116,222 cells across eight standard tables and 13 companions: numeric values and missing masks match (maximum difference 3.16×10⁻¹⁷); literal exact equality is false because of numeric representation. ModelData admits 133 real groups plus its synthetic diet-import row. Constructor admission is separate from scientific readiness; unknown matrix entries remain NaN and the model is not ready for a defensible PPR calculation.

The official 49-group Whitehouse–Aydin 2020 Rpath descendant is extracted as a separate candidate under GOA-2020. It is not a replacement source for this model's unresolved cells. Neither candidate is selected or researcher-approved. No SPPR or annual PPR was calculated, and no map rebuild was performed.

## Evidence links

- [Source cell and prose inventory](extracted_tables/evidence/source_review.json)
- [Round-trip verification](extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json)
- [Constructor and transformation audit](extracted_tables/evidence/constructor_admission.json)
- [Published mass-balance check](extracted_tables/evidence/MASS_BALANCE.md)
- [Portable evidence index](extracted_tables/evidence/evidence_index.json)
- [Completeness assessment](extracted_tables/evidence/completeness.json)

The handoff is complete as a source-faithful partial extraction; the full numerical reconstruction remains incomplete. Model selection, taxonomy authority resolution, catch matching, diagnostics and annual readiness remain separate stages.
'''
validation=(EV/'publication_validate.log').read_text(encoding='utf-8')
counts=re.search(r'(\d+) error\(s\), (\d+) warning\(s\)',validation)
assert counts,validation[-500:]
notes=notes.replace('29 diet-sum errors and 20 warnings',f'{counts[1]} diet-sum errors and {counts[2]} warnings')
balance=(EV/'MASS_BALANCE.md').read_text(encoding='utf-8')
counts=re.search(r'(\d+) error\(s\), (\d+) indeterminate, (\d+) warning\(s\), (\d+) note\(s\)',balance)
assert counts,balance[:500]
notes=notes.replace('14 errors, 190 indeterminate, 31 warnings, two notes',f'{counts[1]} errors, {counts[2]} indeterminate, {counts[3]} warnings, {counts[4]} notes')
(MODEL/'model_notes.md').write_text(notes,encoding='utf-8')
(EV/'REPORT.md').write_text(notes.replace('# Aydin2007 Gulf of Alaska — full published extraction','# Extraction QA report: Aydin2007 Gulf of Alaska').replace('(extracted_tables/evidence/','('),encoding='utf-8')
manifest_path=PAPER/'source_manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['administrative_only']=False
manifest['models']=[MID]
manifest['model_extraction']={'model_id':MID,'model_path':rel(MODEL/'model.json',PAPER),'period':'1990-1994','groups':133,'model_area_km2':291840,'source_role':'published_model_parameter_source','extraction_status':'partial_final_diet_unresolved','model_sha256':before}
manifest['extraction_note']='Latest extraction preserves the published parameter rows and missingness; no measured LME overlap ratio, no selection, no PPR, map refresh deferred by user.'
dump(manifest_path,manifest)
files=list(dict.fromkeys([MODEL/'model.json',MODEL/'model_notes.md',SOURCE]+sorted(TABLES.rglob('*'))))
artifacts=[]
for p in files:
    if not p.is_file() or p.name in ['evidence_index.json','completeness.json']:continue
    role='source_pdf' if p==SOURCE else 'canonical_model' if p==MODEL/'model.json' else 'model_notes' if p==MODEL/'model_notes.md' else 'extraction_evidence' if EV in p.parents else 'extracted_table'
    artifacts.append({'role':role,'availability':'present','path':rel(p,EV),'sha256':sha(p)})
artifacts.append({'role':'complete_final_diet','availability':'missing','reason':'Published preference pools and seabird categories do not provide all final group-level allocations; two source juvenile prey are outside the GOA inventory. Official aggregate is a separate model.','acquisition_status':'Primary report, official repositories and author archives searched; no matching full native parameter set recovered.'})
index={'schema_version':1,'run_id':RUN.name,'region_id':'LME_002','model_id':MID,'variant_id':'published_full_source_faithful','source_identity':{'citation':'Aydin et al. 2007 NOAA AFSC-178','pdf_sha256':source_sha},'computational_input_identity':{'path':'../../model.json','sha256':before,'status':'not_calculated'},'methods':[],'required_roles':['source_pdf','canonical_model','model_notes','extracted_table','extraction_evidence','complete_final_diet'],'artifacts':artifacts,'reconciliation':{'source_numeric_roundtrip_and_masks':True,'constructor_declared_transformations':True},'scientific_status':'partial extraction; complete final diet unavailable; no selection or PPR'}
dump(EV/'evidence_index.json',index)
sys.path.insert(0,str(ROOT/'tools/skills/paper-to-ppr/scripts'))
from check_evidence import check
completeness=check(EV/'evidence_index.json');dump(EV/'completeness.json',completeness)
assert completeness['errors']==[] and completeness['missing_roles']==['complete_final_diet']
print(json.dumps({'canonical_path':rel(MODEL/'model.json'),'sha256':before,'constructor_checks':len(checks),'constructor_matches':admission['all_declared_transformations_match'],'inventory_integrity_errors':completeness['errors'],'scientific_missing_roles':completeness['missing_roles'],'diet_unknown_cells':admission['diet_nan_count'],'fate_unknown_cells':admission['fate_nan_count']},indent=2))
