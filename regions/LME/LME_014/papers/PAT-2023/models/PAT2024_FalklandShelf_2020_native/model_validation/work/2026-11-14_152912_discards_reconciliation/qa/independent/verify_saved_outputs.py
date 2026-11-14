"""Independent saved-array arithmetic only. Never imports an Ecopath engine."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json
import math
import numpy as np

QA = Path(__file__).resolve().parent
RUN = QA.parents[1]
MODEL = RUN.parents[2]
ROOT = next(p for p in RUN.parents if (p / 'Project.xlsx').exists())
OUT = RUN / 'outputs'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def frame(obj):
    if 'dataframe' in obj:
        obj = obj['dataframe']
    return obj['frame'] if obj.get('type') == 'series' else obj

def numbers(obj):
    z = frame(obj)
    values = np.array(z['data'], dtype=float)
    assert values.shape == tuple(z['shape'])
    assert len(z['index']) == len(set(z['index']))
    assert len(z['columns']) == len(set(z['columns']))
    for maskname, mask in z.get('masks', {}).items():
        assert np.array(mask).shape == values.shape
        assert not np.any(mask), f'Unexpected nonfinite mask: {maskname}'
    assert np.isfinite(values).all()
    return z['index'], z['columns'], values

def vector(obj):
    idx, _, val = numbers(obj)
    assert val.shape[1] == 1
    return dict(zip(idx, val[:, 0]))

def close(a, b, atol=1e-12, rtol=1e-12):
    assert math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol), (a,b)

source = read(OUT / 'source/source_fisheries_ledger.json')
raw = read(OUT / 'source/native_readonly_tables.json')['tables']
returns = read(OUT / 'diagnostics/source_return_matrix.json')
groups = {g['GroupID']: g for g in raw['EcopathGroup']}
assert len(groups) == 36
assert groups[45]['Sequence'] == 35 and groups[45]['GroupName'] == 'Discards'
assert groups[1]['Sequence'] == 36 and groups[1]['GroupName'] == 'Detritus'
fleets = {r['FleetID'] for r in raw['EcopathFleet']}
assert fleets == {1,2}
keycounts = Counter((r['GroupID'], r['FleetID']) for r in raw['EcopathCatch'])
assert len(keycounts) == 72 and set(keycounts.values()) == {1}
assert set(keycounts) == {(g,f) for g in groups for f in fleets}
fates = {(r['FleetID'],r['GroupID']):r['DiscardFate'] for r in raw['EcopathDiscardFate']}
assert len(fates) == 4
landings = defaultdict(float)
discards = defaultdict(float)
expected = defaultdict(float)
for row in raw['EcopathCatch']:
    seq = groups[row['GroupID']]['Sequence']
    assert row['Landing'] >= 0 and row['Discards'] >= 0
    assert row['DiscardMortality'] == 1
    landings[seq] += row['Landing']
    discards[seq] += row['Discards']
    for recipient_id in [45,1]:
        recipient_seq = groups[recipient_id]['Sequence']
        expected[(seq,recipient_seq)] += row['Discards']*row['DiscardMortality']*fates[(row['FleetID'],recipient_id)]
for fleet in fleets:
    close(sum(v for (f,g),v in fates.items() if f==fleet),1)
    assert fates[(fleet,45)] == 0 and fates[(fleet,1)] == 1
idx, cols, arr = numbers(returns['matrix'])
assert set(idx) == set(range(1,38)) and cols == [36,35]
for ri,seq in enumerate(idx):
    for ci,recipient in enumerate(cols):
        close(arr[ri,ci],expected[(seq,recipient)],atol=0,rtol=0)
for seq,val in vector(returns['landings']).items():
    close(val,landings[seq],atol=0,rtol=0)
for seq,val in vector(returns['discards']).items():
    close(val,discards[seq],atol=0,rtol=0)
close(arr.sum(),sum(discards.values()))
assert sha(OUT/'source/source_fisheries_ledger.json') == returns['source_ledger_sha256']
source_hashes = {name: sha(ROOT/name)==h for name,h in source['source_hashes'].items()}
assert all(source_hashes.values()), source_hashes
baseline = read(MODEL/'model_validation/evidence/ee_floor_on_review/initialization_and_floor.json')['completed_before_floor']
prior_effective = read(MODEL/'model_validation/evidence/ee_floor_on_review/initialization_and_floor.json')['effective_after_floor']
catch = vector(baseline['catch'])
for seq,val in catch.items():
    close(val,landings[seq]+discards[seq])
dc = baseline['_DC']
consumption = vector(baseline['q'])
discards_col = dc['columns'].index(35)
demands = {seq: consumption[seq]*row[discards_col] for seq,row in zip(dc['index'],dc['data']) if row[discards_col] > 0}
close(sum(demands.values()),source['totals']['discards_accepted_completed_demand'])
close(groups[45]['Export']+sum(demands.values()),3.2644914549351256e-10,atol=1e-16)

result = {
    'scope':'Independent source-key reconstruction and saved-array arithmetic; no engine import or solver execution.',
    'source_hashes_match': source_hashes,
    'all_72_native_group_fleet_rows_present_once':True,
    'native_return_matrix_reconstructed_exactly':True,
    'total_landings':sum(landings.values()),
    'total_discards_and_returns':sum(discards.values()),
    'recipient_35_return':float(arr[:,cols.index(35)].sum()),
    'recipient_36_return':float(arr[:,cols.index(36)].sum()),
    'all_donor_catch_equals_landings_plus_discards':True,
    'discard_demand_by_recipient':demands,
    'total_Discard_35_consumption':sum(demands.values()),
    'stored_native_Export35':groups[45]['Export'],
    'native_Export35_plus_accepted_demand':groups[45]['Export']+sum(demands.values()),
    'source_file_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [OUT/'source/source_fisheries_ledger.json',OUT/'source/native_readonly_tables.json',OUT/'diagnostics/source_return_matrix.json']},
}
(QA/'source_arithmetic_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['source_hashes_match','source_file_hashes']},ensure_ascii=False,indent=2))

# Independently reopen the finished diagnostic package. No calculator is imported.
DIAG = OUT/'diagnostics'
prov = read(DIAG/'run_provenance.json')
assert sha(MODEL/'model.json') == prov['canonical_model_sha256']
assert sha((DIAG/prov['prior_state_path']).resolve()) == prov['prior_state_sha256']
assert sha((DIAG/prov['source_ledger_path']).resolve()) == prov['source_ledger_sha256']
for filename, expected_hash in prov['engine_hashes'].items():
    assert sha((DIAG/prov['engine_paths'][filename]).resolve()) == expected_hash
assert sha((DIAG/prov['script_path']).resolve()) == prov['script_sha256']
assert prov['floor'] == {'use_ee_floor':True,'ee_floor':0.1,'ee_threshold':0.1,'applications_per_scenario':1}
old_methods = {m['method']:m for m in read(MODEL/'model_validation/evidence/ee_floor_on_review/direct_diagnostics_full.json')['methods']}
names = dict(baseline['seq2name']['items'])
fidx, fcols, fate = numbers(baseline['_det_fate'])
living = set(range(1,35))
state_by_scenario = {}
method_checks = {}
for scenario in ['control_no_returns','source_exact_returns_to_36']:
    prefloor = read(DIAG/scenario/'post_returns_before_floor.json')['runtime']
    full_state = read(DIAG/scenario/'effective_floor_on.json')
    state = full_state['runtime']
    state_by_scenario[scenario] = state
    assert full_state['floor_application_count'] == 1
    assert state['use_ee_floor'] is True and state['ee_floor'] == 0.1
    for stage in [prefloor,state]:
        for field in ['p','q','catch','predation','growth','immigration','emigration','net_migration','respiration','egestion','GE','GS','TL']:
            original, current = vector(baseline[field]), vector(stage[field])
            assert all(original[g] == current[g] for g in living), (scenario,field)
        assert stage['_DC'] == baseline['_DC']
        assert stage['_det_fate'] == baseline['_det_fate']
        assert vector(stage['catch']) == vector(baseline['catch'])
        original_groups = {g:dict(zip(baseline['_groups_df']['columns'],r)) for g,r in zip(baseline['_groups_df']['index'],baseline['_groups_df']['data'])}
        current_groups = {g:dict(zip(stage['_groups_df']['columns'],r)) for g,r in zip(stage['_groups_df']['index'],stage['_groups_df']['data'])}
        for g in living:
            for column in ['group_name','trophic_info','taxon_descr','biomass','pb','qb','gs','tl','catch','p','q','predation','egestion','respiration','biomass_accum','immigration','emigration','net_migration']:
                assert original_groups[g][column] == current_groups[g][column],(scenario,g,column)
    for field in ['source_EE','source_M0']:
        old_frame,new_frame=frame(prior_effective[field]),frame(state[field])
        old_values=dict(zip(old_frame['index'],old_frame['data']))
        new_values=dict(zip(new_frame['index'],new_frame['data']))
        assert old_values == new_values,(scenario,field)
    for field in ['EE','M0']:
        assert vector(prefloor[field]) == vector(baseline[field]),(scenario,field)
    eg = vector(state['egestion']); m0 = vector(state['M0']); production = vector(state['p'])
    pp_m0 = vector(prefloor['M0']); pp_ee = vector(prefloor['EE']); effee = vector(state['EE'])
    sink = vector(state['external_mortality_export'])
    affected = []
    for g in living:
        close(sink[g],pp_m0[g]-m0[g])
        if sink[g]>0:
            affected.append(g)
            close(effee[g],0.1)
            close(m0[g],production[g]*(1-effee[g]))
        else:
            close(effee[g],pp_ee[g])
    assert set(affected) == {1,4,5,12,25,26,27,32}
    close(sum(sink.values()),65.52118784337331)
    ret = arr if scenario=='source_exact_returns_to_36' else np.zeros_like(arr)
    ri,rc,rv = numbers(state['_discard_returns'])
    assert ri == idx and rc == cols and np.array_equal(rv,ret)
    growth = vector(state['growth']); predation = vector(state['predation']); nm = vector(state['net_migration'])
    for budget in full_state['pool_budget']:
        pool = budget['pool_id']; ci=fcols.index(pool)
        mortality = sum(m0[g]*fate[i,ci] for i,g in enumerate(fidx))
        egest = sum(eg[g]*fate[i,ci] for i,g in enumerate(fidx))
        returned = float(ret[:,cols.index(pool)].sum())
        close(mortality,budget['mortality_inflow']);close(egest,budget['egestion_inflow']);close(returned,budget['fishery_return_inflow'])
        close(production[pool],mortality+egest+returned)
        residual = production[pool]-predation[pool]-catch[pool]-nm[pool]
        close(residual,budget['detritus_stock_residual']);close(residual,growth[pool])
        assert budget['source_BA'] == 0
        close(residual,budget['source_BA_balance_gap'])
    method_checks[scenario] = {}
    for method in ['GE','TE']:
        output = read(DIAG/scenario/f'{method}_full_return.json')
        assert output['execution']=='returned' and output['diagnostic']['status']=='WARN'
        diagnostic=output['diagnostic']; weighted=output['weighted_budget']
        mids,mcols,sppr=numbers(output['SPPR'])
        assert set(mids)==set(range(1,38)) and mcols==[37,36,35,22,12]
        assert output['SPPR']['row_ids']==mids and output['SPPR']['column_ids']==mcols
        assert output['SPPR']['row_names']==[names[g] for g in mids]
        assert output['SPPR']['column_names']==[names[g] for g in mcols]
        assert np.all(sppr>=0) and np.all(sppr[:,mcols.index(35)]==0)
        assert int(np.any(sppr<0,axis=0).sum())==diagnostic['divergence']['n_negative_sources']==0
        for matrix_name in ['A','L']:
            ai,ac,av=numbers(output[matrix_name]); assert ai==ac==mids
        # Scope sums are independently computed from full source columns by ID.
        scope_totals={}
        for scope,columns in output['source_scopes'].items():
            expected_scope=sppr[:,[mcols.index(g) for g in columns]].sum(axis=1)
            given=vector(output['scope_coefficients'][scope])
            assert np.allclose(expected_scope,[given[g] for g in mids],rtol=1e-12,atol=1e-12)
            footprint=float(np.dot(expected_scope,[catch[g] for g in mids]))
            key={'all':'ppr_all','inner':'ppr_inner','PP':'ppr_pp_only'}[scope]
            close(footprint,diagnostic['footprint'][key])
            scope_totals[scope]=footprint
        coeff=dict(zip(mids,sppr.sum(axis=1)))
        calc={
            'total_catch':sum(coeff[g]*catch[g] for g in mids),
            'internal_return':sum(coeff[g]*ret[idx.index(g),:].sum() for g in mids),
            'growth':sum(coeff[g]*growth[g] for g in mids),
            'net_migration':sum(coeff[g]*nm[g] for g in mids),
            'det_export':sum(coeff[g]*vector(state['det_export'])[g] for g in mids),
            'external_mortality_sink':sum(coeff[g]*sink[g] for g in mids),
            'inflow':sum(production[g] for g in [12,22,37]),
        }
        calc['external_catch']=calc['total_catch']-calc['internal_return']
        calc['weighted_outflow']=sum(calc[k] for k in ['external_catch','growth','net_migration','det_export','external_mortality_sink'])
        calc['source_BA0_outflow_arithmetic_only']=calc['weighted_outflow']-calc['growth']
        calc['source_BA0_weighted_gap']=-calc['growth']
        for key,value in calc.items():close(value,weighted[key])
        close(calc['inflow'],diagnostic['balance']['inflow']);close(calc['weighted_outflow'],diagnostic['balance']['outflow'])
        close(calc['total_catch'],diagnostic['footprint']['ppr_all'])
        assert diagnostic['balance']['is_balanced'] is True
        old_parity=None
        if scenario=='control_no_returns':
            parity={}
            for key in ['SPPR','A','L']:
                oi,oc,ov=numbers(old_methods[method][key]); ni,nc,nv=numbers(output[key])
                assert oi==ni and oc==nc
                parity[key]=bool(np.array_equal(ov,nv))
                assert parity[key],(method,key,float(np.max(np.abs(ov-nv))))
            old_parity=parity
        method_checks[scenario][method]={'source_matrix_shape':list(sppr.shape),'all_37_group_axes_and_five_source_labels_verified':True,'negative_entries':0,'nonfinite_entries':0,'Discards35_source_column_all_zero':True,'scope_footprints':scope_totals,'weighted_budget_independently_reconstructed':calc,'prior_saved_no_return_exact_matrix_parity':old_parity}

a=state_by_scenario['control_no_returns'];b=state_by_scenario['source_exact_returns_to_36']
for field in ['EE','M0','external_mortality_export']:
    assert vector(a[field])==vector(b[field])
for field in ['p','growth']:
    va,vb=vector(a[field]),vector(b[field])
    close(vb[36]-va[36],sum(discards.values()),atol=2e-13)
    assert all(va[g]==vb[g] for g in va if g!=36)
parity={}
for method in ['GE','TE']:
    aa=read(DIAG/'control_no_returns'/f'{method}_full_return.json')['SPPR']
    bb=read(DIAG/'source_exact_returns_to_36'/f'{method}_full_return.json')['SPPR']
    ai,ac,av=numbers(aa);bi,bc,bv=numbers(bb)
    assert ai==bi and ac==bc
    parity[method]={'max_absolute_change_by_source':{str(g):float(np.max(np.abs(bv[:,j]-av[:,j]))) for j,g in enumerate(ac)}}
    assert all(np.array_equal(av[:,j],bv[:,j]) for j,g in enumerate(ac) if g!=36)

final={
    'status':'All independent saved-array and input/hash checks passed.',
    'no_scientific_solver_executed':True,
    'code_source_state_and_runner_hashes_verified':True,
    'native_source_return_matrix_exactly_reconstructed':True,
    'all_living_fields_and_complete_catch_preserved':True,
    'same_floor_applied_once_per_scenario':True,
    'sourceBA0_semantics':'Conditional arithmetic only. Native/source BA, legacy completed pre-floor BA and effective floor closure are distinct provenance layers; no sourceBA0-preserving run was performed or implied.',
    'method_checks':method_checks,
    'between_scenario_matrix_changes':parity,
    'output_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(DIAG.rglob('*.json'))},
    'limitation':'A closed SPPR-weighted budget does not repair the physical Discards35 deficit: its source column/row has zero SPPR, while native Export35 is separately stored negative and canonical export is zero. No observed import or new offal is established.',
}
(QA/'diagnostic_array_verification.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf-8')
print(final['status'])
print(json.dumps({k:{m:v['scope_footprints']['all'] for m,v in methods.items()} for k,methods in method_checks.items()},indent=2))
