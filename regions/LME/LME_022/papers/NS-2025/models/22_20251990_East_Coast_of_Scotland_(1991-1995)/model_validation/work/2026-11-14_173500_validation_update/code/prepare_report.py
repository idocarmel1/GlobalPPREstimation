from pathlib import Path
import hashlib,json,shutil,sys,zipfile
from lxml import etree as E
from docx import Document
sys.stdout.reconfigure(encoding='utf-8')
run=Path(__file__).resolve().parents[1]; model=run.parents[2]; root=next(p for p in run.parents if (p/'Project.xlsx').exists())
for p in ['inputs','outputs','qa']: (run/p).mkdir(exist_ok=True)
report=model/'model_validation/validation.docx'
original=run/'inputs/validation_before.docx'
if not original.exists(): shutil.copyfile(report,original)
sys.path.insert(0,str(root))
from tools.project_core.validation.researcher_review import read_report
def parser(p):
    try: return {'parsed':read_report(root,p,model.name)}
    except Exception as e:return {'exception':type(e).__name__,'message':str(e)}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def txt(e):return ''.join(e.itertext())
with zipfile.ZipFile(original) as z:
    x=E.fromstring(z.read('word/document.xml'))
    manual={}
    for row in x.findall('.//w:tr',ns):
        c=row.findall('w:tc',ns)
        if len(c)==2 and txt(c[0]) in ['SPPR calculation','Open issues and next action','Review and reproducibility']:
            manual[txt(c[0])]=E.tostring(c[1]).decode()
    manifest={p:hashlib.sha256(z.read(p)).hexdigest() for p in z.namelist()}
qa={'sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'parts':manifest,'manual_cells':manual,'signoff_parser':parser(report)}
(run/'qa/before_report.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False),encoding='utf-8')
doc=Document(original)
sections=[{'width':s.page_width,'height':s.page_height,'left_margin':s.left_margin,'right_margin':s.right_margin,'top_margin':s.top_margin,'bottom_margin':s.bottom_margin} for s in doc.sections]
(run/'inputs/artifact.md').write_text('# Scotland report preservation contract\n\nExisting report is the content/style authority; current template field order applies. Preserve all package parts except word/document.xml and its relationship part. Preserve manual cells (SPPR calculation, Open issues, Review) exactly, images, styles, numbering, section geometry, existing useful links and unsuperseded prose. Update candidate identity, scientific extraction/GE/TE/Other findings, selection distinction, coverage format and current missing Very low table. Merge two main Field/Entry grids into one flowing grid, with GE/TE before SPPR. Keep geography/source images and their original captions; update only explicit contextual wording when necessary. No fabricated researcher decision/date.\n\nSection geometry in EMU: '+json.dumps(sections)+'\n\nSource SHA256: '+qa['sha256']+'\n',encoding='utf-8')
print(json.dumps({'source':str(original),'signoff':qa['signoff_parser'],'manual_fields':list(manual),'sections':sections},ensure_ascii=False))
