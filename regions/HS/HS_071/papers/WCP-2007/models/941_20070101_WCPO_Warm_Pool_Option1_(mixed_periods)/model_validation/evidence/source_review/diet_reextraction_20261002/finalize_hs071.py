from pathlib import Path
import json,hashlib,math,os
root=Path.cwd();reg=root/'regions/HS_071';out=reg/'diet_reextraction_20261002';mid='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)';hist=reg/'validation_reports'/mid/'reused_diagnostics'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
write=lambda n,x:(out/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
r=read(out/'retained_loaded_state.json')
def frame_compare(a,b):
    changes=[];maximum=0;numeric=0
    axes=a['index']==b['index'] and a['columns']==b['columns']
    if axes:
        for i,row in enumerate(a['index']):
            for j,col in enumerate(a['columns']):
                x,y=a['data'][i][j],b['data'][i][j]
                if isinstance(y,dict) and 'nonfinite' in y and y['nonfinite']=='nan':y=None
                if isinstance(x,dict) and 'nonfinite' in x and x['nonfinite']=='nan':x=None
                eq=x==y
                if isinstance(x,(int,float)) and not isinstance(x,bool) and isinstance(y,(int,float)) and not isinstance(y,bool):
                    diff=abs(x-y);numeric+=1;maximum=max(maximum,diff);eq=diff<=1e-12
                if not eq:changes.append({'row':row,'column':col,'actual_retained':x,'reproduced':y})
    return {'axes_exact':axes,'equivalent':axes and not changes,'numeric_cells_compared':numeric,'max_abs_difference':maximum,'differences':changes}
actual_comparison={}
for n, mappings in [('loaded_state.json',{'groups':'_groups_df','DC':'_DC','det_fate':'_det_fate'}),('before_state.json',{'groups':'groups_data','DC':'DC','det_fate':'det_fate'})]:
    saved=read(hist/n);loaded=r if n=='loaded_state.json' else r['modeldata']
    actual_comparison[n]={'path':(hist/n).relative_to(root).as_posix(),'sha256':sha(hist/n),'tables':{k:frame_compare(saved[k],loaded[v]) for k,v in mappings.items()}}
passed=all(x['equivalent'] for record in actual_comparison.values() for x in record['tables'].values())
assert passed,actual_comparison
rv=read(hist/'runtime_verification.json');code=read(out/'code_manifest.json')
assert all(code['retained'][n]['pinned_sha256']==v for n,v in rv['code_sha256'].items())
full={'region':'HS_071','input_sha256':rv['input_sha256'],'historical_engine_hashes_match_actual_runtime_receipt':True,'tolerance':{'absolute':1e-12,'relative':0},'actual_raw_and_completed_groups_diets_routing_reproduced':passed,'comparisons':actual_comparison,'settings':rv['settings'],'no_diagnostic_calls':True,'scope':'Original retained actual six complete tables compared to reproduction under historical code/settings. All loaded current calculator object attributes, raw ModelData fields, balanced_model, indices/names/settings and numerical derived fields compared in runtime_comparison.json; no fresh GE/TE/With Egestion computation performed.'}
write('actual_retained_full_state_verification.json',full)
comparison=read(out/'runtime_comparison.json');comparison['actual_retained_full_state_verification']='actual_retained_full_state_verification.json';comparison['actual_retained_full_state_verified']=passed;write('runtime_comparison.json',comparison)
ledger=read(out/'cell_ledger.json')
for cell in ledger:
    seq=int(cell['consumer_seq']);cell['is_feeding_consumer']=seq<=28
    cell['source_primary_path_HS071']='regions/HS_071/papers/WCP-2007/download-0adcf55e.pdf'
    cell['source_primary_HS071_sha256']=sha(reg/'papers/WCP-2007/download-0adcf55e.pdf')
    if seq>28:
        cell['applicability']='Nonfeeding producer/detritus canonical bookkeeping; no feeding diet/import column in Table4; effective0 preserved.'
    cell['native_consumer_pointer']=f'/group/{seq-1}'
write('cell_ledger.json',ledger)
protected=read(out/'protected_verification.json');now={p:sha(root/p) for p in protected['before']};assert protected['before']==now
protected['after']=now;protected['unchanged']=True;protected['verified_after_all_evidence_writes']=True;write('protected_verification.json',protected)
receipt=read(out/'root_receipt.json');receipt['runtime_comparison']=comparison
receipt['evidence_paths']+=['regions/HS_071/diet_reextraction_20261002/'+n for n in ['primary_source_verification.json','source_inventory.json','actual_retained_full_state_verification.json','runtime_diet_transformations.json','accepted_corrections_verification.json']]
receipt['normalization_status']='verified unnormalized: all252 printed final Table4 diet literals,28 source-prose zero consumer imports and retained extraction/import cells agree exactly; sparse blank-cell structural absence convention explicit'
receipt['precise_blockers']=[];receipt['source_native_fidelity_limits']=['No author-native EwE input is present; printed-source fidelity verified independently against local exact PDF.','No independent all-cell human diet signoff is established; Sep28 human acceptance concerns D_fixed_M0 experimental variant.','Sparse blank diet cells are retained absent links; no missing import or other parameter has been newly filled.','Native multistanza equations are not executed by this calculator; accepted31-group compartment structure preserved.']
receipt['source_cell_counts']={'printed_diet_literals_verified':252,'feeding_consumer_import_zeros_verified':28,'full31by31_diet_effective_cells_recorded':961,'nonfeeding_group_import_bookkeeping_rows':3}
receipt['canonical_model_json_path']='regions/HS_071/models/'+mid+'/model.json';receipt['needed_refresh_scope']='none: retain saved diagnostics, coefficients, regional calculations/map/report scientific sections and their actual historical hashes; no non-exempt runtime difference at abs1e-12 rtol0';receipt['review_state']='Evidence audit only; no new signoff, review registration or approval.'
write('root_receipt.json',receipt)
roles={'primary_source':'primary_source_verification.json','diet_cell_ledger':'cell_ledger.json','consumer_sums':'consumer_source_sums.json','accepted_lineage':'accepted_corrections_verification.json','current_retained_runtime_comparison':'runtime_comparison.json','actual_historical_state':'actual_retained_full_state_verification.json','engine_pin':'code_manifest.json','protected_inputs':'protected_verification.json','handoff':'root_receipt.json'}
artifacts=[{'role':role,'path':n,'sha256':sha(out/n),'availability':'present'} for role,n in roles.items()]
for label in ['retained','current']:
    for n in ['ModelData.py','PPRCalculator.py','utils.py']:
        p=out/'executed_code'/label/n;artifacts.append({'role':'pinned_engine_'+label+'_'+n,'path':p.relative_to(out).as_posix(),'sha256':sha(p),'availability':'present'})
for n in ['retained_loaded_state.json','current_loaded_state.json']:
    artifacts.append({'role':n,'path':n,'sha256':sha(out/n),'availability':'present'})
index={'schema_version':1,'run_id':'HS071_diet_retention_audit_20261002','region_id':'HS_071','model_id':mid,'variant_id':'accepted_D_fixed_M0_option1','source_identity':{'path':os.path.relpath(reg/'papers/WCP-2007/download-0adcf55e.pdf',out).replace('\\','/'),'sha256':sha(reg/'papers/WCP-2007/download-0adcf55e.pdf')},'computational_input_identity':{'path':os.path.relpath(reg/'models'/mid/(mid+'.json'),out).replace('\\','/'),'sha256':receipt['canonical_after_sha256']},'methods':[],'required_roles':list(roles),'artifacts':artifacts,'reconciliation':{'printed_exact':True,'source_import_exact':True,'actual_historical_full_state_reproduced':passed,'nonexempt_runtime_equivalent':comparison['equivalent'],'regional_protected_files_unchanged':True},'stage':'Normalization-retention evidence audit and actual loader state comparison only; fresh diagnostics/re-extraction inapplicable.'}
write('evidence_index.json',index)
print(json.dumps({'actual_saved_full_state_reproduced':passed,'non_exempt_runtime_equivalent':comparison['equivalent'],'protected_unchanged':True,'archive_inputs':len(list((out/'original_inputs').glob('*')))}))
