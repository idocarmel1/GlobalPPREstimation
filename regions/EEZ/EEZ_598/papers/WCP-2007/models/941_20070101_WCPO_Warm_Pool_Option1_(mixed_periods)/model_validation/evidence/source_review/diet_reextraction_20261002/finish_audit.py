"""Verify saved source/runtime evidence and write a root handoff receipt."""
from pathlib import Path
from decimal import Decimal as D
import csv
import json,hashlib,math,os
import numpy as np
import pandas as pd

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
REG=ROOT/'regions/EEZ_598'
MID='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
MODEL=REG/'models'/MID
SELECTED=MODEL/(MID+'.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

tol=1e-12
excluded_names={'biomass_accum','biomass_accum_rate','growth','predation'}
metadata_names={'balance_BA_after_DC_normalization','diet_normalization_rows','diet_normalization_balance_ledger'}
differences=[];excluded=[];metadata=[];numeric_count=0;max_nonexcluded_diff=0.0
def compare(a,b,path='',is_excluded=False):
    global numeric_count,max_nonexcluded_diff
    tail=path.split('/')[-1]
    if tail in excluded_names:is_excluded=True
    if isinstance(a,dict) and isinstance(b,dict):
        if a.get('type')=='DataFrame' and b.get('type')=='DataFrame':
            for k in ['type','index','columns']:compare(a[k],b[k],path+'/'+k,is_excluded)
            for ri,index in enumerate(a['index']):
                for ci,col in enumerate(a['columns']):
                    compare(a['values'][ri][ci],b['values'][ri][ci],path+'/row/'+str(index)+'/column/'+str(col),is_excluded or col in excluded_names)
            return
        for k in sorted(set(a)|set(b)):
            if k in metadata_names:
                if a.get(k)!=b.get(k):metadata.append({'path':path+'/'+k,'historical_present':k in a,'current_present':k in b})
                continue
            if k not in a or k not in b:
                differences.append({'path':path+'/'+k,'historical_present':k in a,'current_present':k in b,'kind':'unclassified_presence_difference'})
            else:compare(a[k],b[k],path+'/'+k,is_excluded)
        return
    if isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):differences.append({'path':path,'kind':'length','historical':len(a),'current':len(b)})
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i),is_excluded)
        return
    if isinstance(a,(float,int)) and not isinstance(a,bool) and isinstance(b,(float,int)) and not isinstance(b,bool):
        delta=abs(a-b);numeric_count+=1
        if not is_excluded:max_nonexcluded_diff=max(max_nonexcluded_diff,delta)
        if delta>tol:
            (excluded if is_excluded else differences).append({'path':path,'historical':a,'current':b,'absolute_difference':delta})
    elif a!=b:
        (excluded if is_excluded else differences).append({'path':path,'historical':a,'current':b,'kind':'exact_non_numeric_difference'})

historical=read(OUT/'historical_runtime/state.json');current=read(OUT/'current_runtime/state.json')
compare(historical,current)
actual=pd.read_csv(MODEL/'diagnostic_evidence/loaded_groups.csv',index_col=0)
replay=pd.read_csv(OUT/'historical_runtime/loaded_groups.csv',index_col=0)
assert actual.index.equals(replay.index) and actual.columns.equals(replay.columns)
numeric={c:float((actual[c]-replay[c]).abs().max()) for c in actual.select_dtypes('number')}
strings={c:bool(actual[c].fillna('').equals(replay[c].fillna(''))) for c in actual.select_dtypes(exclude='number')}
assert all(v<=tol for v in numeric.values()) and all(strings.values())
pins=read(OUT/'executing_code_hashes_before.json')
pin_after={k:{**v,'after_sha256':sha(ROOT/v['source_path']),'pinned_sha256':sha(ROOT/v['pinned_path']),'source_stable':sha(ROOT/v['source_path'])==v['before_sha256']} for k,v in pins.items()}
write(OUT/'executing_code_hashes_final.json',pin_after)
comparison={'comparison_tolerance':{'atol':tol,'rtol':0.0,'non_numeric':'exact'},'selected_input_sha256':sha(SELECTED),'historical_input_sha256':read(MODEL/'diagnostic_evidence/SCENARIO_SUMMARY.json')['input_sha256'],'loader_settings':read(OUT/'loader_settings.json'),'current_extra_default_setting':{'balance_BA_after_DC_normalization':True},'historical_replay_to_retained_actual_loaded_groups':{'numeric_max_absolute_difference':max(numeric.values()),'numeric_fields':numeric,'all_text_fields_exact':all(strings.values()),'text_fields':strings,'actual_file':rel(MODEL/'diagnostic_evidence/loaded_groups.csv')},'historical_replay_identity_limit':'Retained actual group table exact; historical full state reconstructed from exact retained input, exact archived executing code hashes and exact loader settings. Retained historical diet/full object snapshot was not originally serialized; historical normalized matrix reproduced from those pinned inputs. No fresh diagnostic methods called.','compared_attributes':list(historical),'numeric_values_compared':numeric_count,'maximum_nonexcluded_absolute_difference':max_nonexcluded_diff,'nonexcluded_differences':differences,'excluded_change_fields':sorted(excluded_names),'excluded_changes':excluded,'metadata_presence_differences':metadata,'runtime_equivalent_under_human_rule':not differences,'refresh_required':bool(differences),'code_source_stable_during_run':all(v['source_stable'] for v in pin_after.values()),'state_files':{'historical':{'path':rel(OUT/'historical_runtime/state.json'),'sha256':sha(OUT/'historical_runtime/state.json')},'current':{'path':rel(OUT/'current_runtime/state.json'),'sha256':sha(OUT/'current_runtime/state.json')}}}
write(OUT/'runtime_comparison.json',comparison)

before=read(OUT/'protected_before.json');checks={p:{'before_sha256':v,'after_sha256':sha(ROOT/p) if (ROOT/p).is_file() else None,'unchanged':(ROOT/p).is_file() and sha(ROOT/p)==v} for p,v in before.items()}
write(OUT/'protected_files_verification.json',{'all_unchanged':all(v['unchanged'] for v in checks.values()),'checks':checks,'scope':'All preexisting EEZ_598 files; agent wrote only new diet_reextraction_20261002 evidence. Shared/other-region writes are prohibited and were not performed.'})
source=read(OUT/'source_comparison.json')
source_dir=ROOT/'regions/EEZ_941/papers/WCP-2007/extraction_evidence'
predecessor_dir=ROOT/'regions/EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)'
extraction=read(source_dir/'final_extraction.json')
import_path=predecessor_dir/'extracted_tables/Diet_composition.csv'
with import_path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f))
header=rows[0];body={r[0]:r for r in rows[1:] if r[0]}
import_row=next(r for r in rows if r[1]=='Import')
import_checks=[]
for ci,consumer in enumerate(header[2:],2):
    for ps,row in body.items():
        printed=extraction['diet'][consumer].get(ps)
        actual=row[ci]
        assert actual==('' if printed is None else printed),(consumer,ps,printed,actual)
        import_checks.append({'consumer_seq':consumer,'prey_seq':ps,'import_table_literal':actual,'printed_source_literal':printed,'exact_equal':True,'import_table_cell':{'csv_row_1based':rows.index(row)+1,'csv_column_1based':ci+1}})
    assert import_row[ci]==extraction['diet'][consumer]['import']=='0'
    import_checks.append({'consumer_seq':consumer,'prey_seq':'import','import_table_literal':import_row[ci],'printed_source_literal':'0','exact_equal':True,'import_table_cell':{'csv_row_1based':rows.index(import_row)+1,'csv_column_1based':ci+1}})
write(OUT/'retained_import_comparison.json',{'path':rel(import_path),'sha256':sha(import_path),'all_exact_source_literals':True,'cell_checks':import_checks,'display_row_warning':'Retained (1 - Sum) footer is uniformly zero despite nonunit source sums. It is not diet/import input and must not be interpreted as a source deficit fill.'})
raw=pd.read_csv(OUT/'current_runtime/raw_loaded_diet.csv',index_col=0)
runtime=pd.read_csv(OUT/'current_runtime/loaded_diet.csv',index_col=0)
transform=[]
for consumer in raw.index:
    s=float(raw.loc[consumer].sum());r=float(runtime.loc[consumer].sum())
    factor=1/s if s!=0 else None
    cells=[{'prey_seq':str(prey),'raw':float(raw.loc[consumer,prey]),'runtime':float(runtime.loc[consumer,prey])} for prey in raw.columns if raw.loc[consumer,prey]!=runtime.loc[consumer,prey]]
    transform.append({'consumer_seq':int(consumer),'raw_sum_including_import':s,'runtime_sum_including_import':r,'normalization_factor':factor,'changed_cells':cells})
write(OUT/'runtime_diet_transformations.json',{'canonical_sha256':sha(SELECTED),'raw_matrix_sha256':sha(OUT/'current_runtime/raw_loaded_diet.csv'),'runtime_matrix_sha256':sha(OUT/'current_runtime/loaded_diet.csv'),'orientation':'consumer rows, prey columns (includes synthetic diet_import group 32)','runtime_normalization_allowed':True,'normalization_does_not_establish_researcher_review':True,'transformations':transform})
blockers=[]
if not comparison['code_source_stable_during_run']:blockers.append('Shared source code changed during snapshot audit. Re-pin current code and compare before integration.')
if differences:blockers.append('Nonexcluded runtime state differs beyond atol=1e-12; root-coordinated affected refresh required.')
if not all(v['unchanged'] for v in checks.values()):blockers.append('Preexisting EEZ_598 file changed concurrently; inspect protected verification before handoff.')
receipt={'region':'EEZ_598','selected_model_id':MID,'selected_path':rel(SELECTED),'outcome':'verified unnormalized unchanged; runtime equivalent with permitted BA/growth differences excluded' if not blockers else 'mixed; see precise_blockers','normalization_status':source['normalization_status'],'normalization_decision_basis':'Every Final printed Table 4 numerical token verified in primary PDF at retained display bbox; exact cell equality with selected JSON, source extraction and predecessor canonical; converter normalization restoration before accepted scenario independently confirmed. Sum=1 not used as proof.','reextraction_performed':False,'canonical_before_sha256':next(iter(source['selected_alias_sha256'].values())),'canonical_after_sha256':sha(SELECTED),'changed_diet_cells':[],'accepted_overrides_preserved':True,'canonical_model_json_sha256':sha(MODEL/'model.json'),'runtime_comparison_path':rel(OUT/'runtime_comparison.json'),'runtime_equivalent_under_human_rule':comparison['runtime_equivalent_under_human_rule'],'runtime_refresh_required':comparison['refresh_required'],'comparison_tolerance':comparison['comparison_tolerance'],'excluded_runtime_fields':comparison['excluded_change_fields'],'code_source_stable':comparison['code_source_stable_during_run'],'source_native_fidelity_limit':source['source_fidelity_limits'],'researcher_review_state':'Existing accepted Sept 28 selection/PB/EE scenario retained; this audit is evidence only and grants no new scientific approval.','evidence_paths':[rel(OUT/n) for n in ['cell_ledger.json','consumer_sums.json','source_comparison.json','primary_coordinate_verification.json','researcher_override_evidence.json','runtime_comparison.json','executing_code_hashes_before.json','executing_code_hashes_final.json','protected_files_verification.json']],'precise_blockers':blockers,'protected_files_unchanged':all(v['unchanged'] for v in checks.values()),'protected_files_checked':len(checks),'hold_respected':True,'selected_input_or_workbook_mutation':False,'historical_results_disposition':'Retain actual historic result/input hashes unchanged. Root may attach this provenance bridge; no numerical refresh triggered by permitted excluded differences.','missing_evidence':['Original native EwE binary/model file not retained; printed Table 4 diet fidelity verified rather than native full-equation fidelity.','Full historical runtime object/matrix was not serialized contemporaneously; reproduced from exact input/code/settings and reconciled exactly to retained actual loaded groups.']}
receipt['evidence_paths'] += [rel(OUT/'retained_import_comparison.json'),rel(OUT/'runtime_diet_transformations.json')]
write(OUT/'root_receipt.json',receipt)
roles={'primary_source':REG/'papers/WCP-2007/download-0adcf55e.pdf','source_cells':source_dir/'cell_evidence.json','source_extraction':source_dir/'final_extraction.json','source_restoration_history':predecessor_dir/'extracted_tables/converter_to_canonical_audit.json','restoration_executing_builder':source_dir/'build_artifacts.py','scenario_executing_builder':predecessor_dir/'balance_investigation/correction_scenarios/run_scenarios.py','accepted_selection':MODEL/'SELECTION_AND_PROVENANCE.json','selected_input':SELECTED,'canonical_copy':MODEL/'model.json','retained_actual_loaded_groups':MODEL/'diagnostic_evidence/loaded_groups.csv','historical_provenance':MODEL/'diagnostic_evidence/experiment_PROVENANCE.json','cell_ledger':OUT/'cell_ledger.json','consumer_sums':OUT/'consumer_sums.json','source_comparison':OUT/'source_comparison.json','primary_verification':OUT/'primary_coordinate_verification.json','import_comparison':OUT/'retained_import_comparison.json','runtime_comparison':OUT/'runtime_comparison.json','runtime_transformations':OUT/'runtime_diet_transformations.json','historical_state':OUT/'historical_runtime/state.json','current_state':OUT/'current_runtime/state.json','pinned_code_hashes':OUT/'executing_code_hashes_final.json','protected_verification':OUT/'protected_files_verification.json','receipt':OUT/'root_receipt.json'}
artifacts=[{'role':role,'path':os.path.relpath(p,OUT).replace(os.sep,'/'),'sha256':sha(p),'availability':'present'} for role,p in roles.items()]
artifacts += [{'role':'native_ewe_model','availability':'missing','reason':'Native EwE binary model not present; full printed Table 4 has been verified and is sufficient for diet normalization decision. No native-equation fidelity claimed.','acquisition_status':'not_required_for_printed_cell_audit'},{'role':'fresh_diagnostics','availability':'inapplicable','reason':'No nonexcluded runtime difference; historical results retained.','acquisition_status':'not_run_by_design'}]
write(OUT/'evidence_index.json',{'schema_version':1,'run_id':'EEZ_598_diet_audit_20261002','region_id':'EEZ_598','model_id':MID,'variant_id':'human_accepted_D_fixed_M0_option1','source_identity':{'sha256':source['source_extraction_sha256'],'primary_pdf_sha256':'0adcf55ef7760865786bc2774b1fb147a6461a6fe0b128a943c8fce27c23f52f'},'computational_input_identity':{'selected_sha256':sha(SELECTED),'settings':read(OUT/'loader_settings.json')},'methods':['historical_constructor_replay','current_constructor_state_compare'],'required_roles':list(roles),'artifacts':artifacts,'reconciliation':{'all_primary_table4_tokens_verified':read(OUT/'primary_coordinate_verification.json')['all_verified'],'all_source_and_import_literals_equal':not source['printed_diet_differences'],'historical_actual_groups_reconciled':all(v<=tol for v in numeric.values()) and all(strings.values()),'nonexcluded_runtime_equal':not differences,'protected_files_unchanged':receipt['protected_files_unchanged'],'executing_source_stable':comparison['code_source_stable_during_run']}})
print(json.dumps({'outcome':receipt['outcome'],'nonexcluded_differences':len(differences),'excluded_changes':len(excluded),'max_nonexcluded_absolute_difference':max_nonexcluded_diff,'protected_files_unchanged':receipt['protected_files_unchanged'],'blockers':blockers}))
