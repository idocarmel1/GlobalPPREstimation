"""Bounded GE/TE review run: retained initialization, current EE-floor accounting.

No workbook, canonical model, historical diagnostic, selection or publication writes.
"""
from pathlib import Path
import copy
from datetime import datetime, timezone
import hashlib
import inspect
import json
import os
import platform
import sys
import time
import traceback
import warnings

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
from tools.scientific_helpers.sppr.method_coverage import _isolated_module, encode_lossless, _runtime

MODEL = ROOT/'regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native'
WORK = Path(__file__).resolve().parents[1]
OUT = MODEL/'model_validation/evidence/ee_floor_on_review'
ARCHIVE = MODEL.parent/'PAT2024_FalklandShelf_2020_native__source/extracted_tables/evidence/selection_20260928/executed_code'
ENGINE = ROOT/'tools/scientific_code/PPREstimation'
HIST = MODEL/'model_validation/evidence/source_review/direct_diagnostics_full.json'
RUN_ID = '2026-11-14_120000_validation_ee_on'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def relative(path, base=OUT):
    return Path(os.path.relpath(path, base)).as_posix()

def save(name, value, base=OUT):
    path = base/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(encode_lossless(value), ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return path

def matrix(frame, names, kind):
    if frame is None:
        return {'availability':'unavailable','reason':'method returned no matrix'}
    out = encode_lossless(frame)
    out.update(orientation='rows=recipient groups; columns=basal sources' if kind=='SPPR' else 'rows and columns=group axes',
               row_names=[names.get(int(i),str(i)) for i in frame.index],
               column_names=[names.get(int(i),str(i)) for i in frame.columns],
               units='wet-weight-equivalent coefficient' if kind=='SPPR' else 'dimensionless operator')
    return out

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ('inputs','outputs','qa'):
        (WORK/name).mkdir(parents=True, exist_ok=True)
    protected = [MODEL/'model.json',MODEL/'sppr_source.xlsx',MODEL/'results/regional_snapshot.xlsx',
                 MODEL/'results/result_manifest.json',ROOT/'regions/LME/LME_014/LME_014.xlsx',HIST]
    before = {relative(p):sha(p) for p in protected}
    assert before[relative(MODEL/'model.json')]=='9880e521a406974367530ffb06f13392714dba57b9645c38a1b1448926d83d17'
    staged = WORK/'inputs/14_140001_PAT2024_FalklandShelf_2020_native_(2020).json'
    staged.write_bytes((MODEL/'model.json').read_bytes())
    assert sha(staged)==sha(MODEL/'model.json')
    historical = json.loads(HIST.read_text(encoding='utf-8'))
    constructor = dict(historical['constructor'])
    base_hashes={name:sha(ARCHIVE/name) for name in ('ModelData.py','PPRCalculator.py','utils.py')}
    assert base_hashes['PPRCalculator.py']==historical['engine']['PPRCalculator.py']
    modules={}
    modules['ModelData']=_isolated_module(ARCHIVE/'ModelData.py','_lme014_review_archived_data',{})
    modules['utils']=_isolated_module(ARCHIVE/'utils.py','_lme014_review_archived_utils',{})
    loader=_isolated_module(ARCHIVE/'PPRCalculator.py','_lme014_review_archived_calculator',modules)
    current=_isolated_module(ENGINE/'PPRCalculator.py','_lme014_review_current_calculator',modules)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        source=modules['ModelData'].ModelData(str(staged))
        source_before_completion=copy.deepcopy(source.groups_data)
        base=loader.PPRCalculator.from_modeldata(source,**constructor)
    # The preserved coefficient workbook includes the completed runtime group table.
    # Compare every numerical column and group/type identity; do not solve baseline.
    retained=pd.read_excel(MODEL/'sppr_source.xlsx',sheet_name='groups_df').set_index('seq')
    actual=base.get_groups_df().reindex(retained.index)
    comparisons={}
    for col in retained:
        if col not in actual:
            if col=='group_type':
                comparisons[col]={'passed':retained[col].fillna('').equals(actual['trophic_info'].fillna(''))}
                continue
            comparisons[col]={'passed':False,'reason':'column unavailable in archived initialized state'}
            continue
        if pd.api.types.is_numeric_dtype(retained[col]):
            left=retained[col].to_numpy(float); right=pd.to_numeric(actual[col],errors='raise').to_numpy(float)
            comparisons[col]={'passed':bool(np.allclose(left,right,rtol=1e-12,atol=1e-12,equal_nan=True)),
                              'max_absolute_difference':float(np.nanmax(np.abs(left-right))) if np.isfinite(left-right).any() else 0.}
        else:
            comparisons[col]={'passed':retained[col].fillna('').astype(str).equals(actual[col].fillna('').astype(str))}
    parity={'reference':relative(MODEL/'sppr_source.xlsx')+'#groups_df','rtol':1e-12,'atol':1e-12,
            'group_axes_equal':list(retained.index)==list(actual.index),'columns':comparisons,
            'all_pass':all(v['passed'] for v in comparisons.values()),'baseline_solver_run':False}
    save('initialization_parity.json',parity)
    if not parity['all_pass']:
        raise RuntimeError('Audited initialization differs from preserved runtime group table; ON execution blocked')
    pre_floor=copy.deepcopy(base)
    base.__class__=current.PPRCalculator
    # ModelData derives M0 and the old constructor mutates its group table.
    # Preserve canonical raw unknown mortality rather than calling derived M0 source data.
    raw_groups=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))['group']
    base.source_EE=source_before_completion['ee'].reindex(base._groups_df.index).copy()
    base.source_M0=pd.Series(np.nan,index=base._groups_df.index)
    raw_mortality=[]
    for group in raw_groups:
        seq=int(group['group_seq'])
        mortality=float(group.get('other_mort','-9999'))
        biomass=float(group.get('biomass','-9999'))
        if np.isfinite(mortality) and mortality>=0 and np.isfinite(biomass) and biomass>=0:
            base.source_M0.loc[seq]=mortality*biomass
        raw_mortality.append({'seq':seq,'other_mort':group.get('other_mort'),
                             'source_M0':base.source_M0.loc[seq]})
    base._initialization_settings={**constructor,'use_ee_floor':True,'ee_floor':.1,'ee_threshold':.1}
    base.apply_ee_floor(use_ee_floor=True,ee_floor=.1,ee_threshold=.1)
    living=base._groups_df.index[base._groups_df.trophic_info.isin(['Regular','PP'])]
    preserved={k:bool(np.array_equal(getattr(pre_floor,k).reindex(living).to_numpy(),getattr(base,k).reindex(living).to_numpy(),equal_nan=True))
               for k in ['p','q','catch','predation','growth','net_migration','respiration','egestion']}
    preserved['diet']=pre_floor._DC.equals(base._DC)
    preserved['fate']=pre_floor._det_fate.equals(base._det_fate)
    assert all(preserved.values()),preserved
    # Canonical accepted EE contains documented prior coupled-completion values.
    # Native publication unknowns are retained separately, not called measurements.
    save('initialization_and_floor.json',{'source':{'groups_before_calculator_completion':source_before_completion,'diet':source.DC,'fate':source.det_fate},
         'completed_before_floor':_runtime(pre_floor),'effective_after_floor':_runtime(base),
         'ledger':base.ee_floor_ledger,'info':base.ee_floor_info,'protected_living_fields':preserved,
         'canonical_raw_mortality':raw_mortality,
         'source_M0_definition':'Raw canonical other_mort rate times biomass only when both are valid; unknown sentinels remain NaN. ModelData-derived M0 is retained separately in groups_before_calculator_completion.',
         'source_EE_definition':'EE read from the exact accepted canonical variant, including its already documented coupled-completion departures; not asserted to be measured native publication EE.',
         'native_missing_EE_provenance':relative(MODEL/'model_notes.md')})
    actual_settings={'constructor':constructor,'floor':{'use_ee_floor':True,'ee_floor':.1,'ee_threshold':.1},
        'diagnostics':{'short':False,'flat':False,'return_sppr':True,'det_collapse_mode':'never','det_open_mode':'none'},
        'thresholds':current.DEFAULT_DIAGNOSTIC_THRESHOLDS}
    provenance={'schema_version':1,'run_id':RUN_ID,'timestamp':datetime.now(timezone.utc).isoformat(),
        'unit_id':'LME_014','model_id':MODEL.name,'canonical_input':relative(MODEL/'model.json'),
        'canonical_model_sha256':sha(MODEL/'model.json'),'configuration':actual_settings,
        'archived_base_engine':{name:{'path':relative(ARCHIVE/name),'sha256':digest} for name,digest in base_hashes.items()},
        'current_calculation_engine':{'path':relative(ENGINE/'PPRCalculator.py'),'sha256':sha(ENGINE/'PPRCalculator.py')},
        'serialization_helper':{'path':relative(ROOT/'tools/scientific_helpers/sppr/method_coverage.py'),'sha256':sha(ROOT/'tools/scientific_helpers/sppr/method_coverage.py')},
        'script':{'path':relative(Path(__file__)),'sha256':sha(Path(__file__))},
        'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,
        'base_loader_provenance':'Archived 2026-09-28 selection engine. ModelData differs from 2026-09-30 direct review; completed runtime parity checked independently against retained coefficient workbook.',
        'loader_warnings':[str(w.message) for w in caught],
        'historical_results':{'path':relative(HIST),'sha256':sha(HIST),'floor_flags':'not recorded; never relabeled ON'},
        'adoption':'review only; no workbook, snapshot, project, map, trend or signed-review adoption'}
    save('run_provenance.json',provenance)
    methods=[]
    negatives=[]
    for option in ('GE','TE'):
        started=time.perf_counter()
        record={'method':option,'call':{'TE_option':option,**actual_settings['diagnostics']}}
        try:
            with warnings.catch_warnings(record=True) as diagnostic_warnings:
                warnings.simplefilter('always')
                report,sppr,A,L=base.diagnose_sppr(TE_option=option,**actual_settings['diagnostics'])
            record.update(execution='returned',diagnostic=report,SPPR=matrix(sppr,base.seq2name,'SPPR'),
                          A=matrix(A,base.seq2name,'A'),L=matrix(L,base.seq2name,'L'),
                          warnings=[str(w.message) for w in diagnostic_warnings])
            scopes={'all':list(sppr.columns),'inner':[s for s in sppr.columns if base._groups_df.loc[s,'trophic_info']!='Import'],
                    'PP':[s for s in sppr.columns if base._groups_df.loc[s,'trophic_info']=='PP']}
            record['source_scope']=scopes
            record['scope_coefficients']={s:sppr[cols].sum(axis=1) for s,cols in scopes.items()}
            record['source_matrix_review']={'shape':list(sppr.shape),'negative_count':int((sppr.to_numpy() < -1e-10).sum()),
                'nonfinite_count':int((~np.isfinite(sppr.to_numpy())).sum()),'all_groups_including_unfished':True,
                'source_columns':[{'id':int(s),'name':base.seq2name[s]} for s in sppr.columns]}
            record['model_catch_footprint_reconciliation']={s:{'matrix_catch_dot':float(base.catch.reindex(sppr.index).dot(sppr[cols].sum(axis=1))),
                'diagnostic':report['footprint'][{'all':'ppr_all','inner':'ppr_inner','PP':'ppr_pp_only'}[s]]} for s,cols in scopes.items()}
            for matrix_name,frame in [('SPPR',sppr),('A',A),('L',L)]:
                if frame is not None:
                    for i,j in zip(*np.where(frame.to_numpy() < -1e-10)):
                        recipient,source_id=frame.index[i],frame.columns[j]
                        negatives.append({'method':option,'matrix':matrix_name,'source_id':int(source_id),'source_name':base.seq2name[source_id],
                           'recipient_id':int(recipient),'recipient_name':base.seq2name[recipient],'value':float(frame.iloc[i,j]),'tolerance':1e-10})
            old=next(m for m in historical['methods'] if m['method']==option)['diagnostic']
            record['historical_comparison']={key:{'historical':old[section][key],'floor_on':report[section][key]}
                for section,keys in [('divergence',['b','rho_living','sppr_det']),('balance',['is_balanced','rel_gap']),('footprint',['ppr_all','ppr_inner','ppr_pp_only'])] for key in keys}
        except Exception:
            record.update(execution='exception',exception=traceback.format_exc())
        record['seconds']=time.perf_counter()-started
        methods.append(record)
        save('direct_diagnostics_full.json',{'model_id':MODEL.name,'run_id':RUN_ID,'methods':methods})
        print(option,record['execution'],record.get('diagnostic',{}).get('status'),flush=True)
    save('negative_entries.json',{'entries':negatives,'SPPR_negative_pairings':[r for r in negatives if r['matrix']=='SPPR'],
        'L_interpretation':'A minus identity, not the SPPR matrix; living diagonal negatives are expected equation-operator terms.'})
    after={relative(p):sha(p) for p in protected}
    checks={'protected_inputs_unchanged':before==after,'initialization_parity':parity['all_pass'],
        'living_fields_preserved':all(preserved.values()),'both_methods_returned':all(m['execution']=='returned' for m in methods)}
    save('protected_verification.json',{'before':before,'after':after,'checks':checks},WORK/'qa')
    summary={'run_id':RUN_ID,'model_id':MODEL.name,'floor':base.ee_floor_info,'checks':checks,
        'changed_groups':base.ee_floor_ledger[base.ee_floor_ledger.applied].reset_index().to_dict('records'),
        'methods':[{k:m[k] for k in ['method','execution','diagnostic','source_matrix_review','historical_comparison'] if k in m} for m in methods]}
    save('review_summary.json',summary)
    artifacts=[]
    for name,role in [('run_provenance.json','configuration'),('initialization_parity.json','initialization-parity'),
        ('initialization_and_floor.json','floor-ledger'),('direct_diagnostics_full.json','full-direct-returns'),
        ('negative_entries.json','negative-pairings'),('review_summary.json','review-summary')]:
        path=OUT/name
        artifacts.append({'role':role,'path':name,'sha256':sha(path),'availability':'present'})
    artifacts.append({'role':'protected-inputs','path':relative(WORK/'qa/protected_verification.json'),
                      'sha256':sha(WORK/'qa/protected_verification.json'),'availability':'present'})
    save('evidence_index.json',{'schema_version':1,'run_id':RUN_ID,'region_id':'LME_014','model_id':MODEL.name,
        'variant_id':'accepted-native-ee-floor-on-0.1-review','methods':['GE','TE'],
        'source_identity':{'canonical_model_path':relative(MODEL/'model.json'),'sha256':sha(MODEL/'model.json')},
        'computational_input_identity':{'canonical_model_sha256':sha(MODEL/'model.json'),'use_ee_floor':True,'ee_floor':.1,'ee_threshold':.1},
        'canonical_model_sha256':sha(MODEL/'model.json'),'required_roles':[r['role'] for r in artifacts],
        'artifacts':artifacts,'reconciliation':checks})
    print(json.dumps(encode_lossless(summary),ensure_ascii=False,indent=2),flush=True)
    assert all(checks.values()),checks

if __name__=='__main__':
    main()
