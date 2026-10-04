import ast,csv,json,pathlib,hashlib,datetime,platform,sys,importlib.metadata,math
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[4];OUT=HERE/'direct_diagnostics'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
save=lambda n,v:(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
runtime={int(r['group_seq']):r for r in csv.DictReader((OUT/'runtime_groups_before.csv').open(encoding='utf-8'))}
source=ROOT/'tools/scientific_code/PPREstimation/PPRCalculator.py'
tree=ast.parse(source.read_text(encoding='utf-8'));thresholds=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DEFAULT_DIAGNOSTIC_THRESHOLDS' for t in n.targets))
ident=json.loads((OUT/'input_identity.json').read_text(encoding='utf-8'))
ident['effective_diagnostic_thresholds']=thresholds
ident['runtime_settings_sha256']=hashlib.sha256(json.dumps({k:ident[k] for k in ['constructor','diagnostic_settings','effective_diagnostic_thresholds']},sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
ident['environment']={'executable':sys.executable,'python':platform.python_version(),'platform':platform.platform(),'packages':{x:importlib.metadata.version(x) for x in ['numpy','pandas','scipy','sympy','igraph']},'run_time_evidence':'UTC modification timestamps of per-method report files; exact wall-clock start was not recorded by the initial bounded runner.'}
ident['methods_executed']=['GE','TE','With Egestion'];ident['global_or_monte_carlo_executed']=False
ident['runtime_code_hashes']={p.name:sha(p) for p in [HERE/'direct_diagnostics.py',source,source.with_name('ModelData.py'),source.with_name('utils.py')]}
save('complete_input_identity.json',ident)
index=[]
for option in ['GE','TE','With Egestion']:
 stem=option.replace(' ','_');report=OUT/(stem+'_report.json')
 for mat in ['SPPR','A','L']:
  p=OUT/(stem+'_'+mat+'.json');d=json.loads(p.read_text(encoding='utf-8'))
  assert all(isinstance(v,(int,float)) and math.isfinite(v) for row in d['values'] for v in row),(option,mat)
  d['row_axis']=[{'group_id':i,'group_name':runtime[i]['group_name'],'trophic_info':runtime[i]['trophic_info'],'synthetic':i==39} for i in d['row_ids']]
  d['column_axis']=[{'group_id':i,'group_name':runtime[i]['group_name'],'trophic_info':runtime[i]['trophic_info'],'synthetic':i==39} for i in d['column_ids']]
  d['masks']={x:[[False]*len(d['column_ids']) for row in d['values']] for x in ['null','nan','positive_infinity','negative_infinity']}
  d['finite_mask']=[[True]*len(d['column_ids']) for row in d['values']]
  d['orientation']='Recipient/consumer groups in rows; basal-source groups in SPPR columns, dependency groups in A/L columns.'
  d['units']='Dimensionless source-specific primary-production requirement per unit recipient mass' if mat=='SPPR' else 'Dimensionless edge weights A = diet / effective transfer; L = A - I'
  d['scope_definitions']={'PP':'Source IDs 1 and 2 only, from runtime trophic_info PP.','inner':'All basal source columns except synthetic external import 39; detritus source 38 is retained.','all':'Every returned basal source column including import 39 and detritus 38.'}
  d['source_sha256']=sha(p);d['csv_sha256']=sha(OUT/(stem+'_'+mat+'.csv'))
  save(stem+'_'+mat+'_lossless.json',d)
  reopened=json.loads((OUT/(stem+'_'+mat+'_lossless.json')).read_text(encoding='utf-8'));assert reopened['values']==d['values'] and reopened['row_axis']==d['row_axis'] and reopened['column_axis']==d['column_axis']
  index.append({'method':option,'matrix':mat,'path':stem+'_'+mat+'_lossless.json','sha256':sha(OUT/(stem+'_'+mat+'_lossless.json')),'shape':[len(d['row_ids']),len(d['column_ids'])],'axis_names_verified':True,'all_entries_finite':True,'reopened_equal':True,'report_last_write_utc':datetime.datetime.fromtimestamp(report.stat().st_mtime,datetime.timezone.utc).isoformat()})
save('lossless_matrix_checks.json',index)
negatives=[]
for option in ['GE','TE','With Egestion']:
 for mat in ['SPPR','A','L']:
  d=json.loads((OUT/(option.replace(' ','_')+'_'+mat+'_lossless.json')).read_text(encoding='utf-8'))
  for i,row in enumerate(d['values']):
   for j,v in enumerate(row):
    if v<0:negatives.append({'method':option,'matrix':mat,'recipient_id':d['row_ids'][i],'recipient_name':runtime[d['row_ids'][i]]['group_name'],'column_id':d['column_ids'][j],'column_name':runtime[d['column_ids'][j]]['group_name'],'value':v,'comparison_tolerance':0.0,'interpretation':'Algebraic L = A - I negative entries are retained, not negative source SPPR.' if mat=='L' else 'Negative entry'})
save('negative_entry_table.json',{'entries':negatives,'negative_SPPR_entries':sum(r['matrix']=='SPPR' for r in negatives),'negative_SPPR_tolerance':0.0,'negative_L_entries_are_operator_terms':True})
save('manual_exclusion_discrepancy.json',{'manual_note':'The researcher SPPR calculation row says seabirds, other mammals, pinnipeds and marine turtles were removed.','accepted_runtime':'Groups 34–37 remain present in both saved and freshly reproduced accepted computational state. All four have finite direct SPPR for all three methods. No exclusions were applied.','manual_row_preserved':True,'resolution':'Qualify the discrepancy in the report Other row; exclusion variants require a distinct future scientific configuration.'})
print('Verified all 9 complete finite matrices with explicit masks and named axes.')
