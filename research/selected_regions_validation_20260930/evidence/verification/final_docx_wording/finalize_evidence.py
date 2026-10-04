"""Retain completed visual notes and a fresh final hash/OOXML guard without changing DOCXs."""
from pathlib import Path
import json, hashlib, zipfile, datetime
from lxml import etree
from patch_and_prove import ROOT, EVIDENCE, CHANGES, NS, zip_index

def sha(data): return hashlib.sha256(data).hexdigest()
proof=json.loads((EVIDENCE/'patch_proof.json').read_text())
comparison=json.loads((EVIDENCE/'render_comparison.json').read_text())
notes={
 'EEZ_598':'Page 1: completed-review sentence fits the existing Region cell; Regional workbook and source/model links remain blue and underlined; table boundaries and manual calculation field are clean.',
 'LME_026':'Page 1: shortened Mediterranean title is clear and fits the existing title line; table text, links, and manual calculation field are clean.',
 'LME_036':'Page 1: completed-review opening sentence is clear; later sentences including Estimates remain provisional remain visible and unchanged; table and blue underlined links are clean.',
 'LME_038':'Page 2: Regional review completed appears above the existing diagnostics table; provisional scientific caveats, open-issues field, and researcher name/date placeholders remain visible; blue underlined link is preserved.',
 'LME_049':'Page 1: Regional review completed remains below the existing title, on its original status line; source caveats, table, links, and manual calculation field are clean.',
 'LME_052':'Page 1: Regional review completed remains below the existing title, on its original status line; scientific caveats, table, blue underlined links, and manual calculation field are clean.',
}
final=[]
for item,render in zip(proof['files'],comparison['files']):
 unit=item['unit']; assert render['unit']==unit
 path=ROOT/item['path']; data=path.read_bytes(); assert sha(data)==item['after_sha256']
 before=(EVIDENCE/'before'/f'{unit}.docx').read_bytes(); assert sha(before)==item['before_sha256']
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  xml=z.read('word/document.xml')
  assert xml==(EVIDENCE/'xml'/f'{unit}.after.document.xml').read_bytes()
  original_xml=(EVIDENCE/'xml'/f'{unit}.before.document.xml').read_bytes()
  old,new=CHANGES[unit]
  assert xml.replace(new.encode(),old.encode(),1)==original_xml
  assert old.encode() not in xml
 br,_,_,_=zip_index(before); ar,_,_,_=zip_index(data)
 assert len(br)==len(ar)
 for b,a in zip(br,ar):
  assert b['name']==a['name']
  if b['name']!='word/document.xml': assert b['local_raw']==a['local_raw']
 render['visual_inspection_pending']=False
 render['visually_inspected']=True
 render['no_clipping_or_overlap']=True
 render['blue_underlined_hyperlinks_visually_preserved']=True
 render['visual_observations']=notes[unit]
 final.append({'unit':unit,'path':item['path'],'before_sha256':item['before_sha256'],'final_sha256':sha(data),
               'final_hash_rechecked_after_native_word_render_and_visual_qa':True,
               'changed_page':render['inspected_page'],'before_pages':render['before_page_count'],'after_pages':render['after_page_count']})
comparison['visual_qa_complete']=True
comparison['visual_qa_scope_limit']='Brief appearance inspection of only the six affected pages, as authorized. All 37 pages were compared for page text, dimensions and exported links; all 31 unaffected pages also matched character geometry, font and color exactly. No scientific reruns.'
(EVIDENCE/'render_comparison.json').write_text(json.dumps(comparison,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
report={'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'Six automatic-status wording text nodes only; no scientific or manual-review content changed',
 'files':final,'total_pages':sum(x['after_pages'] for x in final),
 'all_six_affected_pages_visually_inspected':True,'pagination_preserved':True,
 'all_31_unaffected_pages_character_geometry_font_and_color_exact':True,
 'all_158_hyperlink_elements_xml_exact':sum(x['hyperlink_count'] for x in proof['files'])==158,
 'all_manual_researcher_field_xml_exact':True,
 'all_other_raw_compressed_zip_entries_exact':True,
 'runtime':r'C:\Users\idoca\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',
 'retained_evidence':['patch_proof.json','render_comparison.json','native_word_render.log','before/','xml/','render/'],
 'limits':'Native Word PDF export, bundled Poppler rendering, and brief inspection of changed pages. No scientific parameter/workbook/index/handoff/log/graph/Git edits or reruns.'}
(EVIDENCE/'final_verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
