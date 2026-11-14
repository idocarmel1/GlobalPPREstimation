"""Report arithmetic and lossless evidence verification; no calculator calls."""
from pathlib import Path
import gzip, hashlib, json, os, shutil, sys
import numpy as np
import pandas as pd
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
MODEL=Path(__file__).resolve().parents[4]
WORK=Path(__file__).resolve().parents[1]
EV=MODEL/'model_validation/evidence/ee_floor_on'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf8')
def frame(d): return pd.DataFrame(d['data'],index=d['index'],columns=d['columns'])
def series(d): return frame(d['frame']).iloc[:,0]
def main():
    report=json.loads((WORK/'outputs/diagnostic_audit.json').read_text(encoding='utf8'))
    constructor=json.loads(gzip.decompress((EV/'constructor.json.gz').read_bytes()))
    state=constructor['constructor_outcome']['runtime']
    base=state['_ee_floor_base']; before=frame(base['_groups_df']); after=frame(state['_groups_df'])
    groups=constructor['constructor_outcome']['groups']; names={g['id']:g['name'] for g in groups}
    living=[g['id'] for g in groups if g['type'] in ('Regular','PP')]
    det=[g['id'] for g in groups if g['type']=='DET']
    comparisons={}
    for attr in ('p','q','growth'):
        comparisons[attr]=bool(np.allclose(series(base[attr]).loc[living],series(state[attr]).loc[living],atol=0,rtol=0,equal_nan=True))
    for attr in ('biomass','pb','qb','catch','predation','respiration','egestion','biomass_accum','net_migration'):
        if attr in before:
            comparisons['table_'+attr]=bool(np.allclose(before.loc[living,attr].astype(float),after.loc[living,attr].astype(float),atol=0,rtol=0,equal_nan=True))
    sink=series(state['external_mortality_export'])
    ledger=frame(state['ee_floor_ledger'])
    source=json.loads((MODEL/'model.json').read_text(encoding='utf8'))
    source_rows={int(g['group_seq']):g for g in source['group']}
    source_distinction=[]
    for group_id,row in ledger[ledger.applied].iterrows():
        g=source_rows[group_id]
        source_distinction.append({'group_id':group_id,'group_name':names[group_id],'canonical_ee':float(g['ee']),'canonical_other_mort':g.get('other_mort'),'canonical_independent_M0':None,'raw_M0_availability':'Not independently provided in canonical JSON; other_mort=-9999 means unknown','engine_field_source_M0':row.source_M0,'engine_field_source_M0_interpretation':'Loader-completed/exposed mortality; not a separately observed publication value','EE_before_floor':row.EE_before_floor,'M0_before_floor':row.M0_before_floor,'EE_effective':row.EE_effective,'M0_effective':row.M0_effective,'external_mortality_export':row.external_mortality_export})
    detritus=[]
    for group_id in det:
        detritus.append({'group_id':group_id,'group_name':names[group_id],'inflow_before':float(series(base['p'])[group_id]),'inflow_effective':float(series(state['p'])[group_id]),'stock_residual_before':float(series(base['growth'])[group_id]),'stock_residual_effective':float(series(state['growth'])[group_id])})
    for key,label in [('new_GE','GE'),('new_TE_EEfix','TE')]:
        doc=json.loads(gzip.decompress((EV/f'{key}.json.gz').read_bytes()))
        matrix=frame(doc['source_matrix']); row_sums=matrix.sum(axis=1)
        weighted={scope:float(matrix[cols].sum(axis=1).mul(sink).sum()) for scope,cols in [('all',list(matrix.columns)),('inner',[x for x in matrix.columns if x!=41]),('PP',[39])]}
        report['methods'][label]['weighted_external_mortality_sink']=weighted
        report['methods'][label]['basal_sources']=[{'id':int(i),'name':names[int(i)]} for i in matrix.columns]
        report['methods'][label]['maximum_group_total']={'id':int(row_sums.idxmax()),'name':names[int(row_sums.idxmax())],'sppr':float(row_sums.max())}
        report['methods'][label]['reopened_matrix_values_equal']=bool(np.array_equal(frame(json.loads((EV/f'SPPR_{label}.json').read_text())).to_numpy(),matrix.to_numpy()))
    report['floor_accounting']={'affected_groups':source_distinction,'detritus':detritus,'living_flow_checks':comparisons,'all_living_flow_checks_pass':all(comparisons.values()),'raw_external_mortality_sink_total':float(sink.sum()),'units':'model mass flow density per year; not observed fisheries catch','raw_canonical_source_M0_note':'Source M0 is unavailable independently. Engine source_M0 field contains loader-completed/exposed mortality and must not be described as an independently reported parameter.'}
    report['effective_constructor']=constructor['identity']['constructor']
    report['report_ready']={
        'GE diagnostics':[
            'EE floor ON (0.1): overall OK; living-network spectral radius rho_living = 0.1060 and detritus recycling b = 0.03056, both below 1. Detritus (group 40) SPPR = 1.3599.',
            'No negative SPPR entries across the basal-source columns. All 123 entries in the 41-group by 3-source matrix are finite, including unfished groups. Sources are diet_import, Detritus and Phytoplankton.',
            'Model and SPPR balances pass; SPPR relative gap = 5.06e-9. No diagnostic warning was returned.'],
        'TE diagnostics':[
            'EE floor ON (0.1): overall OK; rho_living = 0.2461. Detritus (group 40) SPPR = 0.6730. The reported b = 0 is the TE method convention, not evidence that physical detritus recycling is absent.',
            'No negative SPPR entries across the basal-source columns; all 123 entries are finite. Model and SPPR balances pass; SPPR relative gap = 1.37e-7.',
            'The maximum group-total SPPR remains high for Tuna (group 8): 2,530.26. This magnitude and the catch-mapping transfer assumptions require ecological interpretation despite the numerical OK grade.'],
        'Other':[
            'The 0.1 EE floor changes Brittle star (EE 0.01), Tongue sole (0) and Octopus (0.04) to 0.1 after audited initialization. It redirects 0.26452 model flow units/year from nonpredatory mortality to a hypothetical external nonfishery sink. Living production, consumption, catch and other protected flows remain unchanged.',
            'Detritus inflow decreases by the routed sink; no negative detritus stock residual occurs. The sink is not observed catch. Independent source M0 is unavailable; retained engine mortality values are loader-completed.',
            'Fresh GE/TE diagnostics use the recorded current engine and verified audited initialization. Historical WARN diagnostics remain supporting evidence under their original configuration. Numerical OK does not establish source fidelity, regional suitability or researcher approval.']}
    dump(WORK/'outputs/diagnostic_audit.json',report)
    dump(EV/'diagnostic_audit.json',report)
    dump(EV/'floor_accounting.json',report['floor_accounting'])
    shutil.copy2(__file__,EV/'executed_code'/Path(__file__).name)
    index=json.loads((EV/'evidence_index.json').read_text(encoding='utf8'))
    index['artifacts']=[{'role':p.relative_to(EV).as_posix(),'path':p.relative_to(EV).as_posix(),'sha256':sha(p),'availability':'present'} for p in sorted(EV.rglob('*')) if p.is_file() and p.name not in ('evidence_index.json','completeness.json')]
    index['artifacts'].append({'role':'canonical_model','path':os.path.relpath(MODEL/'model.json',EV).replace('\\','/'),'sha256':sha(MODEL/'model.json'),'availability':'present'})
    index['required_roles']+=['diagnostic_audit.json','floor_accounting.json']
    index['reconciliation']['living_flows_preserved']=all(comparisons.values())
    index['reconciliation']['reopened_matrices_equal']=all(v['reopened_matrix_values_equal'] for v in report['methods'].values())
    dump(EV/'evidence_index.json',index)
    print(json.dumps({'floor_accounting':report['floor_accounting'],'weighted_sink':{k:v['weighted_external_mortality_sink'] for k,v in report['methods'].items()}},ensure_ascii=False))
if __name__=='__main__': main()
