"""In-memory constructor admission probe; never calculates SPPR or writes inputs."""
import collections, inspect, json, sys, warnings
from pathlib import Path
import openpyxl
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from PPRCalculator import PPRCalculator
from tools.project_core.registry.discovery import discover_regions,discover_models
from tools.project_core.workbooks.workbooks import sha
QA=Path(__file__).resolve().parent.parent/'qa'
defaults={'underdetermined':False,'zero_catch':True,'zero_biomass_accum':True,'default_gs':True,
          'weight_flow':1.0,'weight_guess':1.0,'normalize_DC':False,'DC_tol':0.001,
          'balance_BA_after_DC_normalization':False}
assert set(defaults)==set(inspect.signature(PPRCalculator.__init__).parameters)-{'self','model_number'}
def settings(path):
    wb=openpyxl.load_workbook(path,read_only=True,data_only=False)
    try:
        result={};active=False;header=False
        for row in wb['Overview'].values:
            if not row:continue
            if row[0]=='@table':active=row[1]=='Settings';header=active
            elif active and header:header=False
            elif active and row[0]:result[row[0]]=row[1] if len(row)>1 else None
        return result
    finally:wb.close()
def flags_from(settings,path):
    found=[]
    direct={k:v for k,v in settings.items() if k in defaults and v is not None}
    if direct:found.append({'path':path,'field':'Overview/Settings direct constructor fields','flags':direct})
    for key in ['effective_loader_flags','sppr_configuration','effective_flags','constructor_flags']:
        value=settings.get(key)
        if isinstance(value,str):
            try:value=json.loads(value)
            except ValueError:continue
        if isinstance(value,dict):
            recognized={k:v for k,v in value.items() if k in defaults}
            if recognized:found.append({'path':path,'field':key,'flags':recognized})
    return found
regions=discover_regions(ROOT)
models={(u,m):p for u,w in regions.items() for m,p in discover_models(w.parent).items()}
start={p:sha(p) for p in models.values()}
region_settings={u:settings(w) for u,w in regions.items() if discover_models(w.parent)}
results=[]
for (unit,mid),p in models.items():
    home=p.parent; sources=[];current=region_settings[unit]
    if current.get('results_model_id')==mid:sources+=flags_from(current,regions[unit].relative_to(ROOT).as_posix())
    manifest_path=home/'results/result_manifest.json';saved_path=home/'results/regional_snapshot.xlsx'
    if manifest_path.is_file():
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('model_id')==mid:
            sources+=flags_from(manifest,manifest_path.relative_to(ROOT).as_posix())
            if saved_path.is_file() and sha(saved_path)==manifest['snapshot_sha256']:
                saved=settings(saved_path)
                if saved.get('results_model_id')==mid:sources+=flags_from(saved,saved_path.relative_to(ROOT).as_posix())
    variants={json.dumps(s['flags'],sort_keys=True):s['flags'] for s in sources}
    if not variants:variants={'explicit_strict_constructor_probe':{}}
    for recorded in variants.values():
        opts={**defaults,**recorded}
        item={'unit_id':unit,'model_id':mid,'path':p.relative_to(ROOT).as_posix(),'source_sha256':start[p],
              'probe_options':opts,'stored_constructor_flag_sources':sources,
              'probe_kind':'recorded_partial_flags_with_explicit_probe_defaults' if recorded else 'explicit_strict_constructor_probe_unknown_historical_flags',
              'historical_compatibility_or_approval_claim':False}
        with warnings.catch_warnings(record=True) as observed:
            warnings.simplefilter('always')
            try:
                if opts['underdetermined']:raise RuntimeError('Stored underdetermined=True would run LIM; scientific solver invocation excluded from this constructor-only audit')
                calc=PPRCalculator(str(p),**opts)
                item.update({'constructible':True,'groups':calc.n_groups})
            except Exception as exc:item.update({'constructible':False,'failure_type':type(exc).__name__,'failure':str(exc)})
        item['warnings']=sorted({str(w.message) for w in observed})
        item['source_bytes_unchanged']=sha(p)==start[p]
        results.append(item)
print(f'Constructor probes: {len(results)}, constructed {sum(r["constructible"] for r in results)}',flush=True)
changed=[p.relative_to(ROOT).as_posix() for p,h in start.items() if sha(p)!=h]
record={'schema_version':1,'runtime':sys.executable,'probe_defaults':defaults,'model_count':len(models),
        'probe_count':len(results),'constructed':sum(r['constructible'] for r in results),
        'failed':sum(not r['constructible'] for r in results),'known_partial_flags_probe_count':sum(bool(r['stored_constructor_flag_sources']) for r in results),
        'changed_source_files':changed,'results':results,
        'scope':'In-memory public PPRCalculator constructor only; no SPPR, diagnose_sppr, Monte Carlo, LIM, coefficient export, parameter save, missing-route relaxation or scientific approval.',
        'interpretation':'Unknown historical constructor options remain unknown. Explicit probe defaults are current admission tests, not replication of retained outputs. Existing in-memory Ecopath defaults may fill missing catch, BA or GS; these probe objects are discarded and source missingness remains byte-identical.'}
(QA/'constructor_probe.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['model_count','probe_count','constructed','failed','known_partial_flags_probe_count','changed_source_files']},indent=2),flush=True)
