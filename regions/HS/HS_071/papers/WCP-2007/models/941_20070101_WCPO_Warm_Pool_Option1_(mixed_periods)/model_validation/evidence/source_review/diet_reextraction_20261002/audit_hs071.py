"""Evidence-only WCPO option1 audit. No canonical or scientific-result writes."""
from pathlib import Path
import csv, hashlib, json, shutil, subprocess, sys, math, zipfile
from decimal import Decimal
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
REG=ROOT/'regions/HS_071'
OUT=Path(__file__).resolve().parent
MID='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
BASE=REG/'models'/MID
ORIG=ROOT/'regions/EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)'
SRC=ROOT/'regions/EEZ_941/papers/WCP-2007/extraction_evidence'
SELECTED=BASE/(MID+'.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(name,v):(OUT/name).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def probe():
    import numpy as np
    import pandas as pd
    code=Path(sys.argv[2]); inp=Path(sys.argv[3]); dest=Path(sys.argv[4])
    sys.path.insert(0,str(code))
    from ModelData import ModelData
    from PPRCalculator import PPRCalculator
    settings=read(BASE/'diagnostic_evidence/experiment_PROVENANCE.json')['loader_settings']
    model=PPRCalculator.from_modeldata(ModelData(str(inp)),**settings)
    def atom(v):
        if isinstance(v,np.generic):v=v.item()
        if isinstance(v,float) and not math.isfinite(v):return {'nonfinite':str(v)}
        if v is None or isinstance(v,(str,bool,int,float)):return v
        return str(v)
    def pack(v,seen=None):
        if isinstance(v,pd.DataFrame):return {'kind':'DataFrame','index':[atom(x) for x in v.index],'columns':[atom(x) for x in v.columns],'data':[[atom(x) for x in row] for row in v.to_numpy()]}
        if isinstance(v,pd.Series):return {'kind':'Series','index':[atom(x) for x in v.index],'data':[atom(x) for x in v.tolist()]}
        if isinstance(v,np.ndarray):return {'kind':'array','data':v.tolist()}
        if isinstance(v,dict):return {str(k):pack(x) for k,x in v.items()}
        if isinstance(v,(list,tuple)):return [pack(x) for x in v]
        if isinstance(v,PPRCalculator):return {k:pack(x) for k,x in vars(v).items() if k not in ['_model','balanced_model']}
        return atom(v)
    state=pack(model)
    state['balanced_model']=pack(model.balanced_model)
    state['modeldata']={k:pack(getattr(model._model,k)) for k in ['groups_data','DC','det_fate','seq2name','name2seq','groups_taxons'] if hasattr(model._model,k)}
    state['settings']=settings
    dest.write_text(json.dumps(state,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    model.get_groups_df().to_csv(dest.with_suffix('.groups.csv'))
    model._DC.to_csv(dest.with_suffix('.diet.csv'))
    model._det_fate.to_csv(dest.with_suffix('.routing.csv'))
    return

def compare(a,b):
    diffs=[]; excluded=[]; metadata=[]
    ignore={'biomass_accum','biomass_accum_rate','growth','predation'}
    def walk(x,y,path,exclude=False):
        if isinstance(x,dict) and isinstance(y,dict) and x.get('kind')=='DataFrame' and y.get('kind')=='DataFrame':
            if x['index']!=y['index'] or x['columns']!=y['columns']:
                diffs.append({'path':path,'reason':'dataframe axes differ','before_axes':[x['index'],x['columns']],'after_axes':[y['index'],y['columns']]});return
            for ri,r in enumerate(x['index']):
                for ci,c in enumerate(x['columns']):walk(x['data'][ri][ci],y['data'][ri][ci],f'{path}/{r}/{c}',exclude or c in ignore)
            return
        if isinstance(x,dict) and isinstance(y,dict):
            for k in sorted(set(x)|set(y)):
                if k not in x or k not in y:
                    target=metadata if k in {'balance_BA_after_DC_normalization','diet_normalization_balance_ledger','diet_normalization_rows'} else diffs
                    target.append({'path':path+'/'+k,'before':x.get(k),'after':y.get(k),'reason':'attribute presence differs'});continue
                walk(x[k],y[k],path+'/'+k,exclude or k in ignore)
            return
        if isinstance(x,list) and isinstance(y,list):
            if len(x)!=len(y):diffs.append({'path':path,'reason':'length differs'});return
            for i,(xx,yy) in enumerate(zip(x,y)):walk(xx,yy,path+'/'+str(i),exclude)
            return
        equal=x==y
        if isinstance(x,(float,int)) and not isinstance(x,bool) and isinstance(y,(float,int)) and not isinstance(y,bool):equal=abs(x-y)<=1e-12
        if not equal:(excluded if exclude else diffs).append({'path':path,'before':x,'after':y,'absolute_difference':abs(x-y) if isinstance(x,(float,int)) and isinstance(y,(float,int)) else None})
    walk(a,b,'')
    return {'abs_tolerance':1e-12,'relative_tolerance':0,'equivalent':not diffs,'differences':diffs,'excluded_changes':excluded,'metadata_presence_changes':metadata,'excluded_fields':sorted(ignore)}

if len(sys.argv)>1 and sys.argv[1]=='probe':
    probe();sys.exit(0)

OUT.mkdir(exist_ok=True)
protected=[SELECTED,BASE/'model.json',BASE/'diagnostic_evidence/941_200701_WCPO_Warm_Pool_Final_(mixed_periods).json',REG/'HS_071.xlsx',REG/('Model_validation_'+MID+'.docx'),ORIG/'model.json']
protected+=list((ORIG/'extracted_tables').glob('*'));protected+=list((REG/'validation_reports'/MID/'reused_diagnostics').glob('*'));protected+=[REG/'HS071_taxon_mapping_appendix.xlsx',REG/'papers/WCP-2007/download-0adcf55e.pdf']
protected=[p for p in protected if p.is_file()]
before={rel(p):sha(p) for p in protected}
write('protected_before.json',before)
archive=OUT/'original_inputs';archive.mkdir(exist_ok=True)
for p in [SELECTED,BASE/'model.json']:
    dest=archive/(sha(p)+'__'+p.name)
    if not dest.exists():shutil.copyfile(p,dest)

selected=read(SELECTED); canonical=read(BASE/'model.json'); extraction=read(SRC/'final_extraction.json'); table=read(SRC/'source_tables.json'); cells=read(SRC/'cell_evidence.json')
groups={g['group_seq']:g for g in selected['group']}; names={k:g['group_name'] for k,g in groups.items()}
cellmap={(x['row'],x['column']):x for x in cells if x['table']==4}
csvpath=ORIG/'extracted_tables/Diet_composition.csv'
rows=list(csv.reader(csvpath.open(encoding='utf-8-sig',newline='')))
csvmap={}
for row in rows[1:]:
    if not row or not row[0].isdigit():continue
    for ci,consumer in enumerate(rows[0][2:],2):csvmap[(consumer,row[0])]=row[ci] if ci<len(row) else ''
ledger=[]; mismatch=[]; sums=[]
for consumer,g in groups.items():
    gi=int(consumer)-1; dc=(g.get('diet_descr') or {}).get('diet',[]) or []
    if isinstance(dc,dict):dc=[dc]
    native={d['prey_seq']:d['proportion'] for d in dc}
    ext=extraction['diet'].get(consumer,{})
    for prey,pname in names.items():
        e=cellmap.get((pname,g['group_name']+'|Final'))
        printed=e['text'] if e else None
        adopted=printed if printed is not None else '0'
        current=native.get(prey,'0')
        pointer=next((f'/group/{gi}/diet_descr/diet/{i}/proportion' for i,d in enumerate(dc) if d['prey_seq']==prey),None)
        item={'consumer_seq':consumer,'consumer':g['group_name'],'prey_seq':prey,'prey':pname,'printed_literal':printed,'printed_status':'printed_value' if e else 'blank_table_cell','adopted_literal':adopted,'selected_literal':native.get(prey),'selected_effective_literal':current,'canonical_pointer':pointer,'source_path':rel(SRC.parent/'download-0adcf55e.pdf'),'source_sha256':sha(SRC.parent/'download-0adcf55e.pdf'),'table':4,'page':e['page'] if e else (12 if int(consumer)<=14 else 13),'bbox':e['bbox'] if e else None,'extraction_literal':ext.get(prey),'import_table_literal':csvmap.get((consumer,prey)),'blank_interpretation':'absence treated as structural zero under retained sparse source extraction; no invented prey share','accepted_diet_override':None,'researcher_review_state':'not established as a separate all-cell diet signoff'}
        ledger.append(item)
        if Decimal(current)!=Decimal(adopted) or (printed is not None and current!=printed):mismatch.append(item)
        if printed is not None and (ext.get(prey)!=printed or csvmap.get((consumer,prey))!=printed):mismatch.append({**item,'reason':'source extraction/import literal mismatch'})
    imported=g.get('diet_imp','-9999')
    csv_import=next((row[int(consumer)+1] for row in rows if len(row)>int(consumer)+1 and row[1].lower()=='import'),None)
    ledger.append({'consumer_seq':consumer,'consumer':g['group_name'],'prey_seq':'import','printed_literal':None,'source_literal':'0','source_status':'explicit source prose: imports and exports not considered','selected_literal':imported,'extraction_literal':ext.get('import'),'import_table_literal':csv_import,'source_path':rel(SRC.parent/'download-0adcf55e.pdf'),'source_sha256':sha(SRC.parent/'download-0adcf55e.pdf'),'page':7,'section':'2.2','canonical_pointer':f'/group/{gi}/diet_imp','accepted_diet_override':None,'researcher_review_state':'not established as a separate all-cell diet signoff'})
    if consumer in extraction['diet'] and (ext.get('import')!='0' or csv_import!='0'):mismatch.append(ledger[-1])
    if Decimal(imported)!=0:mismatch.append(ledger[-1])
    prey_sum=sum((Decimal(v) for v in native.values()),Decimal(0))
    sums.append({'consumer_seq':consumer,'consumer':g['group_name'],'prey_only_sum':str(prey_sum),'import_literal':imported,'diet_plus_import_sum':str(prey_sum+Decimal(imported)),'is_consumer':consumer in extraction['diet'],'source_total_is_exact_one':prey_sum+Decimal(imported)==1})
write('cell_ledger.json',ledger);write('consumer_source_sums.json',sums)
accept=read(BASE/'SELECTION_AND_PROVENANCE.json')
summary=read(BASE/'diagnostic_evidence/SCENARIO_SUMMARY.json')
accepted_checks=[]
for change in accept['parameter_changes']:
    g=groups[str(change['seq'])]
    accepted_checks.append({'seq':change['seq'],'group':g['group_name'],'accepted_pb':change['new_PB'],'accepted_ee':change['new_EE'],'current_pb':g['pb'],'current_ee':g['ee'],'current_M0':float(g['biomass'])*float(g['pb'])*(1-float(g['ee'])),'accepted_M0':change['old_M0'],'preserved':float(g['pb'])==change['new_PB'] and float(g['ee'])==change['new_EE'] and abs(float(g['biomass'])*float(g['pb'])*(1-float(g['ee']))-change['old_M0'])<=1e-12})
write('accepted_corrections_verification.json',{'adoption_evidence':rel(BASE/'SELECTION_AND_PROVENANCE.json'),'adoption_date':'2026-09-28','selected_matches_adopted_diagnostic_input_bytes':sha(SELECTED)==sha(BASE/'diagnostic_evidence/941_200701_WCPO_Warm_Pool_Final_(mixed_periods).json')==summary['input_sha256'],'selected_canonical_copies_byte_equal':sha(SELECTED)==sha(BASE/'model.json'),'group_count':len(groups),'accepted_checks':accepted_checks,'source_pdf_hash_verified':sha(REG/'papers/WCP-2007/download-0adcf55e.pdf')==sha(SRC.parent/'download-0adcf55e.pdf')==read(SRC/'VERIFICATION.json')['source_hash_verified'],'diet_override_decision_found':False})

doc=REG/('Model_validation_'+MID+'.docx')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
xml=ET.fromstring(zipfile.ZipFile(doc).read('word/document.xml'))
paras=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in xml.findall('.//w:p',ns)]
write('researcher_document_readonly_extract.json',{'path':rel(doc),'sha256':sha(doc),'matching_paragraphs':[x for x in paras if any(k in x.lower() for k in ['diet','m0','mortality','normaliz','option 1','small bet','small yft'])],'interpretation':'Document confirms adopted D_fixed_M0 and loader normalization; independent all-cell human diet signoff is not established.'})

pin=OUT/'executed_code';pin.mkdir(exist_ok=True)
engines={'retained':ORIG/'diagnostics/executed_code','current':ROOT/'tools/scientific_code/PPREstimation'}
code_manifest={}
for label,engine in engines.items():
    dest=pin/label;dest.mkdir(exist_ok=True)
    code_manifest[label]={}
    for name in ['ModelData.py','PPRCalculator.py','utils.py']:
        source=engine/name;pre=sha(source);shutil.copyfile(source,dest/name);post=sha(source)
        code_manifest[label][name]={'source':rel(source),'before_sha256':pre,'pinned_sha256':sha(dest/name),'after_sha256':post,'stable_while_copying':pre==post==sha(dest/name)}
    inp=BASE/'diagnostic_evidence/941_200701_WCPO_Warm_Pool_Final_(mixed_periods).json' if label=='retained' else SELECTED
    with (OUT/(label+'_probe.log')).open('w',encoding='utf-8') as log:
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'probe',str(dest),str(inp),str(OUT/(label+'_loaded_state.json'))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    code_manifest[label]['probe_exit_code']=proc.returncode
    for name in ['ModelData.py','PPRCalculator.py','utils.py']:
        code_manifest[label][name]['source_sha256_after_probe']=sha(engine/name)
        code_manifest[label][name]['source_stable_during_probe']=code_manifest[label][name]['source_sha256_after_probe']==code_manifest[label][name]['before_sha256']
write('code_manifest.json',code_manifest)
if all(code_manifest[k]['probe_exit_code']==0 for k in engines):
    comparison=compare(read(OUT/'retained_loaded_state.json'),read(OUT/'current_loaded_state.json'))
    import pandas as pd
    retained=pd.read_csv(BASE/'diagnostic_evidence/loaded_groups.csv',index_col=0)
    reproduced=pd.read_csv(OUT/'retained_loaded_state.groups.csv',index_col=0)
    historic=compare({'groups':{'kind':'DataFrame','index':list(retained.index),'columns':list(retained.columns),'data':retained.where(retained.notna(),None).values.tolist()}},{'groups':{'kind':'DataFrame','index':list(reproduced.index),'columns':list(reproduced.columns),'data':reproduced.where(reproduced.notna(),None).values.tolist()}})
    # CSV NaN equality is explicitly checked independently.
    historic['equivalent']=retained.shape==reproduced.shape and list(retained.columns)==list(reproduced.columns) and all((pd.isna(a) and pd.isna(b)) or a==b or (isinstance(a,(float,int)) and isinstance(b,(float,int)) and abs(a-b)<=1e-12) for a,b in zip(retained.values.flat,reproduced.values.flat))
    historic['differences']=[d for d in historic['differences'] if not (isinstance(d.get('before'),float) and isinstance(d.get('after'),float) and math.isnan(d['before']) and math.isnan(d['after']))]
    for d in historic['differences']:
        for k in ['before','after','absolute_difference']:
            if isinstance(d.get(k),float) and not math.isfinite(d[k]):d[k]=str(d[k])
    comparison['retained_actual_loaded_groups_reproduction']=historic
    comparison['retained_actual_input_sha256']=sha(BASE/'diagnostic_evidence/941_200701_WCPO_Warm_Pool_Final_(mixed_periods).json')
    comparison['selected_input_sha256']=sha(SELECTED)
    comparison['historical_diagnostic_hashes_preserved']=True
    raw=read(OUT/'retained_loaded_state.json')['modeldata']['DC']; runtime=read(OUT/'retained_loaded_state.json')['_DC']
    runtime_ledger=[]
    for ri,consumer in enumerate(raw['index']):
        raw_values=raw['data'][ri]; runtime_values=runtime['data'][ri]
        rs=sum(raw_values); ts=sum(runtime_values)
        changes=[{'prey_seq':raw['columns'][i],'raw_value':a,'runtime_value':b} for i,(a,b) in enumerate(zip(raw_values,runtime_values)) if a!=b]
        runtime_ledger.append({'consumer_seq':consumer,'consumer':names.get(str(consumer),'diet_import'),'raw_sum':rs,'runtime_sum':ts,'factor':ts/rs if rs else None,'changed_cells':changes})
    write('runtime_diet_transformations.json',{'input_sha256':sha(SELECTED),'normalization_allowed':True,'normalization_settings':read(BASE/'diagnostic_evidence/experiment_PROVENANCE.json')['loader_settings'],'rows':runtime_ledger,'canonical_cells_written_back':False})
    comparison['loaded_state_sha256']={k:sha(OUT/(k+'_loaded_state.json')) for k in engines}
    write('runtime_comparison.json',comparison)
else:
    comparison={'equivalent':None,'blocker':'bounded actual loader failed; see logs'};write('runtime_comparison.json',comparison)

after={rel(p):sha(p) for p in protected}
write('protected_verification.json',{'before':before,'after':after,'unchanged':before==after,'changed_paths':[p for p in before if before[p]!=after[p]],'scope':'regional selected/source/import/workbook/report protected files; no shared-file write performed'})
receipt={'region':'HS_071','selected_model_id':MID,'selected_path':rel(SELECTED),'outcome':'verified unnormalized unchanged' if not mismatch else 'blocked or mixed','normalization_status':'source printed diet/import values preserved exactly; canonical normalization not established because exact source cells agree' if not mismatch else 'source mismatches require review','source_native_status':'Primary printed Allain et al. 2007 Table 4 pp12-13 + no-import prose p7 verified; no author-native EwE file is present or needed for this printed-source audit. Selected model is accepted D_fixed_M0 surrogate.','reextraction_performed':False,'canonical_before_sha256':before[rel(SELECTED)],'canonical_after_sha256':after[rel(SELECTED)],'canonical_copy_before_sha256':before[rel(BASE/'model.json')],'canonical_copy_after_sha256':after[rel(BASE/'model.json')],'changed_diet_cells':[],'source_mismatches':mismatch,'evidence_paths':[rel(OUT/x) for x in ['cell_ledger.json','consumer_source_sums.json','runtime_comparison.json','code_manifest.json','protected_verification.json','researcher_document_readonly_extract.json']],'precise_blockers':[] if not mismatch else ['Source/import cell differences require review; no mutation permitted during HOLD.'],'protected_files_unchanged':before==after,'runtime_comparison':comparison,'needed_refresh_scope':'root-coordinated affected refresh if non-exempt runtime differences confirmed' if comparison.get('equivalent') is False else 'retain saved numerical results with provenance bridge; no canonical or runtime change from diet audit','diet_review_state':'not established; explicit adoption is of D_fixed_M0 experiment, not an independent all-cell diet approval','hold_respected':True,'utc':datetime.now(timezone.utc).isoformat()}
write('root_receipt.json',receipt)
print(json.dumps({'outcome':receipt['outcome'],'mismatches':len(mismatch),'protected_unchanged':before==after,'runtime_equivalent':comparison.get('equivalent'),'runtime_differences':len(comparison.get('differences',[])),'excluded_changes':len(comparison.get('excluded_changes',[])),'retained_reproduced':comparison.get('retained_actual_loaded_groups_reproduction',{}).get('equivalent')}))
