"""Isolated, fixed-rate whole-network diet sensitivity; never publish/adopt."""
from pathlib import Path
import copy, gzip, hashlib, inspect, json, os, platform, sys, time, traceback, warnings
from datetime import datetime, timezone
import numpy as np
import pandas as pd

RUN = Path(__file__).resolve().parents[1]
ROOT = next(p for p in RUN.parents if (p/'README.md').exists() and (p/'tools/scientific_helpers').exists())
sys.path.insert(0, str(ROOT))
from tools.scientific_helpers.sppr import method_coverage as mc
MODEL = ROOT/'regions/LME/LME_028/papers/GUI-2004/models/28_646_Guinea_(1998)'
for folder in ('inputs','outputs','qa'): (RUN/folder).mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return os.path.relpath(p, RUN).replace('\\','/')
def save(p, data):
    raw = json.dumps(mc.encode_lossless(data), ensure_ascii=False, indent=2, allow_nan=False).encode('utf-8')
    if p.suffix == '.gz':
        p.write_bytes(gzip.compress(raw,mtime=0)); assert gzip.decompress(p.read_bytes()) == raw
    else: p.write_bytes(raw)
    return json.loads(raw)
def read(p): return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text(encoding='utf-8'))
protected = [p for base in (MODEL, ROOT/'interactive_map') for p in base.rglob('*')
             if p.is_file() and p.name.lower()!='notes for ai.txt' and '__pycache__' not in p.parts]
protected += [ROOT/'regions/LME/LME_028/LME_028.xlsx',ROOT/'regions/human-validated.xlsx',ROOT/'Project.xlsx',ROOT/'tools/knowledge_graph/graph.json']
protected = sorted(set(p for p in protected if p.exists()))
before = {rel(p):sha(p) for p in protected}
save(RUN/'inputs/protected_hashes.json',before)
manifest = read(MODEL/'results/result_manifest.json'); flags=manifest['effective_flags']
assert sha(MODEL/'model.json') == manifest['canonical_model_sha256']
assert sha(ROOT/'regions/LME/LME_028/LME_028.xlsx') == manifest['snapshot_sha256']
# Load exact archived bytes directly. The current adapter intentionally refuses historical
# scientific bodies that differ from today's engine. This experiment replays the old engine,
# not an upgrade or a claim of compatibility with today's scientific implementation.
paths = mc._engine_paths(flags,MODEL/'model.json')
calcpath = mc._calculation_engine_path(flags,MODEL/'model.json')
data_mod=mc._isolated_module(paths['ModelData.py'],'_shark_data',{})
utils_mod=mc._isolated_module(paths['utils.py'],'_shark_utils',{})
deps={'ModelData':data_mod,'utils':utils_mod}
loader_mod=mc._isolated_module(paths['PPRCalculator.py'],'_shark_loader',deps)
calc_mod=mc._isolated_module(calcpath,'_shark_calculation',deps)
constructor={k:v for k,v in flags['constructor'].items() if k not in ('use_ee_floor','ee_floor')}
with warnings.catch_warnings(record=True) as notices:
    warnings.simplefilter('always')
    source=data_mod.ModelData(str(MODEL/'model.json'))
    base=loader_mod.PPRCalculator.from_modeldata(source,**constructor)
    base.__class__=calc_mod.PPRCalculator
    base._initialization_settings=copy.deepcopy(flags['constructor'])
    base.apply_ee_floor(True,.1)
base.__dict__.pop('balanced_model',None) # Never substitute a rebalanced model in this experiment.
focal=next(s for s,n in base.seq2name.items() if n=='Sélaciens L prof')
removed=float(base._DC.loc[focal,focal]); rowsum=float(base._DC.loc[focal].sum())
history=ROOT/'regions/LME/LME_028/work/2026-10-16_202757_trophic_aggregation/outputs/decomposition.json'
decomp=read(history); groups=[g for g in decomp['groups'] if g['unit_id']=='LME_028']
assert decomp['sources_sha256']['regions\\LME\\LME_028\\LME_028.xlsx']==manifest['snapshot_sha256']
catch={g['group']:g['catch_tonnes'] for g in groups}
classic=sum(g['catch_tonnes']*g['saved_group_classic_sppr'] for g in groups)/9
save(RUN/'inputs/catch_and_benchmark.json',{'year':2019,'basis':'landings plus discards','treatment':'unidentified method; historical exclusions Oiseaux/Dauphins/Baleines; fixed original allocations','source':rel(history),'source_sha256':sha(history),'groups':groups,'classic_tC':classic,'catch_tonnes':sum(catch.values())})
settings={'TE_option':None,'short':False,'flat':False,'return_sppr':True,**flags['diagnostics'],
          'DET_TE_vals':1.,'fix_EE_0_cases':True,'thresholds':calc_mod.DEFAULT_DIAGNOSTIC_THRESHOLDS}
save(RUN/'inputs/provenance.json',{'timestamp_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'canonical_model_sha256':sha(MODEL/'model.json'),'flags':flags,'engine_files':{rel(p):sha(p) for p in [paths['ModelData.py'],paths['PPRCalculator.py'],paths['utils.py'],calcpath]},'adapter_serializer_sha256':sha(Path(mc.__file__)),'load_warnings':[str(w.message) for w in notices],'focal_seq':focal,'focal_name':base.seq2name[focal],'removed_share':removed,'initial_row_sum':rowsum,'method_settings':settings,'interpretation':'Fixed-rate diet intervention after audited normalization and EE floor. Preserve p, q, EE, M0, catch, growth, migration, detritus fate; update predation from changed diet. No BA repair, automatic diet normalization, or Ecopath rebalance. Full network solve for every group. Canonical and map read-only.'})
print('Loaded',focal,base.seq2name[focal],'removed',removed,'EE floor',base.ee_floor_info,flush=True)
summaries=[]; coefficients=[]; negatives=[]; checks={}; failures=[]
for scenario in ('baseline','zero_unredistributed','zero_redistributed'):
    model=copy.deepcopy(base)
    if scenario!='baseline':
        model._DC.loc[focal,focal]=0.
        if scenario=='zero_redistributed': model._DC.loc[focal]*=rowsum/model._DC.loc[focal].sum()
        model.predation=model.get_Z(DET_as_PP=True).sum(axis=0).reindex(model.predation.index)
        model._groups_df['predation']=model.predation
        model.is_balanced=model.is_model_balanced()[0]
    for attr in ('p','q','EE','M0','catch','growth','net_migration','egestion','_det_fate'):
        assert getattr(model,attr).equals(getattr(base,attr)),attr
    assert model.use_ee_floor and model.ee_floor==.1
    changed=model._DC.ne(base._DC)
    assert not changed.drop(index=focal).any().any()
    if scenario=='zero_unredistributed': assert changed.sum().sum()==1
    if scenario=='zero_redistributed': np.testing.assert_allclose(model._DC.loc[focal].sum(),rowsum,rtol=0,atol=1e-14)
    save(RUN/f'outputs/{scenario}_runtime.json.gz',mc._runtime(model))
    save(RUN/f'outputs/{scenario}_diet_changes.json',{'row_sum':model._DC.loc[focal].sum(),'cells':[{'predator_seq':int(i),'prey_seq':int(j),'prey_name':model.seq2name[j],'before':base._DC.loc[i,j],'after':model._DC.loc[i,j]} for i in changed.index for j in changed.columns if changed.loc[i,j]],'production_residual':model.catch+model.predation+model.growth+model.net_migration+model.M0+model.external_mortality_export-model.p})
    for option in ('TE','GE','With Egestion'):
        start=time.monotonic(); tag=option.replace(' ','_'); kwargs={**settings,'TE_option':option}
        print('Running',scenario,option,flush=True)
        runtime_before=mc._runtime(model)
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always'); result=model.diagnose_sppr(**kwargs)
            report,sppr,A,L=result
            retained=save(RUN/f'outputs/{scenario}_{tag}_full_return.json.gz',{'settings':kwargs,'return':result,'runtime_before':runtime_before,'runtime_after':mc._runtime(model),'warnings':[str(w.message) for w in caught],'elapsed_seconds':time.monotonic()-start})
            assert sppr is not None and sppr.index.is_unique and sppr.columns.is_unique
            assert runtime_before==mc._runtime(model),'Diagnostic changed runtime'
            reopened=retained['return']['items'][1]
            np.testing.assert_equal(np.array(reopened['data'],dtype=float),sppr.values)
            assert np.isfinite(sppr.values).all()
            # Independent numerical linear solve using every consumer and the returned basal anchors.
            living=[s for s in A.index if s not in sppr.columns]
            rhs=A.loc[living,sppr.columns].to_numpy()@sppr.loc[sppr.columns,sppr.columns].to_numpy()
            direct=np.linalg.solve(np.eye(len(living))-A.loc[living,living].to_numpy(),rhs)
            np.testing.assert_allclose(direct,sppr.loc[living].to_numpy(),rtol=1e-9,atol=1e-8)
            maxrel=float(np.max(np.abs(direct-sppr.loc[living].to_numpy())/np.maximum(1,np.abs(sppr.loc[living].to_numpy()))))
            scopes={}
            for scope in ('all','inner','PP'):
                omit=set() if scope=='all' else set(model.get_Import_seq())
                if scope=='PP': omit.update(model.get_DET_seq())
                cols=[c for c in sppr.columns if c not in omit]
                values=sppr[cols].sum(axis=1)
                scopes[scope]=values
                for seq,value in values.items(): coefficients.append({'scenario':scenario,'option':option,'scope':scope,'seq':int(seq),'group':model.seq2name[seq],'sppr':float(value)})
                np.testing.assert_allclose(np.array(reopened['data'])[:,[sppr.columns.get_loc(c) for c in cols]].sum(axis=1),values,rtol=1e-12,atol=1e-12)
            if scenario=='baseline':
                method={'TE':'new_TE_EEfix','GE':'new_GE','With Egestion':'new_WithEgestion'}[option]
                old=read(MODEL/f'results/diagnostics/method_coverage/{method}.ee_floor_reused.json.gz')
                diffs=[]
                for scope,vals in scopes.items():
                    for seq,v in vals.items():
                        prior=old['scopes'][scope][model.seq2name[seq]]
                        np.testing.assert_allclose(v,prior,rtol=1e-10,atol=1e-8)
                        diffs.append(abs(v-prior)/max(1,abs(prior)))
                checks[f'{option}_saved_baseline_reproduced']=True
                print('Baseline max relative error',max(diffs),flush=True)
            for i,j in np.argwhere(sppr.values < -1e-10): negatives.append({'scenario':scenario,'option':option,'recipient_seq':int(sppr.index[i]),'recipient_name':model.seq2name[sppr.index[i]],'source_seq':int(sppr.columns[j]),'source_name':model.seq2name[sppr.columns[j]],'value':sppr.iloc[i,j],'tolerance':1e-10})
            totals={scope:sum(c*values.loc[model.name2seq[name]] for name,c in catch.items())/9 for scope,values in scopes.items()}
            focal_ppr=catch[model.seq2name[focal]]*scopes['inner'].loc[focal]/9
            summaries.append({'scenario':scenario,'option':option,'diet_row_sum':model._DC.loc[focal].sum(),'self_share':model._DC.loc[focal,focal],'focal_sppr_inner':scopes['inner'].loc[focal],'regional_ppr_tC':totals,'inner_ratio_to_fixed_classic':totals['inner']/classic,'focal_share_inner':focal_ppr/totals['inner'],'focal_catch_tonnes':catch[model.seq2name[focal]],'A_ii':A.loc[focal,focal],'diagnostic':report,'independent_solve_max_relative_error':maxrel,'floor':model.ee_floor_info})
            checks[f'{scenario}_{tag}_matrices_scopes_and_full_solve_verified']=True
            print('Done',scenario,option,'inner tC',totals['inner'],'status',report['status'],flush=True)
        except Exception:
            failures.append({'scenario':scenario,'option':option,'traceback':traceback.format_exc()}); print(failures[-1]['traceback'],flush=True)
save(RUN/'outputs/coefficients.json',coefficients)
save(RUN/'outputs/negative_entries.json',negatives)
for row in summaries:
    b=next(r for r in summaries if r['scenario']=='baseline' and r['option']==row['option'])
    row['inner_change_percent']=100*(row['regional_ppr_tC']['inner']/b['regional_ppr_tC']['inner']-1)
save(RUN/'outputs/comparison.json',{'fixed_classic_tC':classic,'summaries':summaries,'failures':failures})
after={rel(p):sha(p) for p in protected}
checks['all_protected_files_unchanged']=before==after
checks['all_nine_runs_completed']=len(summaries)==9 and not failures
save(RUN/'qa/checks.json',{'checks':checks,'failures':failures,'protected_file_count':len(protected),'changed_files':[p for p in before if before[p]!=after[p]]})
print(json.dumps({'checks':checks,'failures':failures},indent=2),flush=True)
assert all(checks.values()) and not failures
