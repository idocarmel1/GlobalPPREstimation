"""Isolated sensitivity probe; never changes canonical inputs or production outputs.

The explicit external sink is hypothetical mortality/export, not catch, migration,
or observed biomass accumulation. Routing-only TE is an algorithm sensitivity:
the existing zero-EE re-credit assumes all mortality is returned internally, so
its output is not an independently validated spatial mortality formulation.
"""
from pathlib import Path
import argparse, copy, gzip, hashlib, inspect, json, sys, time, traceback, warnings
import numpy as np
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
sys.path.insert(0, str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records
from tools.scientific_helpers.sppr.method_coverage import (
    _constructor, _load, _runtime, encode_lossless, engine_identity, method_settings)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(p, x, typed=False):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = encode_lossless(x) if typed else x
    txt = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False,
                     default=lambda v: v.item() if isinstance(v, np.generic) else str(v))
    if p.suffix == '.gz':
        with gzip.open(p, 'wt', encoding='utf-8') as f: f.write(txt)
    else: p.write_text(txt, encoding='utf-8')

def fit(c, living, consumers_only=False):
    pp = set(c.get_PP_seq())
    train = [s for s in living if c.EE[s] > .1 and (not consumers_only or s not in pp)]
    x, y = c.TL.loc[train].to_numpy(), c.EE.loc[train].to_numpy()
    if len(train) < 3 or np.ptp(x) == 0:
        return {'available': False, 'reason': 'insufficient varying trophic levels'}
    slope, intercept = np.polyfit(x, y, 1)
    prediction = intercept + slope * x
    r2 = 1 - float(np.sum((y - prediction)**2) / np.sum((y - y.mean())**2))
    low = [s for s in living if c.EE[s] <= .1]
    targets = {int(s): float(intercept + slope * c.TL[s]) for s in low}
    loo = []
    for k in range(len(train)):
        keep = np.arange(len(train)) != k
        b, a = np.polyfit(x[keep], y[keep], 1)
        loo.append(float(a + b*x[k]))
    loo_rmse = float(np.sqrt(np.mean((y - np.asarray(loo))**2)))
    return {'available': True, 'n': len(train), 'training_group_ids': list(map(int, train)),
            'intercept': float(intercept), 'slope': float(slope), 'r_squared': r2,
            'leave_one_out_rmse': loo_rmse, 'tl_min': float(x.min()), 'tl_max': float(x.max()),
            'target_predictions': targets, 'consumers_only': consumers_only,
            'selection': 'EE > 0.1; synthetic imports and detritus/nonfeeding pools excluded',
            'caution': 'Truncated-response calibration; low-EE targets have no observed prediction validation.'}

def decode_frame(x):
    assert x['type'] == 'dataframe'
    def cell(v):
        if isinstance(v, dict) and v.get('type') == 'float':
            return {'nan':np.nan,'positive_infinity':np.inf,'negative_infinity':-np.inf}[v['value']]
        return v
    return pd.DataFrame([[cell(v) for v in row] for row in x['data']],
                        index=x['index'], columns=x['columns'])

def scenario(base, living, export, update_ee):
    c = copy.deepcopy(base)
    export = export.reindex(c.p.index).fillna(0)
    internal_m0 = base.M0 - export
    if (export < -1e-12).any() or (internal_m0 < -1e-12).any():
        raise ValueError('Hypothetical external sink must be between zero and original M0')
    c.M0 = internal_m0
    if update_ee:
        c.EE.loc[living] = 1 - c.M0.loc[living] / c.p.loc[living]
    # Only the actual internal mortality supply changes. Egestion is retained.
    fate = c._det_fate.reindex(index=c.p.index).fillna(0)
    supply = c.M0 + c.egestion
    for s in c.get_DET_seq():
        inflow = float((supply * fate[s]).sum()) if s in fate else float(supply.sum())
        c.q[s] = c.p[s] = inflow
        c.growth[s] = inflow - c.predation[s] - c.net_migration[s]
    c._groups_df['M0'] = c.M0
    c._groups_df['ee'] = c.EE
    c._groups_df['p'] = c.p
    c._groups_df['q'] = c.q
    c._groups_df['biomass_accum'] = c.growth
    c._groups_df['flow_to_det'] = c.M0 + c.egestion
    c._groups_df['hypothetical_external_mortality'] = export
    # Living closure includes the separate external sink; no BA/migration proxy.
    lhs = c.catch + c.predation + c.growth + c.net_migration + c.M0 + export
    residual = lhs - c.p
    original_residual = base.catch + base.predation + base.growth + base.net_migration + base.M0 - base.p
    assert np.allclose(residual.loc[living], original_residual.loc[living], atol=1e-10, rtol=1e-10)
    for attr in ['catch', 'predation', 'egestion', 'respiration', 'immigration', 'emigration', 'net_migration']:
        assert getattr(c, attr).equals(getattr(base, attr)), attr
    assert c.growth.loc[living].equals(base.growth.loc[living])
    assert c.p.loc[living].equals(base.p.loc[living])
    assert c.q.loc[living].equals(base.q.loc[living])
    assert c._DC.equals(base._DC) and c._det_fate.equals(base._det_fate)
    return c, export

def group_catch(work, config, base):
    model = ROOT / config['model_path']
    snapshot = read_book(model.parent / 'results/regional_snapshot.xlsx', sheets=['PPR'])
    region = work.parents[1]
    book = read_book(region / (region.name + '.xlsx'), sheets=['Catch'])
    catches = {r['taxon']: r.get(2019) for r in records(book, 'Catch', 'Catch')
               if r.get('catch_basis') == 'landings'}
    out = pd.Series(0., index=base.p.index)
    missing = []
    for row in records(snapshot, 'PPR', 'Matching'):
        if row.get('model_id') != config['model_id']: continue
        amount = catches.get(row.get('taxon'))
        name, weight = row.get('group'), row.get('weight')
        if amount is None or not name or weight is None:
            missing.append(row.get('taxon')); continue
        if name not in base.name2seq: raise ValueError('Saved mapping has unknown group: '+name)
        out[base.name2seq[name]] += float(amount) * float(weight)
    return out, sorted(set(missing))

def recycling_metrics(c, A, matrix, option):
    idx = list(A.index)
    a = A.reindex(index=idx, columns=idx).to_numpy(dtype=float)
    basal = [i for i in range(len(idx)) if np.array_equal(a[i],np.eye(len(idx))[i])]
    consumers = [i for i in range(len(idx)) if i not in basal]
    acc = a[np.ix_(consumers,consumers)]
    raw = np.zeros((len(idx),len(basal)))
    raw[basal,:] = np.eye(len(basal))
    raw[consumers,:] = np.linalg.solve(np.eye(len(consumers))-acc,a[np.ix_(consumers,basal)])
    basis = pd.DataFrame(raw,index=idx,columns=[idx[i] for i in basal])
    other = [s for s in basis.columns if s not in c.get_DET_seq()]
    error=float(np.max(np.abs(basis[other].to_numpy()-matrix.reindex(index=idx,columns=other).to_numpy())))
    assert np.allclose(basis[other],matrix.reindex(index=idx,columns=other),rtol=1e-9,atol=1e-8)
    rho=float(max(abs(np.linalg.eigvals(acc)))) if acc.size else 0.
    result={'rho_living':rho,'unscaled_basis_reconciliation_max_absolute_error':error}
    if option!='TE':
        dc=c.get_DC(DET_as_PP=True,normalize=False)
        B,cv=c._build_det_BC(basis,basis[other].sum(axis=1),c.get_DET_seq(),dc,option)
        result.update(unpooled_detritus_recycling_radius=float(max(abs(np.linalg.eigvals(B)))) if B.size else 0.)
        try:
            _,factor,ap,bp=c._collapse_det_scaling(basis.copy(),c.get_DET_seq(),basis[other].sum(axis=1),
                c.M0,c.egestion,c.q,c.M0+c.egestion,dc,option,det_fate=c._det_fate)
            result.update(pooled_recycling_b=float(bp),pooled_source_a=float(ap),pooled_multiplier=float(factor))
        except ValueError as exc: result['pooled_recycling_failure']=str(exc)
    else:
        result['detritus_recycling_matrix']='TE uses direct basal inflow scaling; no explicit B recycling matrix'
    return result

def metrics(c, matrix, export, catch, A, option):
    sppr = matrix.sum(axis=1).reindex(c.p.index).fillna(0)
    basal = c.get_PP_seq() + c.get_Import_seq()
    inflow = float(c.p.loc[basal].sum())
    outflow_existing = float(((c.catch + c.growth + c.net_migration) * sppr).sum())
    explicit_sink_pp = float((export * sppr).sum())
    outflow = outflow_existing + explicit_sink_pp
    gap = (outflow-inflow)/inflow if inflow else None
    det = c.get_DET_seq()
    return {'pp_inflow': inflow, 'pp_outflow_existing_sinks': outflow_existing,
            'recycling':recycling_metrics(c,A,matrix,option),
            'hypothetical_external_sink_pp': explicit_sink_pp, 'pp_outflow_with_external_sink': outflow,
            'relative_pp_budget_gap_with_external_sink': gap,
            'strict_pp_budget_balanced_with_external_sink': bool(np.isclose(inflow, outflow)),
            'negative_source_entries': int((matrix.to_numpy() < -1e-10).sum()),
            'finite_coefficients': bool(np.isfinite(matrix.to_numpy()).all()),
            'landings_2019_ppr_tC': float((catch * sppr).sum()/9),
            'represented_landings_2019_tonnes': float(catch.sum()),
            'detritus_growth_residual': {str(s): float(c.growth[s]) for s in det},
            'detritus_growth_negative': [int(s) for s in det if c.growth[s] < -1e-10],
            'detritus_sppr': {str(s): float(sppr[s]) for s in det},
            'hypothetical_external_sink_flow': float(export.sum())}

def run(work):
    started = time.time()
    config = json.loads((work/'inputs/configuration.json').read_text(encoding='utf-8'))
    model = ROOT / config['model_path']; flags = config['flags']
    c, source_state, loading_warnings = _load(model, _constructor(flags, model), flags)
    frozen_runtime = _runtime(c)
    save(work/'outputs/source_and_runtime.json.gz', {'source': source_state, 'runtime': frozen_runtime})
    living = [s for s in c.p.index if s not in c.get_DET_seq()+c.get_Import_seq() and c.p[s]>0]
    low = [s for s in living if c.EE[s] <= .1]
    fits = {'all_living': fit(c, living), 'consumers_only': fit(c, living, True)}
    save(work/'outputs/regressions.json', fits)
    catch, missing_catch = group_catch(work, config, c)
    zero = pd.Series(0., index=c.p.index)
    specs = [('baseline', zero, False)]
    for fit_name in fits:
        fitted = fits[fit_name]
        if not fitted.get('available'): continue
        ext = zero.copy()
        for s, value in fitted['target_predictions'].items():
            if not float(c.EE[s]) <= value <= 1:
                raise ValueError(f'{fit_name}: inadmissible prediction {s}={value}; no silent clipping')
            ext[s] = c.p[s]*(value-c.EE[s])
        specs.append(('predicted_ee_'+fit_name, ext, True))
        if fit_name == 'all_living': specs.append(('routing_only_matched', ext, False))
    for fraction in [.5, 1.]:
        ext = zero.copy(); ext.loc[low] = fraction*c.M0.loc[low]
        specs.append((f'routing_only_{int(100*fraction)}pct', ext, False))
    if config['unit_id'] == 'LME_013':
        for label, ids in [('birds_pinnipeds', [31,32]), ('jellyfish', [7])]:
            ext = zero.copy(); ext.loc[ids] = c.M0.loc[ids]
            specs.append(('routing_only_100pct_'+label, ext, False))
    group_rows=[]; result_rows=[]; baseline={}
    for label, export, ee_updated in specs:
        current, external = scenario(c, living, export, ee_updated)
        for option, key in [('GE','new_GE'),('TE','new_TE_EEfix'),('With Egestion','new_WithEgestion')]:
            print(config['unit_id'],label,option,flush=True)
            settings = method_settings(key, flags, model)
            solver_keys = inspect.signature(current.SPPR_new).parameters
            kwargs = {k:v for k,v in settings['kwargs'].items() if k in solver_keys}
            if label.startswith('routing_only') and option=='TE':
                # Keep the original efficiency matrix to isolate changed internal supply.
                kwargs['TE'] = c.get_TE('TE', DET_values=kwargs.get('DET_TE_vals',1))
            output = work/'outputs'/label/option.replace(' ','_')
            try:
                with warnings.catch_warnings(record=True) as ws:
                    warnings.simplefilter('always')
                    if label == 'baseline':
                        diagnostic, matrix, A, L = current.diagnose_sppr(**settings['kwargs'])
                        save(output/'direct_diagnostic.json.gz', diagnostic, typed=True)
                    else:
                        # Reuse successful matrices from the first wrapper pass only
                        # after exact source/runtime and solver identity checks.
                        cache = output/'full_return.json.gz'
                        runtime_cache = output/'runtime.json.gz'
                        if cache.is_file() and runtime_cache.is_file():
                            with gzip.open(runtime_cache,'rt',encoding='utf-8') as f:
                                cached_runtime=json.load(f)
                            assert cached_runtime == _runtime(current), 'Cached scenario runtime differs'
                            with gzip.open(cache,'rt',encoding='utf-8') as f: previous=json.load(f)
                            matrix,A,L=(decode_frame(previous[k]) for k in ['SPPR','A','L'])
                            # Recovery cache does not retain emitted warning strings
                            # or transient detritus_resolution_info; these are explicit.
                            current.detritus_resolution_info = {'availability':'not retained in first wrapper pass',
                                'source_matrix_reused':True}
                        else:
                            matrix,A,L = current.SPPR_new(**kwargs)
                        diagnostic=None
                if matrix is None: raise ValueError('Solver returned no source matrix')
                save(output/'full_return.json.gz', {'SPPR':matrix,'A':A,'L':L}, typed=True)
                save(output/'runtime.json.gz', _runtime(current))
                m = metrics(current, matrix, external, catch,A,option)
                m.update(scenario=label,method=option,status='computed_sensitivity',
                         detritus_resolution=copy.deepcopy(getattr(current,'detritus_resolution_info',None)),
                         warnings=[str(w.message) for w in ws], ee_updated=ee_updated,
                         routing_only_te_limitation=(label.startswith('routing_only') and option=='TE'),
                         full_diagnostics_available=(diagnostic is not None))
                save(output/'metrics.json', m)
                if (output/'failure.json').exists(): (output/'failure.json').unlink()
                sums = matrix.sum(axis=1)
                if label=='baseline':baseline[option]=sums
                for s in c.p.index:
                    v = float(sums.get(s,0)); original=float(baseline[option].get(s,0))
                    group_rows.append({'scenario':label,'method':option,'seq':int(s),'group':c.seq2name[s],
                                       'source_EE':float(c.EE[s]),'scenario_EE':float(current.EE[s]),
                                       'source_M0':float(c.M0[s]),'internal_M0':float(current.M0[s]),
                                       'external_sink':float(external[s]),'TL':float(c.TL[s]),
                                       'sppr_all':v,'baseline_sppr_all':original,
                                       'relative_change':(v-original)/original if original else None,
                                       'landings_2019':float(catch[s])})
                result_rows.append(m)
            except Exception as exc:
                failure={'scenario':label,'method':option,'status':'failed','reason':str(exc),
                         'traceback':traceback.format_exc()}
                save(output/'failure.json',failure);result_rows.append(failure)
        assert _runtime(c) == frozen_runtime, 'Baseline object changed'
    pd.DataFrame(group_rows).to_csv(work/'outputs/group_comparison.csv',index=False,encoding='utf-8',float_format='%.17g')
    save(work/'outputs/scenario_summary.json',result_rows)
    unchanged={name:sha(ROOT/name)==value for name,value in config['protected_hashes'].items()}
    save(work/'qa/protected_inputs.json',unchanged)
    save(work/'outputs/run_manifest.json',{'run_id':config['run_id'],'unit_id':config['unit_id'],
         'model_id':config['model_id'],'source_sha256':sha(model),'flags':flags,
         'engine_identity':engine_identity(flags,model),'experiment_code_sha256':sha(__file__),
         'low_ee_group_ids':list(map(int,low)),'loading_warnings':loading_warnings,
         'missing_landings_or_mapping_taxa':missing_catch,'elapsed_seconds':time.time()-started,
         'protected_inputs_unchanged':all(unchanged.values()),'adoption':'none',
         'PPR_basis':'2019 landings, current regional catch and saved model mapping, all biological groups; tC = wet PPR / 9',
         'detritus_closure':'Living flows fixed. Detritus stock residual changes; negative stock residuals are reported, never treated as evidenced supply.'})
    assert all(row['status']=='computed_sensitivity' for row in result_rows), 'One or more requested scenarios failed'
    assert all(unchanged.values()), 'Protected scientific/project input changed during experiment'
    print('COMPLETE',config['unit_id'],round(time.time()-started,2),flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser();p.add_argument('work');args=p.parse_args()
    run((ROOT/args.work).resolve())
