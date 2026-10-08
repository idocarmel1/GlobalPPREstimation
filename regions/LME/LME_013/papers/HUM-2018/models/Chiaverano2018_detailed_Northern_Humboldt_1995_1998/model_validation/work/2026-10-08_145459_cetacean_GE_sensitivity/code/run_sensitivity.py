"""Unadopted cetacean GE sensitivity with coherent P/B and unchanged Q/B."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math,hashlib,importlib.util,pickle,shutil,warnings
import numpy as np
RUN=Path(__file__).resolve().parents[1];MODEL=Path(__file__).resolve().parents[4]
ROOT=next(p for p in MODEL.parents if (p/'Project.xlsx').exists());OUT=RUN/'outputs'
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
helper_path=MODEL/'model_validation/work/2026-10-08_132433_balanced_validation/code/run_diagnostics.py'
spec=importlib.util.spec_from_file_location('capture_helpers',helper_path);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
h.HERE=OUT
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(h.plain(x),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
comparison=load(OUT/'validated_cetacean_comparison.json')
protected=[MODEL/'model.json',MODEL/'model_notes.md',MODEL/'sppr_source.xlsx',MODEL/'model_validation/validation.docx',MODEL/'model_validation/source_value_corrections.docx',MODEL/'model_validation/taxon_mapping.xlsx',ROOT/'Project.xlsx',ROOT/'regions/LME/LME_013/LME_013.xlsx']
before={p.relative_to(ROOT).as_posix():sha(p) for p in protected}
code=RUN/'code/executed_code';code.mkdir(exist_ok=True)
for file in ['ModelData.py','PPRCalculator.py','utils.py']:shutil.copyfile(ROOT/'tools/scientific_code/PPREstimation'/file,code/file)
settings=load(MODEL/'model_validation/work/2026-10-08_132433_balanced_validation/outputs/pooled/run_manifest.json')['constructor']
results=[]
for scenario,cohort,basis in [('strict_model_mean','strict_cetaceans','model_equal_mean_GE'),
 ('strict_group_mean','strict_cetaceans','mean_GE'),
 ('broad_model_mean','including_other_mammals_proxy','model_equal_mean_GE')]:
    target=comparison['cohorts'][cohort][basis]
    m=ModelData(str(MODEL/'model.json'),model_name='Humboldt Current cetacean GE sensitivity',model_year='1995')
    row=m.groups_data.loc[33].copy();df_before=m.groups_data.copy(deep=True)
    assert row['ee']==0 and row['catch']==0 and row['predation']==0 and row['biomass_accum']==0
    pb=target*row['qb'];p=pb*row['biomass']
    for field,value in [('pb',pb),('ge',target),('p',p),('M0',p),('flow_to_det',p+row['egestion'])]:m.groups_data.loc[33,field]=value
    transformations=[]
    for seq in m.groups_data.index:
        for col in m.groups_data:
            old=df_before.loc[seq,col];new=m.groups_data.loc[seq,col]
            try:same=old==new or (math.isnan(old) and math.isnan(new))
            except (TypeError,ValueError):same=old==new
            if not same:transformations.append(dict(group_id=int(seq),field=col,before=old,after=new))
    assert all(r['group_id']==33 for r in transformations)
    folder=OUT/scenario;folder.mkdir(exist_ok=True)
    dump(folder/'parameter_scenario.json',dict(status='UNADOPTED_SENSITIVITY',cohort=cohort,averaging=basis,GE_target=target,PB=pb,QB=row['qb'],
        held_fixed='Biomass, Q/B, EE, diet, catch, BA, migration and all other living biological inputs.',
        derived_changes='P/B raised to GE*Q/B. Cetacean P and M0 rise together because EE=0; respiration and detritus inflows recomputed by constructor.',
        transformations=transformations,source_sha256=sha(MODEL/'model.json'),constructor=settings))
    with warnings.catch_warnings(record=True) as notes:
        c=PPRCalculator.from_modeldata(m,**settings)
    assert c.is_model_balanced()[0]
    assert math.isclose(c.p[33]/c.q[33],target,rel_tol=1e-12)
    h.save(str((folder/'runtime_before_lossless.json').relative_to(OUT)),vars(c),typed=True)
    for mode,collapse in [('unpooled','never'),('pooled','always')]:
        f=folder/mode;f.mkdir(exist_ok=True)
        options=dict(DET_TE_vals=1,det_collapse_mode=collapse,det_open_mode='none',det_theta=1.,det_external_sppr=0.,fix_EE_0_cases=True)
        with warnings.catch_warnings(record=True) as notes:
            returned=c.diagnose_sppr(TE_option='GE',short=False,flat=False,return_sppr=True,**options)
        report,sppr,A,L=returned
        dump(f/'diagnostic_return.json',report)
        (f/'full_return.pkl').write_bytes(pickle.dumps(returned,protocol=pickle.HIGHEST_PROTOCOL))
        h.save(str((f/'full_return_lossless.json').relative_to(OUT)),returned,typed=True)
        trophic=c.get_groups_df()['trophic_info'].to_dict()
        for name,frame in [('SPPR',sppr),('A',A),('L',L)]:h.capture_matrix(f,name,frame,c.seq2name,trophic,'rows recipient groups; columns basal sources' if name=='SPPR' else 'rows and columns model groups')
        dump(f/'warnings.json',[str(n.message) for n in notes])
        negatives=[]
        for name,frame in [('SPPR',sppr),('A',A),('L',L)]:
            for ri,ci in zip(*np.where(frame.to_numpy(dtype=float)<0)):
                negatives.append(dict(matrix=name,source_column_id=int(frame.columns[ci]),source_column_name=c.seq2name.get(frame.columns[ci]),
                    recipient_group_id=int(frame.index[ri]),recipient_group_name=c.seq2name.get(frame.index[ri]),
                    value=float(frame.iloc[ri,ci]),comparison_tolerance=0.,unfished_recipient=bool(c.catch.get(frame.index[ri],0)==0)))
        dump(f/'negative_matrix_entries.json',negatives)
        scopes={scope:float(sppr.loc[33,cols].sum()) for scope,cols in dict(all=list(sppr.columns),
            inner=[x for x in sppr.columns if x not in c.get_Import_seq()],PP=[x for x in sppr.columns if x in c.get_PP_seq()]).items()}
        results.append(dict(scenario=scenario,cohort=cohort,averaging=basis,configuration=mode,target_GE=target,PB=pb,QB=float(row['qb']),
            actual_GE=float(c.p[33]/c.q[33]),cetacean_SPPR_GE=scopes,overall_status=report['status'],
            model_balanced=report['model_input']['is_model_balanced'],SPPR_budget=report['balance'],
            rho_living=report['divergence']['rho_living'],unpooled_b=report['divergence']['b'],
            config=options,cetacean_catch=float(c.catch[33]),canonical_model_unchanged=True))
        print(scenario,mode,'GE',target,'SPPR',scopes,'grade',report['status'],flush=True)
    h.save(str((folder/'runtime_after_lossless.json').relative_to(OUT)),vars(c),typed=True)
after={p.relative_to(ROOT).as_posix():sha(p) for p in protected}
assert before==after
assert all(sha(ROOT/r['model_path'])==r['model_sha256'] for r in comparison['reviewed_models'])
assert sha(ROOT/'Project.xlsx')==comparison['project_sha256']
dump(OUT/'sensitivity_summary.json',dict(status='UNADOPTED_SENSITIVITY',timestamp_utc=datetime.now(timezone.utc).isoformat(),
 input_sha256=sha(MODEL/'model.json'),constructor=settings,engine={p.name:sha(p) for p in code.iterdir()},
 method='GE only; same normalized runtime and detritus settings as corrected-model validation.',results=results,
 cohort=comparison['cohorts'],protected_inputs_unchanged=True,protected_hashes=before,
 note='Researcher-validated models have all comparator cetacean/mammal groups excluded from displayed PPR; these comparisons do not approve their coefficients.'))
print('Sensitivity complete; accepted scientific inputs, reports and workbooks unchanged.',flush=True)
