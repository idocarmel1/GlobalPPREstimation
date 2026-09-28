"""Single coordinator for central writes and preservation checks."""
from pathlib import Path
import sys,json,math,collections,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from update_project import update
from regional import result_hash
from original_atlas_data import review_flags
from xml_audit_reader import read_book

def canonical(records_):
    return digest_tables(sorted([list(r.items()) for r in records_],key=repr))

def main():
    stage='--stage' in sys.argv
    destination=ROOT/'Project.pending.xlsx' if stage else ROOT/'Project.xlsx'
    if stage:
        import update_project
        def staged_write(path,book):
            # Preserve native Excel tables while leaving the open user file alone.
            prepared=HERE/'prepared/Project.xlsx'
            write_book(prepared,book)
            shutil.copyfile(prepared,destination)
        update_project.write_book=staged_write
    baseline=read_book(HERE/'baseline/Project.xlsx')
    assert sha(ROOT/'Project.xlsx')==sha(HERE/'baseline/Project.xlsx'),'Central workbook changed since baseline; re-review before merge'
    previous={r['unit_id']:r for r in records(baseline,'Regions & status','Regions')}
    paths=[ROOT/r['workbook'] for r in previous.values() if sha(ROOT/r['workbook'])!=r['sha256']]
    units={p.stem for p in paths}
    expected={'EEZ_598','EEZ_941','HS_071','HS_077','LME_013','LME_022','LME_024','LME_027','LME_029','LME_037','LME_049'}
    assert units==expected,(units,expected)
    selected=[]
    for r in previous.values():
        if not r['selected_model_id']:continue
        p=ROOT/r['workbook'];b=read_book(p);o=validate_region(b,p)
        assert o['calculation_result_sha256']==result_hash(b)
        assert o['selected_model_id']==r['selected_model_id']
        assert o['selection_rationale']==r['selection_rationale']
        allannual=records(b,'PPR','Annual')
        def get(metric):return next((x for x in allannual if x['scope']=='all' and x['method']=='new_GE' and x['catch_basis']=='catch' and x['unidentified']=='method' and x['metric']==metric),{})
        v=get('ppr');total=get('catch').get(2019);covered=get('covered_catch').get(2019)
        numeric=v.get(2019)
        selected.append({'unit_id':p.stem,'name':o['region_name'],'model_id':o['selected_model_id'],'updated':p.stem in units,'ge_status':v.get('status','unavailable'),'ge_ppr_tC_2019':numeric/9 if finite(numeric) else None,'covered_catch_tonnes':covered,'total_catch_tonnes':total,'coverage_pct':100*covered/total if finite(covered) and total else None,'mapped_taxa':len({x['taxon'] for x in records(b,'PPR','Matching') if x.get('group')}),'review_flags':review_flags(b),'source_note':o.get('source_note'),'workbook':r['workbook'],'workbook_sha256':sha(p)})
        print('Verified selected region',p.stem,flush=True)
    # The updater alone creates all new freshness hashes and generated central records.
    if '--verify-existing' not in sys.argv:update(ROOT,paths)
    current=read_book(destination)
    central_checks=[]
    for s,table in [('Papers','Papers'),('Models & coverage','Models')]:
        old=records(baseline,s,table);new=records(current,s,table)
        assert canonical(old)==canonical(new),(s,'central source metadata changed')
        central_checks.append(s+' exact content preserved')
    for s,blocks in baseline.items():
        for name,(h,_) in blocks.items():
            if 'unit_id' not in h:continue
            old=[r for r in records(baseline,s,name) if r.get('unit_id') not in units]
            new=[r for r in records(current,s,name) if r.get('unit_id') not in units]
            # Preserve by keys/content, independent of updater sort order.
            assert canonical(old)==canonical(new),(s,name,'unrelated region records changed')
    for p in paths:
        b=read_book(p)
        for sheet in ['Classic PPR','PPR']:
            expected_rows=records(b,sheet,'Annual')
            actual=[{k:v for k,v in r.items() if k!='unit_id'} for r in records(current,'Regional PPR','Annual') if r['unit_id']==p.stem and bool(r['model_id'])==(sheet=='PPR')]
            assert canonical(expected_rows)==canonical(actual),(p,sheet,'central numerical mismatch')
    report={'staged':stage,'workbook':destination.name,'regional_count':len(previous),'selected_count':len(selected),'unselected_preserved':sum(not r['selected_model_id'] for r in previous.values()),'updated_regions':sorted(units),'selected_regions':selected,'central_checks':central_checks+['All unrelated central records preserved by content','All updated regional annual cells match combined workbook','All selected IDs and rationales unchanged','All regional freshness/result checks pass'],'project_sha256':sha(destination)}
    (HERE/('STAGED_INTEGRATION_VERIFICATION.json' if stage else 'FINAL_INTEGRATION_VERIFICATION.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Central consolidation and preservation verified',flush=True)

if __name__=='__main__':main()
