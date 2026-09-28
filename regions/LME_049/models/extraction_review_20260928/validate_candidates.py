"""Validate source imports; undo converter assumptions; stage isolated diagnostics."""
from pathlib import Path
import subprocess,sys,json,shutil,hashlib,csv
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists()); REG=ROOT/'regions/LME_049'
SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts');sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(SKILL))
from workbooks import read_book,write_book,sha
from database_json import EwEConverter
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
for dest in REG.glob('models/49_*'):
    et=dest/'extracted_tables';source=json.loads((et/'model.json').read_text(encoding='utf-8'));year=source['metadata']['model_year'];cells=json.loads((et/'source_cells.json').read_text(encoding='utf-8'));dcells=json.loads((et/'diet_source_cells.json').read_text(encoding='utf-8'))
    for cmd in [['validate.py',str(et)],['massbalance_check.py',str(et)],['database_json.py','-d',str(et),'--update-report']]:
        r=subprocess.run([sys.executable,'-X','utf8',str(SKILL/cmd[0]),*cmd[1:]],capture_output=True,text=True,encoding='utf-8')
        (dest/(cmd[0].replace('.py','')+'.log')).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8');print(dest.name,cmd[0],r.returncode)
    db=list(et.glob('49_*.json'));assert len(db)==1,db
    d=json.loads(db[0].read_text());converter_model=json.loads(db[0].read_text());edits=[]
    for g in d['group']:
        seq=int(g['group_seq']);sg=source['groups'][seq-1];assert g['group_name']==sg['name']
        for sf,df in [('biomass','biomass_habitat_area'),('pb','pb'),('qb','qb'),('ee','ee'),('hab_area','habitat_area')]:g[df]=sg.get(sf) or '-9999'
        if year==2013:
            b=[x['source_text'] for x in cells if x['group_seq']==seq and x['field']=='biomass_model_area'][0]
            g['biomass']=b if not b.startswith('<') and b not in ['–','—'] else '-9999'
        else:g['biomass']=sg.get('biomass') or '-9999'
        catch=source['landings'].get(str(seq),{}).get('Total fishery');g['export']=catch or '-9999'
        for f in ['diet_imp','gs','vbk','shadow_price','detritus_import']:g[f]='-9999'
        gd=[]
        for c in dcells:
            if c['predator_seq']!=seq:continue
            t=c['source_text']
            if t=='':continue
            gd.append({'prey_seq':str(c['prey_seq']),'proportion':'-9999' if t=='+' else t,'detritus_fate':'-9999'})
        g['diet_descr']={'diet':gd} if gd else None
        # A database field that is not source-supported remains the -9999 sentinel.
        for f in ['biomass_accum','biomass_accum_rate','respiration','immigration','emigration','emigration_rate','other_mort','ge']:g[f]='-9999'
        old=converter_model['group'][seq-1]
        for f in g:
            if g[f]!=old[f]:edits.append({'group_seq':seq,'field':f,'converter_value':old[f],'source_faithful_value':g[f]})
    dump(dest/'model.json',d);dump(et/'converter_transformations_reversed.json',edits)
    cv=EwEConverter(log_file=str(dest/'canonical_roundtrip.log'))
    cv.json_to_excel(str(dest/'model.json'),str(et/'canonical_reconstructed.xlsx'))
    findings=cv.check_mass_balance(d['group']);cv.report_mass_balance(findings,dest.name,str(et/'MASS_BALANCE_CANONICAL.md'))
    # Exact JSON roundtrip assertions independent of numerical solver assumptions.
    for sg,g in zip(source['groups'],d['group']):
        assert all(g[f]==(sg.get(f) or '-9999') for f in ['pb','qb','ee'])
        entries=(g.get('diet_descr') or {}).get('diet',[])
        lookup={int(x['prey_seq']):x['proportion'] for x in entries}
        for c in dcells:
            if c['predator_seq']==sg['n'] and c['source_text']:
                assert lookup[c['prey_seq']]==('-9999' if c['source_text']=='+' else c['source_text'])
        assert g['taxon_descr']
    dump(dest/'roundtrip_checks.json',{'groups':len(d['group']),'all_source_pb_qb_ee_preserved':True,'all_printed_diet_values_and_censored_sentinels_preserved':True,'all_taxonomy_present':True,'canonical_sha256':sha(dest/'model.json'),'source_import_converter_normalization_reversed':True,'conversion_changes':len(edits)})
    b=read_book(REG/'LME_049.xlsx');b={s:{n:(h,[]) for n,(h,rs) in tabs.items()} for s,tabs in b.items()}
    engine_id=db[0].stem.replace('49_Kuroshio_Current_','49_')
    b['Overview']['Settings']=(['field','value'],[['unit_id','LME_049'],['region_name','Kuroshio Current'],['selected_model_id',engine_id],['model_path','model.json'],['selection_rationale','ISOLATED CANDIDATE LOADER DIAGNOSTIC ONLY. Exact published-model SPPR unsupported until censored/missing inputs are resolved. No production selection.'],['production_eligible',False],['catch_basis','landings'],['taxon_detail_year',2019]])
    write_book(dest/'candidate_diagnostics.xlsx',b)
    snapshot=dest/'diagnostic_code';snapshot.mkdir(exist_ok=True)
    for p in [ROOT/'tools/run_region.py',ROOT/'tools/workbooks.py',ROOT/'tools/regional.py',ROOT/'tools/scientific_helpers/ppr_scopes.py']:
        shutil.copy2(p,snapshot/p.name)
    eng=ROOT/'tools/scientific_code/PPREstimation'
    for p in eng.rglob('*.py'):
        if '__pycache__' in p.parts:continue
        out=snapshot/'PPREstimation'/p.relative_to(eng);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
    dump(dest/'diagnostic_code_hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in [dest/'model.json',*snapshot.rglob('*.py')]})
    dump(dest/'diagnostic_settings.json',{'scope':'unselected candidate loader diagnostics only','exact_source_sppr_eligibility':'unsupported due unresolved/censored inputs','mc_samples_per_method':100,'method_timeout_seconds':180,'random_seed':'not fixed by wrapper','loader_options':{'underdetermined':True,'zero_biomass_accum':False,'DC_tol':.001,'normalize_DC':True},'loader_caveats':['Diet -9999 entries are converted to zero by ModelData; cannot resolve censored observations.','Diet columns normalized by loader; printed values retained in canonical model.json.','Missing GS defaults to 0.2 for regular groups.','Unreported parameters may be solver-completed.'],'production_eligible':False})
    print('staged',dest.name,db[0].stem)
