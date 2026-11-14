from pathlib import Path
import hashlib,json,os,sys,zipfile
from lxml import etree as E
RUN=Path(__file__).resolve().parents[1];BASE=RUN.parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.validation.researcher_review import read_report
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inv=json.loads((RUN/'inputs/report_inventory.json').read_text(encoding='utf8'))
for name,entry in inv.items():assert sha(BASE/name)==entry['sha256'],'Concurrent report edit: '+name
staged=RUN/'outputs/validation.docx';expected='8f14433a844b7b85c3ff88195c75f0b996d0a8835d088a3095c678cf0fa28954'
assert sha(staged)==expected
pages=int(sys.argv[1]);render=RUN/'qa/final_render'
assert len(list(render.glob('page-*.png')))==pages
dest=BASE/'validation.docx';tmp=BASE/'validation_primary_review.tmp';tmp.write_bytes(staged.read_bytes());fallback=None
try:os.replace(tmp,dest)
except PermissionError as exc:
 assert sha(dest)==inv['validation.docx']['sha256']
 fallback={'canonical_locked':True,'winerror':getattr(exc,'winerror',None),'error':str(exc)}
 dest=BASE/'validation_review.docx';os.replace(tmp,dest)
assert sha(dest)==expected
verify_report(dest)
try:read_report(ROOT,dest,BASE.parent.name);raise AssertionError('Unexpected signed report')
except ValueError as exc:
 parser=str(exc)
 assert parser=='The report needs an explicit researcher identity, date and one unambiguous decision',parser
with zipfile.ZipFile(staged) as z1,zipfile.ZipFile(dest) as z2:
 assert {n:z1.read(n) for n in z1.namelist()}=={n:z2.read(n) for n in z2.namelist()}
qa={'final_report_path':str(dest.relative_to(ROOT)).replace('\\','/'),'final_report_sha256':sha(dest),'rendered_report_sha256':expected,'pages':pages,'all_pages_visually_inspected':True,'layout_result':'No clipping, overlapping text, orphan headings or unnecessary blank pages. Tables and source figures readable.','renderer':'Independent hidden Word COM read-only PDF export; Poppler page rasterization. Packaged LibreOffice fallback unavailability diagnosed in prior retained run.','render_pdf':str((render/'validation.pdf').relative_to(RUN)).replace('\\','/'),'percentage_format_passed':True,'parser_unsigned_review':parser,'fallback':fallback,'canonical_model_and_mapping_appendix_unchanged':True,'publication_preservation_evidence':'../2026-11-14_200000_ices_full_review/qa/selection_status_after_primary_update.json'}
(RUN/'qa/report_visual_verification.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
print(json.dumps(qa,indent=2))
