"""Verify and index the exact report/appendix review package without adoption."""
from pathlib import Path,PureWindowsPath
import json,hashlib,zipfile,sys,os,shutil
from urllib.parse import urlsplit,unquote
from lxml import etree as E
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
RUN=Path(__file__).resolve().parents[1];BASE=RUN.parents[1]
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.validation_percentage_format import verify_report
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
W='{'+NS['w']+'}'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REPORT=BASE/'validation_review.docx'
data=json.loads((BASE/'evidence/mapping/mapping_decisions.json').read_text(encoding='utf8'))
render=json.loads((RUN/'qa/visual_review.json').read_text(encoding='utf8'))
assert render['all_pages_inspected'] and render['all_pages_clean']
assert render['docx_sha256']==sha(REPORT)
assert sha(BASE/'validation.docx')==sha(RUN/'inputs/validation_before.docx')
content=json.loads((RUN/'outputs/report_mapping_content.json').read_text(encoding='utf8'))
assert content['mapping_decisions_sha256']==sha(BASE/'evidence/mapping/mapping_decisions.json')
independent=json.loads((RUN/'qa/independent_review.json').read_text(encoding='utf8'))
assert independent['review_stage']=='final_hash_verified'
assert independent['passed'] is True
assert not independent['mapping_checks']['structural_arithmetic_errors']
assert independent['appendix_check']['sha256']==sha(BASE/'taxon_mapping.xlsx')
assert independent['appendix_check']['taxon_count']==384
for rel,expected in independent['input_hashes'].items():
    assert sha(ROOT/rel)==expected,('Independent QA input changed',rel)
changed=[]
for rel,expected in data['input_sha256'].items():
    if sha(ROOT/rel)!=expected:changed.append(rel)
assert not changed,('Mapping inputs changed',changed)
diagnostics=json.loads((RUN/'qa/diagnostic_review.json').read_text(encoding='utf8'))
SCOT=ROOT/'regions/LME/LME_022/papers/NS-2025/models/22_20251990_East_Coast_of_Scotland_(1991-1995)'
assert sha(SCOT/'model_validation/validation.docx')=='500a5734b3e6de8924af64c5b0abf59ed0c368f91fd1b817dabda4ff79e3fbf5'
assert sha(SCOT/'model_validation/taxon_mapping.xlsx')=='c3cbe2fd6ba79229dbfb446ab196a5f39b00eed3705c3540da56e3dc8b6a091c'
assert sha(SCOT/'model.json')=='5cda503a847a6ea9bdcda077c184ac20119e0d8b47b064f93b72b72e3d7df691'
verify_report(REPORT)
with zipfile.ZipFile(REPORT) as z:
    document=E.fromstring(z.read('word/document.xml'))
    rels=E.fromstring(z.read('word/_rels/document.xml.rels'))
    xml_parts={n:z.read(n) for n in z.namelist() if n.endswith('.xml')}
linked=[]
for rel in rels:
    if rel.get('TargetMode')!='External':continue
    target=rel.get('Target','');parsed=urlsplit(target)
    if parsed.scheme in ['https','http','mailto']:continue
    assert not parsed.scheme and not PureWindowsPath(target).drive and not target.startswith(('/','\\'))
    p=(BASE/unquote(parsed.path)).resolve()
    assert p.is_relative_to(ROOT) and p.exists(),target
    linked.append({'target':target,'resolved_repository_path':p.relative_to(ROOT).as_posix()})
for link in document.xpath('.//w:hyperlink',namespaces=NS):
    for r in link.findall(W+'r'):
        if not ''.join(r.xpath('.//w:t/text()',namespaces=NS)):continue
        assert r.find(W+'rPr/'+W+'color').get(W+'val')=='0563C1'
        assert r.find(W+'rPr/'+W+'u').get(W+'val')=='single'
assert not any(b'HyperlinkBase' in b and b'C:' in b for b in xml_parts.values())
proof=json.loads((RUN/'qa/report_patch_verification.json').read_text(encoding='utf8'))
assert proof['after_sha256']==sha(REPORT)
review={'scope':'ICES model-local review package; mapping proposals only; no adoption or renewed selection',
        'report_sha256':sha(REPORT),'appendix_sha256':sha(BASE/'taxon_mapping.xlsx'),
        'mapping_sha256':sha(BASE/'evidence/mapping/mapping_decisions.json'),
        'links':linked,'relative_links_resolve':True,'hyperlink_format_verified':True,
        'manual_xml_preserved':proof['manual_cells_unchanged'],'percentage_format_passed':True,
        'rendered_pages':render['pages'],'all_pages_inspected':True,'mapping_inputs_unchanged':True,
        'independent_final_appendix_qa_passed':True,
        'scotland_signed_report_appendix_model_unchanged':True,'scientific_rerun':False,
        'selection_change':False,'researcher_decision_registration':False,
        'regional_or_Project_workbook_write':False,'map_trends_source_refresh':False}
(RUN/'qa/final_review_verification.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf8')

index_path=BASE/'evidence/evidence_index.json'
backup=RUN/'inputs/evidence_index_before.json'
if not backup.exists():shutil.copy2(index_path,backup)
index=json.loads(backup.read_text(encoding='utf8'))
index['run_id']=RUN.name
index['review_operation']='Complete local mapping proposal and validation review; retained diagnostic configurations; awaiting researcher review and alignment authorization.'
index['adoption_state']='proposed_not_adopted'
index['required_roles']=sorted(set(index['required_roles'])|{'mapping_source_evidence','mapping_independent_qa','mapping_package_qa','report_verification','report_visual_verification'})
artifacts=[]
for a in index['artifacts']:
    if a['role'] in ['report','taxon_appendix','mapping_decisions']:continue
    if a['role']=='mapping_audit':a['role']='historical_mapping_audit'
    if a['role']=='comparison':a['role']='historical_comparison_after_loader_repair'
    artifacts.append(a)
def add(role,path):
    p=Path(path)
    artifacts.append({'role':role,'path':os.path.relpath(p,BASE/'evidence').replace('\\','/'),'sha256':sha(p),'availability':'present'})
add('report',REPORT);add('taxon_appendix',BASE/'taxon_mapping.xlsx')
add('mapping_decisions',BASE/'evidence/mapping/mapping_decisions.json')
add('mapping_audit',BASE/'evidence/mapping/report_handoff.json')
add('comparison',BASE/'evidence/source_review/validation_comparison_20261114.json')
add('mapping_independent_qa',RUN/'qa/independent_review.json')
add('mapping_package_qa',RUN/'qa/final_mapping_package_qa.json')
add('report_verification',RUN/'qa/final_review_verification.json')
add('report_visual_verification',RUN/'qa/visual_review.json')
add('mapping_method_exposure',RUN/'qa/proposed_mapping_method_exposure.json')
for p in sorted((RUN/'inputs/source_research').glob('*.json')):add('mapping_source_evidence',p)
for p in sorted((BASE/'evidence/mapping').glob('*.json')):
    if p.name not in ['mapping_decisions.json','report_handoff.json']:add('mapping_supporting_evidence',p)
index['artifacts']=artifacts
index['reconciliation']={'mapping_full_taxon_universe':True,'report_appendix_same_mapping_decisions':True,'diagnostic_source_matrices_verified':True,'manual_cells_preserved':True,'final_report_all_pages_inspected':True,'relative_links_resolve':True}
index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'report_sha256':review['report_sha256'],'appendix_sha256':review['appendix_sha256'],'mapping_sha256':review['mapping_sha256'],'pages':render['pages'],'linked_local_targets':len(linked),'index_artifact_count':len(artifacts)},indent=2))
