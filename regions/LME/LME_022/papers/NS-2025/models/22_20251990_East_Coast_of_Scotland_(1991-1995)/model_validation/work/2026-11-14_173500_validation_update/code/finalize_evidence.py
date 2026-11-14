from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,zipfile
from lxml import etree as E
from openpyxl import load_workbook
sys.stdout.reconfigure(encoding='utf-8')
run=Path(__file__).resolve().parents[1];model=run.parents[2];validation=model/'model_validation';root=next(p for p in run.parents if (p/'Project.xlsx').exists());sys.path.insert(0,str(root))
from tools.project_core.validation.validation_percentage_format import verify_report
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
verify_report(validation/'validation.docx')
assert sha(model/'model.json')=='5cda503a847a6ea9bdcda077c184ac20119e0d8b47b064f93b72b72e3d7df691'
assert sha(validation/'taxon_mapping.xlsx')=='c3cbe2fd6ba79229dbfb446ab196a5f39b00eed3705c3540da56e3dc8b6a091c'
region=root/'regions/LME/LME_022/LME_022.xlsx'
wb=load_workbook(region,read_only=True,data_only=False)
settings={r[0]:r[1] for r in wb['Overview'].iter_rows(values_only=True) if len(r)>1 and r[0] is not None}
assert settings['selected_model_id']=='ICES_WGSAM2015_North_Sea_1991';wb.close()
with zipfile.ZipFile(validation/'validation.docx') as z:
    x=E.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    review=[c for r in x.findall('.//w:tr',ns) if len(c:=r.findall('w:tc',ns))==2 and ''.join(c[0].itertext())=='Review and reproducibility'][0][1]
    assert 'MODEL VALIDATED' not in ''.join(review.itertext()) and 'MODEL DISQUALIFIED' not in ''.join(review.itertext())
notes=model/'model_notes.md'; original_notes=notes.read_text(encoding='utf-8')
marker='## Runtime correction prepared for review on 14 November 2026'
if marker not in original_notes:
    head,rest=original_notes.split('\n',1)
    notes.write_text(head+'\n\n'+marker+'\n\n'
    'The current regional Overview selects `ICES_WGSAM2015_North_Sea_1991`. This Scotland model is the explicitly named correction candidate; no regional selection or researcher decision is changed. The historical administrative/source descriptions below are retained as historical evidence.\n\n'
    'Canonical publication inputs remain unchanged. A derived runtime variant retains all ecological groups and the computational import, removes only Seabirds self-feeding, proportionally redistributes that share to every remaining prey including Detritus, and refreshes predation at retained consumption. Only 13 affected BA entries whose ledger provenance and archived values prove prior loader derivation are recomputed; observed/manual/uncertain entries are not altered. No EE floor, broad balancing or changes to production, mortality, catch or migration are introduced.\n\n'
    'Fresh historical-engine diagnostics are GE **OK**, TE **WARN**, and With Egestion **OK**. All strict model/SPPR balance flags are true, with no negative or nonfinite SPPR entries. The original TE self-loop divergence is removed. Near-zero TE warnings for Seabirds, Seals and Cetaceans and TE\'s no-detritus-recycling convention remain. These results support review, not registered approval or adoption into regional/map/trend outputs.\n\n'
    '[Correction, provenance and exact before/after cells](results/diagnostics/2026-11-14_171200_seabird_derived_ba/correction_summary.md) · [Full execution evidence](results/diagnostics/2026-11-14_171200_seabird_derived_ba/evidence_index.json) · [Current review report](model_validation/validation.docx) · [Candidate mapping appendix](model_validation/taxon_mapping.xlsx).\n\n'
    '## Preserved historical extraction and administrative record\n'+rest,encoding='utf-8')
    (run/'qa/model_notes_change.json').write_text(json.dumps({'before_sha256':hashlib.sha256(original_notes.encode('utf-8')).hexdigest(),'after_sha256':sha(notes),'change':'Added current candidate/runtime review section; preserved entire existing historical text in order.'},indent=2),encoding='utf-8')
for name in ['independent_runtime_qa.json','independent_runtime_hash_qa.json']:
    assert (run/'qa'/name).exists(),name
pages=sorted((run/'qa/final_render').glob('page-*.png'));assert len(pages)==9
qa={'created_at':datetime.now(timezone.utc).isoformat(),'region_id':'LME_022','candidate_model_id':model.name,'actual_selected_model_id':settings['selected_model_id'],
    'scope':'Current-template candidate report and linked appendix plus explicitly authorized derived runtime correction. No registration or adoption.',
    'methods':{'GE':'OK','TE':'WARN','With Egestion':'OK'},
    'strict_model_and_sppr_balance_flags':'true for all three methods; distinct from graded network status',
    'render':{'engine':'Independent hidden Microsoft Word instance, output opened read-only, macros/alerts/automatic-link updates disabled; only own instance closed','packaged_renderer_unavailable':'Bundled Windows LibreOffice absent; fallback permitted by project document-production reference','all_pages_visually_inspected':list(range(1,10)),'page_count':9,'findings':'No clipping, missing glyphs, unreadable source figures, broken tables, stranded headings or accidental blank pages.'},
    'preservation':{'canonical_model_sha256':sha(model/'model.json'),'regional_workbook_sha256':sha(region),'regional_workbook_same_as_initial_overview_inspection':sha(region)=='60830e20d8751993c4eb0e87a3f08e7a26ddf7e942da45d73d84e76e3fbff829','manual_report_cells':'exact XML preserved','docx_untouched_package_parts':'all except document.xml and document.xml.rels preserved byte-for-byte','researcher_decision':'unsigned and unregistered'},
    'deliverables':{'docx_sha256':sha(validation/'validation.docx'),'xlsx_sha256':sha(validation/'taxon_mapping.xlsx')},
    'remaining_limitations':['TE near-zero-efficiency warnings for seabirds, seals and cetaceans; TE no-detritus-recycling convention.','Scotland geographic coverage approximately 37–42% of North Sea; historical 1991–1995 transfer to 1950–2019 catch.','Source excludes discards; regional total catch includes them.','Retained candidate mapping, 110 Very low taxa and 12 unresolved freshwater labels; current regional Matching empty.','Older result manifest unknown historical execution remains unchanged; new pinned execution evidence does not rewrite that limitation.'],
    'shared_write_assertion':'This task performed no Project.xlsx, regional workbook, generated map/trends/sources, selection, shared engine/helper or shared instruction writes. Shared preexisting/concurrent edits are not attributed to this task.'}
(run/'qa/final_review.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False),encoding='utf-8')
indexpath=validation/'evidence/evidence_index.json'
index=json.loads(indexpath.read_text(encoding='utf-8')) if indexpath.exists() else {'schema_version':1,'role':'Review evidence index; not selection, settings or approval authority','retained_source_review':'source_review/'}
targets=[validation/'validation.docx',validation/'taxon_mapping.xlsx',model/'model_notes.md',model/'model.json',model/'results/diagnostics/2026-11-14_171200_seabird_derived_ba/evidence_index.json',model/'results/diagnostics/2026-11-14_171200_seabird_derived_ba/run_manifest.json',run/'qa/final_review.json',run/'qa/report_structure.json',run/'qa/independent_runtime_qa.json',run/'qa/independent_runtime_hash_qa.json',validation/'work/2026-11-14_180000_appendix_review/qa/final_checks.json',validation/'work/2026-11-14_180000_appendix_review/outputs/report_handoff.json']
import os
index['scotland_seabird_review_20261114']={'candidate_model_id':model.name,'created_at':qa['created_at'],'source_unchanged':True,'researcher_decision_registered':False,'entries':[{'path':Path(os.path.relpath(p,indexpath.parent)).as_posix(),'sha256':sha(p)} for p in targets]}
indexpath.write_text(json.dumps(index,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'report_sha256':sha(validation/'validation.docx'),'appendix_sha256':sha(validation/'taxon_mapping.xlsx'),'pages_inspected':9,'selected_model':settings['selected_model_id'],'regional_hash_unchanged':qa['preservation']['regional_workbook_same_as_initial_overview_inspection'],'review':'ready for human review; unregistered'},ensure_ascii=False))
