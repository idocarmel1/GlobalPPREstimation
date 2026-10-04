"""Read-only causal audit of the published/canonical model and frozen diagnostic engine.

No parameter changes, hypothetical repairs, or adoption. Additional calls retain the
SPPR vector from each same-configuration diagnostic for an exact residual decomposition.
"""
from pathlib import Path
from decimal import Decimal as D
import sys,json,hashlib,contextlib,shutil
import numpy as np
import pandas as pd
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
MID='941_200701_WCPO_Warm_Pool_Final_(mixed_periods)'
BASE=ROOT/'regions/EEZ_941/models'/MID
DIAG=BASE/'diagnostics'; OUT=BASE/'balance_investigation'; OUT.mkdir(exist_ok=True)
CODE=DIAG/'executed_code'; sys.path.insert(0,str(CODE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
source=DIAG/'canonical_run_input.json'
before_hash=hashlib.sha256((BASE/'model.json').read_bytes()).hexdigest()
assert before_hash==hashlib.sha256(source.read_bytes()).hexdigest()
settings=json.loads((DIAG/'RUN_PROVENANCE.json').read_text())['loader_settings']
shutil.copyfile(__file__,OUT/'audit_balance_causes.py')
raw=json.loads(source.read_text())['group']
def num(v): return None if v in [None,'-9999'] else D(str(v))
def write(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')

with (OUT/'execution.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    md=ModelData(str(BASE/(MID+'.json')))
    model=PPRCalculator.from_modeldata(md,**settings)
    predraw={int(g['group_seq']):D(0) for g in raw}
    dietdetails=[]
    for g in raw:
        b,qb=num(g['biomass']),num(g['qb'])
        if b is None or qb is None: continue
        dc=(g.get('diet_descr') or {}).get('diet') or []
        for prey in dc:
            flow=b*qb*D(prey['proportion']); seq=int(prey['prey_seq'])
            predraw[seq]+=flow
            if seq in [11,12]:
                dietdetails.append({'prey_seq':seq,'predator_seq':int(g['group_seq']),'predator':g['group_name'],'B':str(b),'QB':str(qb),'source_diet_fraction':prey['proportion'],'raw_predation_flow':str(flow),'loaded_diet_fraction':float(model._DC.loc[int(g['group_seq']),seq]),'loaded_predation_flow':float(model.q[int(g['group_seq'])]*model._DC.loc[int(g['group_seq']),seq])})
    write('juvenile_tuna_predation_cells.json',dietdetails)
    source_rows=[]
    for g in raw:
        seq=int(g['group_seq']); b,pb,ee,c,ba=[num(g.get(k)) for k in ['biomass','pb','ee','export','biomass_accum']]
        if b is None or pb is None or ee is None: continue
        p=b*pb; pred=predraw[seq]
        r={'seq':seq,'group':g['group_name'],'B':str(b),'PB':str(pb),'production_B_PB':str(p),'published_EE':str(ee),'available_used_production_P_EE':str(p*ee),'source_landings':None if c is None else str(c),'raw_predation':str(pred),'BA':None if ba is None else str(ba),'EE_predation_only':str(pred/p),'EE_predation_and_known_catch':str((pred+(c or D(0)))/p),'raw_residual_known_terms':str(pred+(c or D(0))+(ba or D(0))-p*ee),'raw_residual_relative_production':str((pred+(c or D(0))+(ba or D(0))-p*ee)/p),'BA_unknown':ba is None,'catch_unknown':c is None,'normalized_predation':float(model.predation[seq]),'normalization_predation_change':float(model.predation[seq])-float(pred)}
        source_rows.append(r)
    pd.DataFrame(source_rows).to_csv(OUT/'source_equation_audit.csv',index=False)
    write('source_equation_audit.json',source_rows)
    balanced,recomputed_p,recomputed_q=model.is_model_balanced()
    residual=recomputed_p-model.p
    consumption_direct=model.p+model.egestion+model.respiration-model.q
    rows=pd.DataFrame({'group':pd.Series(model.seq2name),'production':model.p,'catch':model.catch,'predation':model.predation,'growth':model.growth,'net_migration':model.net_migration,'other_mortality_M0':model.M0,'recomputed_production':recomputed_p,'production_residual':residual,'relative_production_residual':residual/model.p.replace(0,np.nan),'consumption_Q':model.q,'egestion':model.egestion,'respiration':model.respiration,'direct_consumption_residual_Q_check':consumption_direct,'diagnostic_consumption_residual':recomputed_q-model.q})
    rows.to_csv(OUT/'loaded_equation_audit.csv',index_label='seq')
    methods={}
    for option in ['GE','TE','With Egestion']:
        rep,sppr,A,L=model.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
        prior=json.loads((DIAG/('diagnose_'+option.replace(' ','_')+'.json')).read_text())
        assert json.loads(json.dumps(rep))==prior,(option,'diagnostic changed')
        total=sppr.sum(axis=1).reindex(model.p.index)
        term=rows.copy()
        term['sppr']=total
        for field in ['catch','growth','net_migration','production_residual']:
            term['weighted_'+field]=term[field]*total
        term['weighted_export']=term['weighted_catch']+term['weighted_growth']+term['weighted_net_migration']
        slug=option.replace(' ','_')
        term.to_csv(OUT/('budget_decomposition_'+slug+'.csv'),index_label='seq')
        sppr.to_csv(OUT/('SPPR_'+slug+'.csv'),index_label='seq')
        actual_gap=rep['balance']['outflow']-rep['balance']['inflow']
        weighted=float((residual*total).sum())
        assert np.isclose(actual_gap,weighted,rtol=1e-8,atol=1e-7),(option,actual_gap,weighted)
        contributions=[{'seq':int(seq),'group':model.seq2name[seq],'production_residual':float(residual[seq]),'sppr':float(total[seq]),'weighted_gap':float(residual[seq]*total[seq]),'percent_net_gap':float(100*residual[seq]*total[seq]/actual_gap)} for seq in model.p.index if abs(float(residual[seq]*total[seq]))>1e-8]
        contributions.sort(key=lambda r:abs(r['weighted_gap']),reverse=True)
        methods[option]={'inflow':rep['balance']['inflow'],'outflow':rep['balance']['outflow'],'gap':actual_gap,'relative_gap':rep['balance']['rel_gap'],'sum_SPPR_weighted_production_residual':weighted,'identity_error':actual_gap-weighted,'weighted_catch':float(term['weighted_catch'].sum()),'weighted_growth':float(term['weighted_growth'].sum()),'weighted_net_migration':float(term['weighted_net_migration'].sum()),'contributors':contributions,'status':rep['status']}
    result={'model_id':MID,'source_input_sha256':before_hash,'loader_settings':settings,'source_equation_units':'tons/km2/year','PP_budget_units':'primary-production-equivalent tons/km2/year','direct_consumption_max_abs_residual':float(consumption_direct.abs().max()),'diagnostic_consumption_max_abs_residual':float((recomputed_q-model.q).abs().max()),'main_source_rows':[r for r in source_rows if r['seq'] in [5,6,7,11,12,13,14]],'methods':methods,'livecanonical_unchanged':hashlib.sha256((BASE/'model.json').read_bytes()).hexdigest()==before_hash,'no_hypothetical_scenarios':True,'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CODE.glob('*.py')}}
    write('CAUSE_AUDIT.json',result)
print(json.dumps(result,indent=2))
