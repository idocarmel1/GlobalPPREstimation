"""Register the signed LME049 decision only; map/trends belong to Validate EEZ_598."""
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
import hashlib, json, shutil, sys

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
from tools.project_core.registry.discovery import region_directory,resolve_model
from tools.project_core.registry.writes import central_lock
from tools.project_core.validation.researcher_review import (
    _register_review,read_report,approved_review,table_rows,sheet_xml,FIELDS,STATUS)
from tools.project_core.validation.validation_percentage_format import verify_report

UNIT='LME_049'
MID='49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
REGION=region_directory(ROOT,UNIT)
MODEL=resolve_model(REGION,MID).parent
REPORT=MODEL/'model_validation/validation.docx'
PROJECT=ROOT/'Project.xlsx'
RUN=Path(__file__).resolve().parents[1]
EVIDENCE=MODEL/'model_validation/evidence/source_review/researcher_registration_20261114.json'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):return path.relative_to(ROOT).as_posix()
def rows(path,sheet,table):
    with ZipFile(path) as z:return [r for _,r in table_rows(z,sheet,table)[3]]
def minimal_review_book():
    out={}
    for sheet,table in [('Overview','Settings'),('Selected model groups','Groups')]:
        r=rows(REGION/(UNIT+'.xlsx'),sheet,table);h=list(r[0])
        out.setdefault(sheet,{})[table]=(h,[[x.get(k) for k in h] for x in r])
    return out

name,date,source_summary=read_report(ROOT,REPORT,MID)
assert source_summary.get('status',STATUS)==STATUS
verify_report(REPORT)
assert name=='Ido Carmel' and date=='2026-11-14'
assert 'Toothed whales (all)' in source_summary['sections'][2]['rows'][0]['text']
assert 'no model groups are excluded' not in source_summary['note']
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(REPORT) as z:
    dom=ET.fromstring(z.read('word/document.xml'))
    document_text='\n'.join(t.text or '' for t in dom.findall('.//w:t',ns))
assert 'EE floor 0.1' in document_text
assert 'exports all seabird group 3 mortality and egestion outside detritus' in document_text
groups=rows(REGION/(UNIT+'.xlsx'),'Selected model groups','Groups')
resolved=[int(float(g['seq'])) for g in groups if g['group_name']=='Toothed whales (all)']
assert resolved==[2]
settings={r['field']:r['value'] for r in rows(REGION/(UNIT+'.xlsx'),'Overview','Settings')}
assert (settings.get('results_model_id') or settings.get('selected_model_id'))==MID
protected=[REPORT,MODEL/'model.json',MODEL/'model_notes.md',MODEL/'model_validation/taxon_mapping.xlsx',REGION/(UNIT+'.xlsx')]
protected += [ROOT/'interactive_map'/n for n in ['index.html','trends.html','sources.html'] if (ROOT/'interactive_map'/n).exists()]

with central_lock(ROOT):
    protected_hashes={rel(p):sha(p) for p in protected}
    # Snapshot the live file under the same lock as the write, preserving peers' updates.
    backup=RUN/'inputs/Project_before_registration.xlsx'
    backup.parent.mkdir(parents=True,exist_ok=True)
    assert not backup.exists(),'Refusing to replace an existing pre-registration snapshot'
    shutil.copyfile(PROJECT,backup)
    before=rows(PROJECT,'Models & coverage','Models')
    matching=[r for r in before if (r['unit_id'],r['model_id'])==(UNIT,MID)]
    assert len(matching)==1
    values=_register_review(PROJECT,REPORT,UNIT,MID,resolved)
    after=rows(PROJECT,'Models & coverage','Models')
    before_by={(r['unit_id'],r['model_id']):r for r in before}
    after_by={(r['unit_id'],r['model_id']):r for r in after}
    assert before_by.keys()==after_by.keys()
    changed=[]
    for key in before_by:
        a,b=before_by[key],after_by[key]
        if a!=b:changed.append(key)
        for field in set(a)|set(b):
            if a.get(field)!=b.get(field):assert key==(UNIT,MID) and field in FIELDS,(key,field)
    assert changed==[(UNIT,MID)],changed
    metadata=after_by[UNIT,MID]
    reviewed=approved_review(ROOT,metadata,minimal_review_book())
    assert reviewed['status']==STATUS
    assert reviewed['excluded_group_ids']==['Toothed whales (all)']
    assert 'toothed whales (all)' in reviewed['note']
    assert 'no model groups are excluded' not in reviewed['note']
    assert reviewed['sections']==source_summary['sections']
    assert metadata['validation_report_sha256']==sha(REPORT)
    assert metadata['reviewed_model_sha256']==sha(MODEL/'model.json')
    assert all(sha(ROOT/p)==h for p,h in protected_hashes.items())
    with ZipFile(backup) as za,ZipFile(PROJECT) as zb:
        assert set(za.namelist())==set(zb.namelist())
        changed_parts=[n for n in za.namelist() if za.read(n)!=zb.read(n)]
        target_part=sheet_xml(zb,'Models & coverage')[0]
        assert all(n==target_part or n=='xl/styles.xml' or n.startswith('xl/tables/') for n in changed_parts),changed_parts
    evidence={'schema_version':1,'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'unit_id':UNIT,'model_id':MID,'status':STATUS,'researcher_name':name,'review_date':date,
        'report_path':rel(REPORT),'report_sha256':sha(REPORT),'canonical_sha256':sha(MODEL/'model.json'),
        'excluded_seq':resolved,'excluded_group_ids':reviewed['excluded_group_ids'],
        'condition_from_signed_report_and_user':{'use_ee_floor':True,'ee_floor':.1,'seabird_M0_and_egestion_exported':True},
        'exclusion_semantics':'Exclude group from displayed/aggregated PPR using existing researcher policy. Retain the trophic network and all scientific inputs.',
        'whale_M0_export_sensitivity_adopted':False,
        'project_before_path':rel(backup),'project_before_sha256':sha(backup),'project_after_sha256':sha(PROJECT),
        'changed_workbook_parts':changed_parts,'changed_model_rows':changed,
        'registered_review':reviewed,'protected_files':protected_hashes,
        'checks':{'only_target_review_metadata_changed':True,'signed_source_unchanged':True,
            'regional_results_unchanged':True,'map_trends_sources_unchanged':True,'source_to_registered_review_equal':True},
        'publication_handoff':{'chat':'Validate EEZ_598','thread_id':'01a1da5c-5c4b-7730-ad60-9e8e8e9e9889',
            'approved_diagnostic_package':rel(MODEL/'results/diagnostics/ee_floor_seabird_accounting_20261114'),
            'methods_inventory':rel(MODEL/'results/diagnostics/ee_floor_seabird_accounting_20261114/inventory/evidence_index.json'),
            'status':'Project registration complete; regional adoption and map/trends publication delegated.',
            'warning':'Regional workbook still holds historical provisional results; do not relabel them as the approved EE-floor scenario.'}}
    EVIDENCE.parent.mkdir(parents=True,exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:evidence[k] for k in ['status','researcher_name','review_date','excluded_group_ids','project_before_sha256','project_after_sha256','changed_workbook_parts','checks']},ensure_ascii=False,indent=2),flush=True)
