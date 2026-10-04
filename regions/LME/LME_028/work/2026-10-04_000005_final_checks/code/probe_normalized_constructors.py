"""Existing runtime-diet constructor convention, without invoking LIM or SPPR."""
import collections, inspect, json, sys, warnings
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from PPRCalculator import PPRCalculator
from tools.project_core.workbooks.workbooks import sha
QA=Path(__file__).resolve().parent.parent/'qa'
inventory=json.loads((QA/'canonical_navigation_verification.json').read_text(encoding='utf-8'))
strict=json.loads((QA/'constructor_probe.json').read_text(encoding='utf-8'))
strict_by_id={(r['unit_id'],r['model_id']):r for r in strict['results']}
opts={k:p.default for k,p in inspect.signature(PPRCalculator.__init__).parameters.items() if k not in ['self','model_number']}
opts['normalize_DC']=True
assert opts['underdetermined'] is False
assert opts['DC_tol']==0.001
engine=ROOT/'tools/scientific_code/PPREstimation'
engine_hashes={n:sha(engine/n) for n in ['ModelData.py','PPRCalculator.py','utils.py','create_PPRS_excel.py']}
out=[]
for index,model in enumerate(inventory['model_compatibility'],1):
    path=ROOT/model['path'];initial=sha(path)
    item={'unit_id':model['unit_id'],'model_id':model['model_id'],'path':model['path'],'source_sha256':initial,
          'flags':opts,'probe_kind':'PPRCalculator_defaults_with_existing_production_runtime_DC_normalization',
          'historical_compatibility_or_approval_claim':False,
          'strict_constructible':strict_by_id[(model['unit_id'],model['model_id'])]['constructible']}
    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter('always')
        try:
            calc=PPRCalculator(str(path),**opts)
            raw=calc._model.DC.reindex(index=calc._DC.index,columns=calc._DC.columns)
            ledger=getattr(calc,'diet_normalization_balance_ledger',None)
            item.update({'constructible':True,'groups':calc.n_groups,
                         'runtime_diet_cells_changed':int(raw.ne(calc._DC).to_numpy().sum()),
                         'runtime_BA_closure_groups':int(ledger['applied'].fillna(False).sum()) if ledger is not None and 'applied' in ledger else 0})
        except Exception as exc:item.update({'constructible':False,'failure_type':type(exc).__name__,'failure':str(exc)})
    item['warnings']=sorted({str(w.message) for w in observed})
    item['source_bytes_unchanged']=sha(path)==initial==model['sha256']
    out.append(item)
    if index%10==0:print(f'Normalized-profile constructors checked: {index}/{len(inventory["model_compatibility"])}',flush=True)
failures=[r for r in out if not r['constructible']]
record={'schema_version':1,'runtime':sys.executable,'probe_options':opts,'engine_hashes':engine_hashes,
        'model_count':len(out),'constructed':sum(r['constructible'] for r in out),'failed':len(failures),
        'strict_failed_but_runtime_normalized_constructs':sum(r['constructible'] and not r['strict_constructible'] for r in out),
        'changed_source_files':[r['path'] for r in out if not r['source_bytes_unchanged']],
        'engine_bytes_unchanged':all(sha(engine/n)==h for n,h in engine_hashes.items()),'results':out,
        'profile_evidence':{'path':'tools/scientific_code/PPREstimation/create_PPRS_excel.py','function':'load_model','actual_explicit_arguments':{'underdetermined':True,'zero_biomass_accum':False,'DC_tol':0.001,'normalize_DC':True},
                            'probe_choice':'Authorized alternative: public PPRCalculator defaults plus that existing runtime diet normalization convention. No LIM. Exact production exporter profile is not executed because underdetermined=True invokes a scientific optimizer.'},
        'interpretation':['A strict nonunit diet rejection does not establish general JSON incompatibility when the existing runtime normalizer can construct it.',
                          'Source bytes, publication missingness and prior stored diagnostics/reviews remain unchanged. New in-memory probe objects and their computational defaults/BA closures are discarded.',
                          'The unchanged multi-DET missing-routing guard remains in force. Constructor admission is distinct from SPPR convergence, source fidelity, production admission and researcher approval.',
                          'No SPPR, diagnose_sppr, Monte Carlo, LIM, output export or saved scientific repair is performed. The constructor itself retains its existing internal property completion and balance-copy behavior.']}
(QA/'normalized_constructor_probe.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['model_count','constructed','failed','strict_failed_but_runtime_normalized_constructs','changed_source_files','engine_bytes_unchanged']},indent=2),flush=True)
