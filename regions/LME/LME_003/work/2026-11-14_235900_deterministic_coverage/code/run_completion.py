"""Bounded deterministic coverage run; no parameter edits or Monte Carlo."""
from __future__ import annotations
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
WORK = Path(__file__).resolve().parents[1]
RUN_ID = 'deterministic_completion_20261114'
from tools.scientific_helpers.sppr import method_coverage as adapter
from tools.scientific_helpers.sppr.ppr_scopes import read_scopes
import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def replay_flags(item):
    flags = copy.deepcopy(item['flags'])
    model_dir = ROOT/item['model_dir']
    inventory=read(WORK/'inputs/validated_inventory.json')
    imported={}
    for name in adapter.ENGINE_FILES:
        if name in flags.get('engine_sources',{}):continue
        expected=flags['engine_source_hashes'][name]
        candidates=list(model_dir.rglob(name))+[adapter.ENGINE/name]
        for peer in inventory['pairs']:
            ref=peer['flags'].get('engine_sources',{}).get(name)
            if ref and peer['flags']['engine_source_hashes'].get(name)==expected:
                candidates.append(ROOT/peer['model_dir']/ref)
        source=next((p for p in candidates if p.is_file() and sha(p)==expected),None)
        if source is None:raise ValueError('Exact recorded dependency could not be recovered: '+name)
        if source.resolve().is_relative_to(model_dir.resolve()):
            flags.setdefault('engine_sources',{})[name]=source.relative_to(model_dir).as_posix()
        else:
            target=model_dir/'results/diagnostics/method_coverage'/RUN_ID/'executed_dependencies'/name
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():target.write_bytes(source.read_bytes())
            if sha(target)!=expected:raise ValueError('Recovered dependency copy changed: '+name)
            flags.setdefault('engine_sources',{})[name]=target.relative_to(model_dir).as_posix()
            imported[name]={'sha256':expected,'original_path':source.relative_to(ROOT).as_posix(),
                            'role':'Exact recorded dependency bytes; no scientific modification'}
    if imported:
        provenance=model_dir/'results/diagnostics/method_coverage'/RUN_ID/'executed_dependencies/engine_copy_provenance.json'
        old=read(provenance) if provenance.exists() else {}
        save(provenance,{'canonical_model_sha256':item['canonical_model_sha256'],
                         'files':{**old.get('files',{}),**imported}})
    from tools.scientific_helpers.sppr.configuration import _pin_engine
    flags = _pin_engine(model_dir.resolve(), flags, item['canonical_model_sha256'])
    # Older records allowed byte-identical dependencies from the shared engine.
    # Bind a model-local copy of those exact recorded bytes for portable replay.
    paths = adapter._engine_paths(flags, model_dir/'model.json')
    for name in adapter.ENGINE_FILES:
        if name not in flags.get('engine_sources', {}):
            target = model_dir/'results/diagnostics/method_coverage'/RUN_ID/'executed_dependencies'/name
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = paths[name].read_bytes()
            if hashlib.sha256(raw).hexdigest() != flags['engine_source_hashes'][name]:
                raise ValueError('Recorded dependency hash differs: '+name)
            if not target.exists():target.write_bytes(raw)
            flags.setdefault('engine_sources', {})[name] = target.relative_to(model_dir).as_posix()
    descriptor = {'schema_version': 1, 'model_sha256': item['canonical_model_sha256'],
                  'mode': 'completed_runtime', 'provenance': copy.deepcopy(item['provenance'])}
    # Java's retained runtime uses an older abbreviated table encoding; its
    # recorded execution had no post-loader changes, so replay its exact loader.
    if item['unit_id'] == 'LME_038':
        descriptor['mode'] = 'recorded_constructor'
    else:
        reference = item['runtime_replay']
        descriptor['runtime'] = {key: reference[key] for key in ('relative_path', 'sha256')}
        descriptor['runtime']['keys'] = [part for part in reference.get('json_pointer', '').split('/') if part]
    descriptor['provenance'] = {k:descriptor['provenance'][k] for k in ('relative_path','sha256')}
    if descriptor['provenance']['relative_path'] == 'results/result_manifest.json':
        baseline = model_dir/'results/diagnostics/method_coverage'/RUN_ID/'inputs/accepted_result_manifest.json'
        baseline.parent.mkdir(parents=True, exist_ok=True)
        original = model_dir/'results/result_manifest.json'
        if not baseline.exists():
            if sha(original) != descriptor['provenance']['sha256']:
                raise ValueError('Accepted execution manifest changed before replay')
            baseline.write_bytes(original.read_bytes())
        descriptor['provenance']['relative_path'] = baseline.relative_to(model_dir).as_posix()
    flags['audited_replay'] = descriptor
    return flags


def control(item):
    model_dir = ROOT/item['model_dir']; model = model_dir/'model.json'
    flags = replay_flags(item)
    directory = model_dir/'results/diagnostics/method_coverage'/RUN_ID/'controls'
    report_path = directory/'verification.json'
    identity = {'model_sha256':sha(model), 'source_sha256':sha(model_dir/'sppr_source.xlsx'),
                'flags':flags, 'engine_identity':adapter.engine_identity(flags,model)}
    if report_path.is_file():
        saved=read(report_path)
        if saved.get('passed') and saved.get('identity')==identity:
            print(item['unit_id']+': reuse authenticated GE/TE control',flush=True)
            return saved
    result=adapter.compute_methods(model, flags, ['new_GE','new_TE_EEfix'], directory,
                                   progress=lambda s:print(s,flush=True),method_timeout=0)
    source=read_scopes(model_dir/'sppr_source.xlsx')
    comparisons=[]; passed=True
    for key in ['new_GE','new_TE_EEfix']:
        outcome=result['methods'][key]
        entry={'method':key,'execution_status':outcome['status'],'reason':outcome.get('reason'),
               'exception':outcome.get('exception'),'checks':[]}
        if outcome['status']!='ok':
            passed=False
        else:
            for scope,(methods,groups) in source.items():
                if key not in methods:
                    passed=False;entry['checks'].append({'scope':scope,'error':'control method missing in source'});continue
                column=methods.index(key); got=outcome['scopes'][scope]
                wanted={name:values[column] for name,values in groups.items()}
                if set(wanted)!=set(got):
                    passed=False;entry['checks'].append({'scope':scope,'error':'group identity mismatch',
                                                       'missing':sorted(set(wanted)-set(got)),
                                                       'extra':sorted(set(got)-set(wanted))});continue
                a=np.array([got[name] if got[name] is not None else np.nan for name in wanted])
                b=np.array([wanted[name] if wanted[name] is not None else np.nan for name in wanted])
                good=np.allclose(a,b,rtol=1e-10,atol=1e-12,equal_nan=True)
                passed=passed and bool(good)
                finite=np.isfinite(a)&np.isfinite(b)
                entry['checks'].append({'scope':scope,'passed':bool(good),'groups':len(wanted),
                                        'max_absolute_error':float(np.max(abs(a[finite]-b[finite]))) if finite.any() else 0})
        comparisons.append(entry)
    report={'unit_id':item['unit_id'],'model_id':item['model_id'],'identity':identity,
            'passed':passed,'comparisons':comparisons,
            'scientific_scope':'Exact retained GE/TE numerical reproduction; existing coefficients unchanged'}
    save(report_path,report)
    save(WORK/'outputs'/f"{item['unit_id']}_control.json",report)
    print(item['unit_id']+': GE/TE control '+('PASS' if passed else 'FAILED'),flush=True)
    return report


def repaired_flags(item, flags, repair='symbolic_repairs_v1'):
    from tools.scientific_helpers.sppr.symbolic_repairs import repair_symbolic_source
    flags=copy.deepcopy(flags)
    model_dir=ROOT/item['model_dir'];model=model_dir/'model.json'
    source=adapter._calculation_engine_path(flags,model) or adapter._engine_paths(flags,model)['PPRCalculator.py']
    raw=source.read_bytes()
    derived,changes=repair_symbolic_source(raw.decode('utf-8-sig'),repair=repair)
    folder='executed_repairs' if repair=='symbolic_repairs_v1' else 'executed_repairs_v2'
    directory=model_dir/'results/diagnostics/method_coverage'/RUN_ID/folder
    directory.mkdir(parents=True,exist_ok=True)
    target=directory/'PPRCalculator.py'
    payload=derived.encode('utf-8')
    if target.exists() and target.read_bytes()!=payload:
        raise ValueError('Previously pinned symbolic derivative differs')
    if not target.exists():target.write_bytes(payload)
    save(directory/'repair_manifest.json',{'base_path':source.relative_to(model_dir).as_posix(),
         'base_sha256':sha(source),'derived_sha256':sha(target),'transformation':changes,
         'scope':'Literal group symbols, identity-substitution termination, and guarded zero-weight axis alignment only'})
    flags['audited_replay']['symbolic_repair']={'relative_path':target.relative_to(model_dir).as_posix(),
         'sha256':sha(target),'base_sha256':sha(source),'repair':repair}
    adapter.engine_identity(flags,model)
    return flags


def authenticate_methods(item, result, directory):
    """Bind each outcome to its actual immutable return and constructor record."""
    from provenance_admission import verify_initialization
    model=ROOT/item['model_dir']/'model.json'
    for key,outcome in result.get('methods',{}).items():
        ref=outcome['evidence'];evidence=(directory/ref['path']).resolve()
        if not evidence.is_relative_to(directory.resolve()) or sha(evidence)!=ref['sha256']:
            raise ValueError('Cached method evidence changed: '+key)
        document=read(evidence);identity=document['identity']
        if identity['model_sha256']!=sha(model) or identity['engine_hashes']!=adapter.engine_identity(identity['flags'],model):
            raise ValueError('Cached method execution identity changed: '+key)
        if document['settings']['method']!=key or document['scopes']!=outcome['scopes'] or document['status']!=outcome['status']:
            raise ValueError('Cached method summary differs from immutable return: '+key)
        outcome['execution_identity']=copy.deepcopy(identity)
        constructor=outcome.get('constructor_evidence')
        embedded=document.get('constructor_evidence')
        if constructor is None and embedded:
            constructor=copy.deepcopy(embedded)
            constructor['path']=(evidence.parent/embedded['path']).relative_to(directory.resolve()).as_posix()
        constructor=constructor or result['constructor_evidence']
        if embedded and embedded['sha256']!=constructor['sha256']:
            raise ValueError('Method constructor differs from its immutable recorded reference: '+key)
        constructor_path=(directory/constructor['path']).resolve()
        if not constructor_path.is_relative_to(directory.resolve()) or sha(constructor_path)!=constructor['sha256']:
            raise ValueError('Cached constructor evidence changed: '+key)
        outcome['constructor_evidence']=copy.deepcopy(constructor)
        verify_initialization(model,directory,key,outcome,document)
    return result


def ewe_flags(item, flags):
    from tools.scientific_helpers.sppr.ewe_path_optimization import repair_ewe_source, REPAIR
    flags=copy.deepcopy(flags)
    model_dir=ROOT/item['model_dir'];model=model_dir/'model.json'
    source=adapter._calculation_engine_path(flags,model) or adapter._engine_paths(flags,model)['PPRCalculator.py']
    derived,certificate=repair_ewe_source(source.read_bytes().decode('utf-8-sig'),force_fast=True)
    directory=model_dir/'results/diagnostics/method_coverage'/RUN_ID/'executed_ewe_optimization'
    directory.mkdir(parents=True,exist_ok=True)
    target=directory/'PPRCalculator.py';payload=derived.encode('utf-8')
    if target.exists() and target.read_bytes()!=payload:raise ValueError('Pinned EwE derivative changed')
    if not target.exists():target.write_bytes(payload)
    save(directory/'repair_manifest.json',{'base_path':source.relative_to(model_dir).as_posix(),
         'base_sha256':sha(source),'derived_sha256':sha(target),'certificate':certificate,
         'scope':'EwE EE numeric parity with original slow path enumeration; explicit path lists omitted'})
    flags['audited_replay']['ew_e_optimized']={'relative_path':target.relative_to(model_dir).as_posix(),
         'sha256':sha(target),'base_sha256':sha(source),'repair':REPAIR}
    adapter.engine_identity(flags,model)
    return flags


def execute(item, *, nonsymbolic=False, symbolic=False, repair='symbolic_repairs_v1', retry_unavailable=False, method_keys=None, optimize_ewe=False):
    model_dir=ROOT/item['model_dir'];model=model_dir/'model.json'
    report_path=model_dir/'results/diagnostics/method_coverage'/RUN_ID/'controls/verification.json'
    report=read(report_path) if report_path.is_file() else control(item)
    if not report.get('passed') or report['identity']['model_sha256']!=sha(model):
        raise ValueError('GE/TE numerical control has not passed')
    flags=replay_flags(item)
    if report['identity']['engine_identity']!=adapter.engine_identity(flags,model):
        raise ValueError('Execution engine changed since GE/TE control')
    keys=[key for key in item['pending_non_mc_methods'] if
          (not nonsymbolic or not key.startswith('sym_')) and (not symbolic or key.startswith('sym_'))
          and (not method_keys or key in method_keys)]
    if not keys:return {'unit_id':item['unit_id'],'passed':True,'methods':{},'executed':[]}
    # These budgets govern execution, not scientific settings. Most algebraic
    # methods run in-process; path enumeration and symbolic solves stay bounded.
    flags['method_timeout_seconds']=0
    flags['method_timeout_overrides_seconds']={**flags.get('method_timeout_overrides_seconds',{}),
        'EwE_TE_EE':600,**{key:300 for key in keys if key.startswith('sym_')}}
    directory=model_dir/'results/diagnostics/method_coverage'/RUN_ID/'calculated'
    cache=directory/'calculated.json'
    cached=authenticate_methods(item,read(cache),directory) if cache.is_file() else None
    cached_methods=cached.get('methods',{}) if cached else {}
    pending=[key for key in keys if key not in cached_methods or
             (retry_unavailable and cached_methods[key].get('status')!='ok')]
    if pending:
        batch_directory=directory
        if optimize_ewe:
            if pending!=['EwE_TE_EE']:raise ValueError('EwE optimization is bounded to the missing EE method')
            flags=ewe_flags(item,flags)
            batch_directory=directory/'ewe_optimized'
        elif any(key.startswith('sym_') for key in pending):
            flags=repaired_flags(item,flags,repair)
            batch_directory=directory/('symbolic' if repair=='symbolic_repairs_v1' else 'symbolic_v2')
        if any(key in cached_methods for key in pending):
            prior=directory/('calculated_before_'+batch_directory.name+'.json')
            if prior.exists():raise ValueError('Retry directory already has prior evidence; use a new versioned attempt')
            save(prior,cached)
        result=adapter.compute_methods(model,flags,pending,batch_directory,
                                       progress=lambda s:print(s,flush=True))
        result=authenticate_methods(item,result,batch_directory)
        if batch_directory!=directory:
            for outcome in result['methods'].values():
                for name in ('evidence','constructor_evidence'):
                    outcome[name]['path']=(batch_directory/outcome[name]['path']).relative_to(directory).as_posix()
            for name in ('constructor_evidence','evidence_index'):
                result[name]['path']=(batch_directory/result[name]['path']).relative_to(directory).as_posix()
        result['methods']={**cached_methods,**result['methods']}
        authenticate_methods(item,result,directory)
        save(cache,result)
    else:
        result=cached
        if result:save(cache,result)
    summary={'unit_id':item['unit_id'],'model_id':item['model_id'],'passed':True,
             'executed':pending,'cache':cache.relative_to(ROOT).as_posix(),
             'methods':{k:{'status':v['status'],'reason':v.get('reason'),'annual_status':v.get('annual_status'),
                           'exception':v.get('exception'),'elapsed_seconds':v.get('elapsed_seconds')}
                        for k,v in result['methods'].items()}}
    save(WORK/'outputs'/f"{item['unit_id']}_calculation.json",summary)
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--units',nargs='*');parser.add_argument('--phase',default='control');parser.add_argument('--nonsymbolic',action='store_true');parser.add_argument('--symbolic',action='store_true')
    parser.add_argument('--repair',default='symbolic_repairs_v1',choices=['symbolic_repairs_v1','symbolic_repairs_v2'])
    parser.add_argument('--retry-unavailable',action='store_true');parser.add_argument('--methods',nargs='+')
    parser.add_argument('--optimize-ewe',action='store_true')
    args=parser.parse_args();inventory=read(WORK/'inputs/validated_inventory.json')
    selected=[item for item in inventory['pairs'] if item['pending_non_mc_methods'] and
              (not args.units or item['unit_id'] in args.units)]
    results=[]
    for item in selected:
        try:
            if args.phase=='control':results.append(control(item))
            elif args.phase=='execute':results.append(execute(item,nonsymbolic=args.nonsymbolic,symbolic=args.symbolic,repair=args.repair,retry_unavailable=args.retry_unavailable,method_keys=args.methods,optimize_ewe=args.optimize_ewe))
            else:raise ValueError('Unknown phase')
        except Exception as error:
            import traceback
            record={'unit_id':item['unit_id'],'passed':False,'error':str(error),'traceback':traceback.format_exc()}
            save(WORK/'outputs'/f"{item['unit_id']}_error.json",record);results.append(record)
            print(item['unit_id']+': '+str(error),flush=True)
    save(WORK/'qa'/('batch_'+args.phase+('_'+'_'.join(args.units) if args.units else '')+'.json'),results)
    if any(not r.get('passed') for r in results):raise SystemExit(1)


if __name__=='__main__':main()
