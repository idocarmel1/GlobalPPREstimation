"""Validate exact extraction artifacts and prepare isolated diagnostic workbooks."""
from pathlib import Path
import subprocess,sys,json,shutil,hashlib
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
REG=ROOT/'regions/LME_022';SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,write_book,overview,sha
from regional import set_setting
for mid in sys.argv[1:]:
    dest=REG/'models'/mid;et=dest/'extracted_tables'
    for cmd in [['validate.py',str(et)],['massbalance_check.py',str(et)],['database_json.py','-d',str(et),'--update-report']]:
        r=subprocess.run([sys.executable,'-X','utf8',str(SKILL/cmd[0]),*cmd[1:]],capture_output=True,text=True,encoding='utf-8')
        (dest/(cmd[0].replace('.py','')+'.log')).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
        print(mid,cmd[0],r.returncode)
    db=[p for p in et.glob('*.json') if p.name!='model.json'];assert len(db)==1,db
    # The legacy converter normalizes diet columns. Retain its compatibility
    # output, then restore source proportions in the canonical database JSON.
    source=json.loads((et/'model.json').read_text(encoding='utf-8'))
    converted=json.loads(db[0].read_text(encoding='utf-8'))
    original=json.loads(db[0].read_text(encoding='utf-8'))
    changes=[]
    for g in converted['group']:
        diet=source.get('diet',{}).get(g['group_seq'],{})
        if not diet:continue
        for item in (g.get('diet_descr') or {}).get('diet',[]):
            raw=diet.get(item['prey_seq'])
            if raw is not None and float(item['proportion'])!=float(raw):
                changes.append([g['group_seq'],item['prey_seq'],item['proportion'],str(raw)])
                item['proportion']=str(raw)
        if 'import' in diet:g['diet_imp']=str(diet['import'])
    if changes:
        (dest/'converter_normalized_intermediate.json').write_text(json.dumps(original,indent=2,ensure_ascii=False),encoding='utf-8')
        db[0].write_text(json.dumps(converted,indent=2,ensure_ascii=False),encoding='utf-8')
        (dest/'source_diet_restoration.json').write_text(json.dumps({'reason':'Legacy converter normalizes published diets; canonical JSON restores source proportions, not corrected/normalized model.','cells':changes},indent=2),encoding='utf-8')
        sys.path.insert(0,str(SKILL))
        from database_json import EwEConverter
        c=EwEConverter(str(dest/'source_faithful_conversion.log'))
        discards=sum(float(v) for r in source.get('discards',{}).values() for v in r.values())
        c.report_mass_balance(c.check_mass_balance(converted['group'],discards),db[0].stem,str(et/'MASS_BALANCE.md'))
        c.json_to_excel(str(db[0]))
    shutil.copy2(db[0],dest/'model.json')
    # Create a fresh minimal regional-format candidate workbook; never copy catch or selected results.
    b=read_book(REG/'LME_022.xlsx')
    b={s:{n:(h,[]) for n,(h,rs) in tabs.items()} for s,tabs in b.items()}
    b['Overview']['Settings']=(['field','value'],[['unit_id','LME_022'],['region_name','North Sea'],['selected_model_id',db[0].stem],['model_path','model.json'],['selection_rationale','ISOLATED CANDIDATE DIAGNOSTICS ONLY. User has not selected a production model.'],['production_eligible',False],['catch_basis','landings'],['taxon_detail_year',2019]])
    write_book(dest/'candidate_diagnostics.xlsx',b)
    snapshot=dest/'diagnostic_code';snapshot.mkdir(exist_ok=True)
    for p in [ROOT/'tools/run_region.py',ROOT/'tools/workbooks.py',ROOT/'tools/regional.py',ROOT/'tools/scientific_helpers/ppr_scopes.py']:
        shutil.copy2(p,snapshot/p.name)
    eng=ROOT/'tools/scientific_code/PPREstimation'
    for p in eng.rglob('*.py'):
        if '__pycache__' in p.parts:continue
        out=snapshot/'PPREstimation'/p.relative_to(eng);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
    manifest={str(p.relative_to(ROOT)):sha(p) for p in [dest/'model.json',*snapshot.rglob('*.py')]}
    (dest/'diagnostic_code_hashes.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
