from pathlib import Path
import subprocess,sys,json,time,hashlib,shutil
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());OUT=Path(__file__).parent
models=['49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023)','49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'];runs=[]
for mid in models:
    dest=ROOT/'regions/LME_049/models'/mid
    for opt in ['GE','TE','With Egestion','global']:
        retained=dest/'evidence'/('diagnose_sppr_'+opt.replace(' ','_')+'.json')
        if retained.exists():
            runs.append({'model_id':mid,'TE_option':opt,'retained_existing_direct_call':True,'model_sha256':hashlib.sha256((dest/'model.json').read_bytes()).hexdigest()});continue
        t=time.monotonic();r=subprocess.run([sys.executable,'-X','utf8',str(OUT/'direct_diagnose.py'),mid,opt],capture_output=True,text=True,encoding='utf-8',timeout=180)
        (dest/'evidence'/('diagnose_sppr_'+opt.replace(' ','_')+'.log')).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8');assert r.returncode==0,(mid,opt,r.stderr)
        runs.append({'model_id':mid,'TE_option':opt,'elapsed_including_load_seconds':time.monotonic()-t,'model_sha256':hashlib.sha256((dest/'model.json').read_bytes()).hexdigest()});print(mid,opt,r.stdout.strip(),flush=True)
engine=ROOT/'tools/scientific_code/PPREstimation';snap=OUT/'direct_diagnose_code';snap.mkdir(exist_ok=True)
for p in [OUT/'direct_diagnose.py',Path(__file__),engine/'PPRCalculator.py',engine/'ModelData.py',engine/'create_PPRS_excel.py',engine/'utils.py']:shutil.copy2(p,snap/p.name)
prov={'date':'2026-09-28','requested_method':'PPRCalculator.diagnose_sppr','supported_TE_options':['GE','TE','With Egestion','global'],'call':{'short':False,'flat':False,'return_sppr':False,'thresholds':None,'det_collapse_mode':'never','det_open_mode':'none','det_theta':1.0,'det_external_sppr':0.0},'unoverridden_defaults':{'DET_TE_vals':1,'fix_EE_0_cases':True,'global_TE':'mean','global_weights':'consumption'},'loader':{'underdetermined':True,'zero_biomass_accum':False,'DC_tol':0.001,'normalize_DC':True,'zero_catch':True,'default_gs':True,'weight_flow':1.0,'weight_guess':1.0},'timeout_per_option_seconds':180,'new_MC_draws':0,'runs':runs,'code_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in snap.glob('*.py')}}
(OUT/'DIRECT_DIAGNOSE_PROVENANCE.json').write_text(json.dumps(prov,indent=2),encoding='utf-8')
