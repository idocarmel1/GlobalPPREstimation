"""Authorized nonfeeding-row structural-zero adaptation; preserve baseline failures."""
from pathlib import Path
import sys, json, hashlib, gzip, multiprocessing as mp, warnings, copy
from datetime import datetime, timezone
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
from tools.scientific_helpers.sppr import method_coverage as mc
from run_ices_diagnostics import MODEL, OUT as BASE, FLAGS, KEYS
OUT=BASE/'structural_zero'

def worker(connection):
    try:
        _, ModelData, Calculator, _=mc._engine()
        with warnings.catch_warnings(record=True) as notices:
            warnings.simplefilter('always')
            source=ModelData(str(MODEL))
            raw=mc.encode_lossless({'groups':source.groups_data,'diet':source.DC,'detritus_fate':source.det_fate})
            adapted=copy.deepcopy(source)
            actual_nan=[(int(i),int(j)) for i in source.DC.index for j in source.DC.columns if source.DC.loc[i,j]!=source.DC.loc[i,j]]
            assert set(actual_nan)=={(66,70),(67,70),(68,70),(69,70)},actual_nan
            for i,j in actual_nan:
                assert source.groups_data.loc[i,'trophic_info'] in ['PP','DET']
                adapted.DC.loc[i,j]=0.0
            model=Calculator.from_modeldata(adapted,**mc._constructor(FLAGS,MODEL))
        initial={'status':'ready','raw_source_state':raw,
            'adapted_source_state':mc.encode_lossless({'groups':adapted.groups_data,'diet':adapted.DC,'detritus_fate':adapted.det_fate}),
            'adaptation_cells':[{'recipient_id':i,'recipient_name':model.seq2name[i],'source_id':j,
                'source_name':model.seq2name[j],'before':'NaN','after':0.0,
                'reason':'Operational no-feeding convention for a primary-producer/detritus row; not a measured source import.'} for i,j in actual_nan],
            'runtime':mc._runtime(model),'groups':mc._group_metadata(model),'warnings':[str(w.message) for w in notices]}
        connection.send(initial)
    except Exception:
        connection.send({'status':'constructor_failed','exception':mc._error()});return
    while True:
        key=connection.recv()
        if key is None:return
        connection.send(mc._run(model,mc.method_settings(key,FLAGS,MODEL)))

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=True)
    canonical=hashlib.sha256(MODEL.read_bytes()).hexdigest()
    identity={'model_id':MODEL.parent.name,'canonical_model_sha256':canonical,
        'variant_id':'current_standard_loader_nonfeeding_import_structural_zero_ee_floor_0.1',
        'constructor':mc._constructor(FLAGS,MODEL),'flags':FLAGS,'engine_hashes':mc.engine_identity(),
        'adaptation':'Exactly four nonfeeding DC synthetic-import cells (66–69,70) NaN→0 on an ephemeral copy. Source missingness is preserved. No producer fate/routing/TL/BA/canonical edits.',
        'original_attempt':'../summary.json'}
    parent,child=mp.get_context('spawn').Pipe();process=mp.get_context('spawn').Process(target=worker,args=(child,));process.start();child.close()
    try:
        initial=parent.recv() if parent.poll(300) else {'status':'constructor_timeout'}
        mc._save(OUT/'constructor.json.gz',{'schema_version':1,'identity':identity,'constructor_outcome':initial})
        summary={'schema_version':1,'identity':identity,'constructor_status':initial['status'],'methods':[]}
        for key in KEYS:
            print('Structural-zero '+key,flush=True)
            if initial['status']=='ready':
                parent.send(key)
                outcome=parent.recv() if parent.poll(180) else {'status':'timeout','reason':'Method exceeded 180 seconds'}
            else:outcome={'status':'NOT_RUN','reason':'Constructor unavailable','constructor_outcome':initial}
            doc={'schema_version':1,'timestamp':datetime.now(timezone.utc).isoformat(),'identity':identity,
                'settings':mc.method_settings(key,FLAGS,MODEL),'groups':initial.get('groups',[]),
                'matrix_orientation':'recipient rows by basal-source columns','sppr_units':'wet-weight primary production equivalent per wet-weight unit of group',
                'scope_definitions':{'all':'all basal sources','inner':'exclude synthetic imports','PP':'exclude imports and detritus'},**outcome}
            evidence=mc._save(OUT/(key+'.json.gz'),doc)
            diag=outcome.get('diagnostics') or {};matrix=outcome.get('source_matrix');negative=[];checks={}
            if matrix:
                names={str(x['id']):x['name'] for x in initial['groups']}
                for i,row in enumerate(matrix['data']):
                    for j,v in enumerate(row):
                        if isinstance(v,(int,float)) and v<0:negative.append({'source_id':matrix['columns'][j],'source_name':names.get(str(matrix['columns'][j])),
                            'group_id':matrix['index'][i],'group_name':names.get(str(matrix['index'][i])),'value':v,'comparison_tolerance':0})
                checks={'shape':matrix['shape'],'negative_source_count':len({x['source_id'] for x in negative}),
                    'diagnostic_negative_count':diag.get('divergence',{}).get('n_negative_sources'),
                    'mask_counts':{k:sum(sum(row) for row in mask) for k,mask in matrix['masks'].items()},
                    'unique_axes':len(set(matrix['index']))==len(matrix['index']) and len(set(matrix['columns']))==len(matrix['columns'])}
            summary['methods'].append({'method':key,'execution_status':outcome['status'],'reason':outcome.get('reason'),
                'diagnostic':diag,'negative_entries':negative,'matrix_checks':checks,'exception':outcome.get('exception'),
                'reconciliation':outcome.get('reconciliation'),'annual_status':outcome.get('annual_status'),'evidence':evidence})
            if outcome['status']=='timeout':break
        summary['canonical_unchanged']=hashlib.sha256(MODEL.read_bytes()).hexdigest()==canonical
        (OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
        print(json.dumps([{'method':x['method'],'execution':x['execution_status'],'diagnostic_status':x['diagnostic'].get('status'),'rho':x['diagnostic'].get('divergence',{}).get('rho_living'),'b':x['diagnostic'].get('divergence',{}).get('b'),'negative_entries':len(x['negative_entries'])} for x in summary['methods']]),flush=True)
    finally:
        if process.is_alive():process.terminate()
        process.join(5);parent.close()
if __name__=='__main__':main()
