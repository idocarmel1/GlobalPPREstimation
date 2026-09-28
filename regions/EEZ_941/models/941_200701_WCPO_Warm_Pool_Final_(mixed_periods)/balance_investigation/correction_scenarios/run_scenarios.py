"""Isolated, non-adopted juvenile tuna sensitivity scenarios. No canonical edits."""
from pathlib import Path
import json,sys,hashlib,contextlib,copy,traceback
import numpy as np
import pandas as pd
OUT=Path(__file__).resolve().parent
BASE=OUT.parent.parent
MID=BASE.name
CODE=BASE/'diagnostics/executed_code'
sys.path.insert(0,str(CODE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
settings=json.loads((BASE/'diagnostics/RUN_PROVENANCE.json').read_text())['loader_settings']
source=BASE/'model.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original_hash=sha(source)
canonical=json.loads(source.read_text())
def safe(v):
    if isinstance(v,dict): return {str(k):safe(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)): return [safe(x) for x in v]
    if isinstance(v,np.generic): return safe(v.item())
    if isinstance(v,float) and not np.isfinite(v): return None
    return v
def write(p,v): p.write_text(json.dumps(safe(v),indent=2,allow_nan=False),encoding='utf-8')
def load(p): return PPRCalculator.from_modeldata(ModelData(str(p)),**settings)
rawpred={11:0.,12:0.}
for g in canonical['group']:
    if g['biomass']=='-9999' or g['qb']=='-9999': continue
    for d in (g.get('diet_descr') or {}).get('diet') or []:
        seq=int(d['prey_seq'])
        if seq in rawpred: rawpred[seq]+=float(g['biomass'])*float(g['qb'])*float(d['proportion'])
all_results={}
with (OUT/'execution.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    baseline=load(BASE/(MID+'.json'))
    original={int(g['group_seq']):g for g in canonical['group']}
    for scenario in ['baseline','A_fixed_EE','B_EE095','B_EE1_boundary','C_negative_BA','D_fixed_M0']:
        folder=OUT/scenario;folder.mkdir(exist_ok=True)
        data=copy.deepcopy(canonical);changes=[]
        for g in data['group']:
            seq=int(g['group_seq'])
            if seq not in [11,12]: continue
            b,pb,qb,ee=[float(g[k]) for k in ['biomass','pb','qb','ee']]
            p=b*pb; m0=p*(1-ee); catch=float(baseline.catch[seq]); pred=float(baseline.predation[seq]); used=pred+catch
            raw_used=rawpred[seq]+catch
            newpb,newee,newba=pb,ee,0.
            raw_pb,raw_ee,raw_ba=pb,ee,0.
            if scenario=='A_fixed_EE': newpb=used/(b*ee);raw_pb=raw_used/(b*ee)
            if scenario in ['B_EE095','B_EE1_boundary']:
                newee=.95 if scenario=='B_EE095' else 1.;raw_ee=newee
                newpb=used/(b*newee);raw_pb=raw_used/(b*newee)
            if scenario=='C_negative_BA': newba=p*ee-used;raw_ba=p*ee-raw_used
            if scenario=='D_fixed_M0':
                newp=used+m0;newpb=newp/b;newee=used/newp
                raw_newp=raw_used+m0;raw_pb=raw_newp/b;raw_ee=raw_used/raw_newp
            if scenario!='baseline':
                g['pb']=str(newpb);g['ee']=str(newee);g['biomass_accum']=str(newba)
            changes.append({'seq':seq,'group':g['group_name'],'B':b,'QB':qb,'old_PB':pb,'new_PB':newpb,'PB_percent_change':100*(newpb/pb-1),'old_EE':ee,'new_EE':newee,'BA':newba,'BA_over_B_per_year':newba/b,'old_M0':m0,'new_M0':b*newpb*(1-newee),'new_P_over_Q':newpb/qb,'normalized_predation':pred,'raw_source_predation':rawpred[seq],'catch':catch,'raw_source_diet_solution':{'PB':raw_pb,'EE':raw_ee,'BA':raw_ba},'omitted_fishing_turnover_hypothesis_PB':pb+catch/b})
        inp=folder/(MID+'.json');write(inp,data)
        model=load(inp)
        model.get_groups_df().to_csv(folder/'loaded_groups.csv')
        _,rp,rq=model.is_model_balanced();resid=rp-model.p
        pd.DataFrame({'group':pd.Series(model.seq2name),'P':model.p,'Q':model.q,'catch':model.catch,'predation':model.predation,'BA':model.growth,'M0':model.M0,'egestion':model.egestion,'respiration':model.respiration,'P_residual':resid,'P_relative_residual':resid/model.p.replace(0,np.nan),'Q_direct_residual':model.p+model.egestion+model.respiration-model.q}).to_csv(folder/'flow_audit.csv',index_label='seq')
        result={'scenario':scenario,'input_sha256':sha(inp),'changes':changes,'is_model_balanced':bool(model.is_model_balanced()[0]),'negative_respiration_groups':[int(i) for i in model.respiration.index[model.respiration<0]],'negative_growth_groups':[int(i) for i in model.growth.index[model.growth<0]],'remaining_production_residuals':[{'seq':int(i),'group':model.seq2name[i],'absolute':float(resid[i]),'relative':float(resid[i]/model.p[i])} for i in resid.index if abs(resid[i])>1e-8],'methods':{}}
        for option in ['GE','TE','With Egestion']:
            slug=option.replace(' ','_')
            try:
                report,sppr,A,L=model.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
                write(folder/('diagnose_'+slug+'.json'),report)
                sppr.to_csv(folder/('SPPR_'+slug+'.csv'),index_label='seq')
                if scenario=='baseline':
                    assert json.loads(json.dumps(safe(report)))==json.loads((BASE/'diagnostics'/('diagnose_'+slug+'.json')).read_text()),option
                coeff=sppr.sum(axis=1)
                result['methods'][option]={'status':report['status'],'model_input_status':report['model_input']['status'],'p_max_rel_residual':report['model_input']['p_max_rel_residual'],'q_max_rel_residual':report['model_input']['q_max_rel_residual'],'balance_status':report['balance']['status'],'PP_relative_gap':report['balance']['rel_gap'],'ppr_all':report['footprint']['ppr_all'],'divergence_status':report['divergence']['status'],'n_negative_sources':report['divergence']['n_negative_sources'],'juvenile_SPPR':{str(i):float(coeff[i]) for i in [11,12]},'warnings':report['warnings']}
            except Exception as e:
                result['methods'][option]={'exception':type(e).__name__+': '+str(e)};traceback.print_exc()
        write(folder/'SCENARIO_SUMMARY.json',result);all_results[scenario]=result
write(OUT/'RESULTS.json',all_results)
assert sha(source)==original_hash
write(OUT/'PROVENANCE.json',{'nonadopted':True,'scope':'Independent-group experimental sensitivities; no native multistanza consistency claim','canonical_sha256_before':original_hash,'canonical_sha256_after':sha(source),'canonical_unchanged':True,'loader_settings':settings,'diagnostic_settings':{'options':['GE','TE','With Egestion'],'short':False,'flat':False,'return_sppr':True},'code_hashes':{p.name:sha(p) for p in CODE.glob('*.py')},'scenario_script_sha256':sha(Path(__file__)),'raw_vs_normalized':'Parameter formula solutions with raw source diet preserved alongside normalized computational solutions; only normalized solutions are run.'})
write(OUT/'artifact_manifest.json',{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='artifact_manifest.json'})
print(json.dumps({s:{'changes':v['changes'],'methods':v['methods']} for s,v in all_results.items()},indent=2))
