"""Unadopted M0-only routing sensitivity; preserve living biology and source inputs."""
from pathlib import Path
import copy, gzip, hashlib, json, math, os, sys, warnings
from datetime import datetime, timezone

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
RUN = Path(__file__).resolve().parent.parent
MODEL = RUN.parent.parent.parent
BASE = RUN.parent / 'ee_floor_seabird_accounting_20261114'
ENGINE = BASE / 'code/engine'
OUT = RUN / 'outputs'
OUT.mkdir(parents=True, exist_ok=True)
sys.path[:0] = [str(ENGINE), str(ROOT / 'research/agents/regional_ge_integration_20260928/evidence'), str(ROOT)]
import numpy as np
import pandas as pd
from PPRCalculator import PPRCalculator
from runtime_codec import encode, decode
from tools.project_core.workbooks.workbooks import read_book, records, overview

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

class MortalityOnlyRouting(PPRCalculator):
    """Separate mortality destination without changing the TE mortality definition.

    The production engine has one fate for M0 AND egestion; its fate row cannot
    express this experiment. These local overrides change only routed mortality
    and its budget sink. This subclass is not an adopted engine modification.
    """
    def _build_det_BC(self, *args, **kwargs):
        original = self.M0
        try:
            self.M0 = original.copy()
            self.M0.loc[2] -= self.whale_m0_diverted
            return super()._build_det_BC(*args, **kwargs)
        finally:
            self.M0 = original

    def get_Z(self, DET_as_PP=False):
        z = super().get_Z(DET_as_PP=DET_as_PP)
        if not DET_as_PP:
            z.loc[39, 2] -= self.whale_m0_diverted
        return z

    def _sppr_unrouted_export(self, sppr, TE_option, diet_sppr=None):
        out = super()._sppr_unrouted_export(sppr, TE_option, diet_sppr)
        # TE already charges consumer mortality through (P-M0)/Q.
        if TE_option in ('GE', 'With Egestion'):
            out.loc[2] += self.whale_m0_diverted * sppr.loc[2]
        return out

raw_state = BASE / 'outputs/initial_runtime.json.gz'
state = decode(json.loads(gzip.decompress(raw_state.read_bytes())))
base = PPRCalculator.__new__(PPRCalculator)
base.__dict__.update(state)
assert base.get_DET_seq() == [39]
assert base._det_fate.loc[2, 39] == 1
assert base.EE.loc[2] == .1
assert all(base.get_TE('TE', as_matrix=False).loc[base.get_Regular_seq()] > 0)
protected = [ROOT / 'Project.xlsx', ROOT / 'regions/LME/LME_049/LME_049.xlsx', MODEL / 'model.json',
             MODEL / 'model_notes.md', MODEL / 'model_validation/validation.docx', MODEL / 'model_validation/taxon_mapping.xlsx']
protected += [p for p in (ROOT / 'interactive_map').rglob('*') if p.is_file()]
before = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
save('protected_before.json', before)
book = read_book(ROOT / 'regions/LME/LME_049/LME_049.xlsx', sheets=['Overview', 'Catch', 'PPR'])
assert overview(book)['selected_model_id'] == MODEL.name
mapping = {}
mapping_rows = list(records(book, 'PPR', 'Matching'))
for row in mapping_rows:
    assert row['model_id'] == MODEL.name
    mapping.setdefault(row['taxon'], []).append((base.name2seq[row['group']], row['weight']))
assert all(math.isclose(math.fsum(w for g,w in v), 1, abs_tol=1e-9) for v in mapping.values())
catch_rows = list(records(book, 'Catch', 'Catch'))
catch = {(r['taxon'], r['catch_basis']): r[2019] for r in catch_rows}
assert all(v is not None and math.isfinite(v) for v in catch.values())
save('arithmetic_inputs.json', {'year':2019, 'scope':'all', 'unidentified':'method', 'mapping':mapping_rows,
     'catch_2019':[{'taxon':t, 'basis':b, 'tonnes':v} for (t,b),v in catch.items()],
     'rule':'Taxon coefficient rounded to 6 decimals before catch multiplication, then wet PPR / 9 once.',
     'direct_whale_mapping_rows':sum(1 for v in mapping.values() for g,w in v if g == 2)})

results = {}
frames = {}
checks = {}
for fraction in (0., 1.):
    scenario = 'baseline' if fraction == 0 else 'M0_export_100pct'
    c = MortalityOnlyRouting.__new__(MortalityOnlyRouting)
    c.__dict__.update(copy.deepcopy(state))
    c.__dict__.pop('balanced_model', None)  # Old cached copy does not represent this routing.
    c.whale_m0_diverted = fraction * float(c.M0.loc[2])
    delta = c.whale_m0_diverted
    for field in ('p', 'q', 'growth'):
        getattr(c, field).loc[39] -= delta
    for col, field in [('p','p'), ('q','q'), ('biomass_accum','growth')]:
        c._groups_df.loc[39,col] = getattr(c,field).loc[39]
    c._groups_df.loc[39,'pb'] = c.p.loc[39] / c._groups_df.loc[39,'biomass']
    c._groups_df.loc[39,'qb'] = c.q.loc[39] / c._groups_df.loc[39,'biomass']
    c.det_export.loc[2] += delta
    c._groups_df.loc[2,'det_export'] = c.det_export.loc[2]
    living = base.get_Regular_seq() + base.get_PP_seq() + base.get_Import_seq()
    for field in ('p','q','growth','M0','egestion','EE','predation','catch','net_migration','external_mortality_export'):
        checks[scenario + '_unchanged_living_' + field] = getattr(c,field).loc[living].equals(getattr(base,field).loc[living])
    checks[scenario + '_unchanged_diets'] = c._DC.equals(base._DC)
    checks[scenario + '_egestion_still_routed'] = np.isclose(c.get_Z().loc[39,2], c.egestion.loc[2] + c.M0.loc[2] - delta)
    assert c.is_model_balanced()[0]
    (OUT/(scenario+'_runtime.json.gz')).write_bytes(gzip.compress(json.dumps(encode(vars(c)),allow_nan=False).encode(),mtime=0))
    results[scenario] = {'whale_TE':float(c.get_TE('TE',as_matrix=False).loc[2]),
                         'M0_export_added':delta, 'whale_M0_to_detritus':float(c.M0.loc[2])-delta,
                         'whale_egestion_to_detritus':float(c.egestion.loc[2]),
                         'detritus_inflow':float(c.q.loc[39]), 'detritus_stock_residual':float(c.growth.loc[39]),
                         'methods':{}}
    for option in ('GE','TE','With Egestion'):
        key = option.replace(' ','_')
        cc = copy.deepcopy(c)
        with warnings.catch_warnings(record=True) as captured:
            ret = cc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
        report,s,a,l = ret
        save(scenario+'_'+key+'_full_return.json',encode(ret))
        save(scenario+'_'+key+'_warnings.json',[str(w.message) for w in captured])
        for name,matrix in [('source_coefficients',s),('A',a),('L',l)]:
            matrix.to_csv(OUT/(scenario+'_'+key+'_'+name+'.csv'),index_label='recipient_id')
        prior = decode(json.loads((BASE/'outputs'/(key+'_full_return.json')).read_text(encoding='utf-8')))
        old = prior[1]
        old_d = float(old.loc[39].sum())
        raw_det = old[39] / old_d
        direct = old.drop(columns=[39]).sum(axis=1)
        old_b = prior[0]['divergence']['b']
        old_q = float(base.q.loc[39])
        if option == 'TE':
            expected_d = old_d * old_q / (old_q-delta)
        else:
            expected_d = (old_q*old_d*(1-old_b)-delta*direct.loc[2]) / (old_q*(1-old_b)-delta*(1-raw_det.loc[2]))
        expected = old.copy()
        expected[39] = raw_det * expected_d
        checks[scenario+'_'+key+'_independent_analytic_match'] = bool(np.allclose(s.loc[expected.index,expected.columns],expected,rtol=1e-11,atol=1e-10))
        checks[scenario+'_'+key+'_living_matrix_unchanged'] = bool(np.array_equal(a.loc[prior[2].index,prior[2].columns],prior[2]))
        checks[scenario+'_'+key+'_finite_nonnegative'] = bool(np.isfinite(s.to_numpy()).all() and (s.to_numpy()>=0).all())
        checks[scenario+'_'+key+'_strict_budget'] = report['balance']['is_balanced']
        checks[scenario+'_'+key+'_strict_model_balance'] = report['model_input']['is_model_balanced']
        total = s.sum(axis=1)
        taxon_s = {t:math.fsum(w*float(total.loc[g]) for g,w in v) for t,v in mapping.items()}
        regional = {}
        for basis in ('landings','catch','discards'):
            vals = [(t,catch[t,basis],taxon_s[t]) for t in sorted(mapping)]
            regional[basis] = {'catch_tonnes':math.fsum(x[1] for x in vals),
                              'PPR_tC':math.fsum(catchv*round(coeff,6) for t,catchv,coeff in vals)/9,
                              'PPR_tC_full_precision':math.fsum(catchv*coeff for t,catchv,coeff in vals)/9}
        results[scenario]['methods'][option] = {'status':report['status'],'balance':report['balance'],
             'near_singular_te':report['divergence']['near_singular_te'], 'rho_living':report['divergence']['rho_living'],
             'b':report['divergence']['b'],'whale_SPPR':float(total.loc[2]),'detritus_SPPR':float(total.loc[39]),
             'regional_2019':regional,'model_catch_PPR':float((base.catch*total).sum())}
        frames[scenario,option] = total
        print(scenario,option,json.dumps(results[scenario]['methods'][option]),flush=True)

comparison = {}
for option in ('GE','TE','With Egestion'):
    b = results['baseline']['methods'][option]
    s = results['M0_export_100pct']['methods'][option]
    comparison[option] = {}
    for basis in ('landings','catch','discards'):
        bv = b['regional_2019'][basis]['PPR_tC']; sv = s['regional_2019'][basis]['PPR_tC']
        comparison[option][basis] = {'baseline_tC':bv,'M0_export_tC':sv,'delta_tC':sv-bv,'percent_change':100*(sv/bv-1)}
    pd.DataFrame({'baseline':frames['baseline',option], 'M0_export':frames['M0_export_100pct',option],
                  'difference':frames['M0_export_100pct',option]-frames['baseline',option]}).to_csv(OUT/(option.replace(' ','_')+'_coefficient_comparison.csv'))
save('summary.json',{'source_configuration':'EE floor 0.1; seabird M0 and egestion exported; finalized missing-BA closure',
     'assumption':'Only destination of remaining toothed-whale M0 changes. Whale EE, M0 magnitude and TE are held fixed. Egestion remains in detritus.',
     'results':results,'regional_comparison':comparison,'adopted':False,'review_artifacts_changed':False})
checks['all_protected_files_unchanged'] = all(sha(ROOT/p)==h for p,h in before.items())
checks['source_runtime_unchanged'] = encode(vars(base)) == encode(state)
save('verification.json', {'checks':{k:bool(v) for k,v in checks.items()}, 'passed':all(checks.values())})
assert all(checks.values()),[k for k,v in checks.items() if not v]
save('settings.json', {'timestamp_utc':datetime.now(timezone.utc).isoformat(),'model_id':MODEL.name,
     'canonical_sha256':sha(MODEL/'model.json'),'initial_runtime_sha256':sha(raw_state),
     'engine_hashes':{p.name:sha(p) for p in ENGINE.glob('*.py')}, 'methods':['GE','TE','With Egestion'],
     'mortality_export_fractions':[0,1], 'no_constructor_rerun':True, 'no_monte_carlo':True,
     'implementation':'Experiment-local subclass separates mortality from egestion routing; production engine unchanged. Replay runtime snapshots with this subclass and whale_m0_diverted, not the base class alone.',
     'units':'Model flow units retained; regional PPR converted to tC/year by division by nine once.'})
paths = [p for p in OUT.glob('*') if p.name not in ('evidence_index.json','handoff_check.json')] + [Path(__file__),raw_state,MODEL/'model.json'] + list(ENGINE.glob('*.py'))
save('evidence_index.json', {'schema_version':1,'run_id':'2026-11-14_toothed_whale_M0_export_sensitivity',
     'region_id':'LME_049','model_id':MODEL.name,'variant_id':'M0_only_export_EE_fixed',
     'methods':['GE','TE','With Egestion'],
     'source_identity':sha(MODEL/'model.json'),'computational_input_identity':sha(raw_state),
     'required_roles':['diagnostic return and matrices','provenance and reproduction'],
     'reconciliation':{'independent_analytical_solution':True,'strict_balance_all_methods':True,'canonical_and_review_files_unchanged':True},
     'artifacts':[{'path':os.path.relpath(p,OUT).replace('\\','/'),'sha256':sha(p),'availability':'present',
                  'role':'diagnostic return and matrices' if p.parent==OUT else 'provenance and reproduction'} for p in paths],
     'adopted':False})
print('VERIFIED',json.dumps(comparison),flush=True)
