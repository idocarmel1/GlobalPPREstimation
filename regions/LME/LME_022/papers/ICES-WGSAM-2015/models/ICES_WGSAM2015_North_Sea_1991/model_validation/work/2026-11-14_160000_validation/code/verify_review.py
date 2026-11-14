from pathlib import Path, PureWindowsPath
import json, hashlib, zipfile, sys, math, csv
from urllib.parse import unquote, urlsplit
from lxml import etree
from docx import Document
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve()
while not (ROOT/'Project.xlsx').exists():ROOT=ROOT.parent
BASE=ROOT/'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991/model_validation'
RUN=BASE/'work/2026-11-14_160000_validation'
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.validation_percentage_format import verify_report
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={};errors=[]
baseline=json.loads((RUN/'inputs/protected_hashes.json').read_text(encoding='utf-8'))
checks['protected_files']={p:sha(ROOT/p)==s for p,s in baseline.items()}
errors += [f'protected file changed: {p}' for p,ok in checks['protected_files'].items() if not ok]
report=BASE/'validation.docx'; appendix=BASE/'taxon_mapping.xlsx'
verify_report(report);checks['percentage_format']=True
doc=Document(report)
cells={row.cells[0].text:row.cells[1].text for row in doc.tables[0].rows[1:]}
assert cells['Open issues and next action']==''
assert 'MODEL VALIDATED' not in cells['Review and reproducibility']
assert 'MODEL DISQUALIFIED' not in cells['Review and reproducibility']
assert '____________________' in cells['Review and reproducibility']
assert cells['SPPR calculation']=='[Researcher calculation choices and notes]'
auto='\n'.join(v for k,v in cells.items() if k not in ['SPPR calculation','Review and reproducibility'])
assert 'in progress' not in auto and 'Awaiting' not in auto
checks['manual_review_unsigned']=True
with zipfile.ZipFile(ROOT/'tools/templates/validation.docx') as z:tpl={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(report) as z:
    parts={n:z.read(n) for n in z.namelist()}
    allowed={'word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml'}
    checks['template_parts_preserved']=all(parts.get(n)==b for n,b in tpl.items() if n not in allowed)
    assert checks['template_parts_preserved']
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    xml=etree.fromstring(parts['word/document.xml'])
    checks['docx_local_links']=[]
    rel=etree.fromstring(parts['word/_rels/document.xml.rels'])
    for e in rel:
        if not e.get('Type','').endswith('/hyperlink'):continue
        target=e.get('Target');p=urlsplit(target)
        if p.scheme in ('http','https','mailto'):continue
        assert not p.scheme and not PureWindowsPath(target).drive and not target.startswith(('/','\\'))
        resolved=(BASE/unquote(p.path)).resolve()
        assert resolved.exists(),target
        checks['docx_local_links'].append(target)
    for h in xml.xpath('//w:hyperlink',namespaces=ns):
        for r in h.xpath('./w:r',namespaces=ns):
            assert r.xpath('./w:rPr/w:color[@w:val="0563C1"]',namespaces=ns)
            assert r.xpath('./w:rPr/w:u[@w:val="single"]',namespaces=ns)
    for name,b in parts.items():
        if name.startswith('docProps/') and name.endswith('.xml'):
            properties=etree.fromstring(b)
            for prop in properties.iter():
                if etree.QName(prop).localname=='HyperlinkBase':assert not (prop.text or '').strip()
checks['docx_hyperlinks_blue_underlined']=True

audit=json.loads((BASE/'evidence/source_review/mapping_audit.json').read_text(encoding='utf-8'))
wb=load_workbook(appendix,data_only=False)
ws=wb['Taxon mapping']
assert ws.max_row==391 and ws.max_column==7
assert ws.freeze_panes=='B8'
for i,r in enumerate(audit['rows'],8):
    vals=[ws.cell(i,j).value for j in range(1,8)]
    assert vals[0]==r['taxon']
    assert vals[1]==('?' if r['tl'] is None else r['tl'])
    for a,b in [(vals[2],r['catch_tonnes']),(vals[3],r['simple_chain_ppr_tC'])]:assert math.isclose(a,b,rel_tol=1e-13,abs_tol=1e-9)
    assert vals[4]=='Unresolved' and vals[5]=='Unresolved'
assert math.isclose(sum(ws.cell(i,3).value for i in range(8,392)),audit['totals']['catch_tonnes'],rel_tol=1e-13)
assert math.isclose(sum(ws.cell(i,4).value for i in range(8,392)),audit['totals']['known_simple_chain_ppr_tC'],rel_tol=1e-13)
checks['appendix_rows_numbers_order']=True
diag=wb['SPPR diagnostics']
assert diag.max_row==271 and diag.max_column==7
assert diag.freeze_panes=='B8'
ledger=BASE.parent/'results/diagnostics/2026-11-14_validation/structural_zero/negative_entries.tsv'
with ledger.open(encoding='utf-8',newline='') as f:
    expected={(r['method'],int(r['source_id']),r['source_name'],int(r['group_id']),r['group_name']):(float(r['value']),float(r['comparison_tolerance'])) for r in csv.DictReader(f,delimiter='\t')}
actual={tuple(diag.cell(i,j).value for j in range(1,6)):tuple(diag.cell(i,j).value for j in (6,7)) for i in range(8,272)}
assert len(expected)==len(actual)==264
assert actual==expected
checks['appendix_all_264_negative_pairs_exact']=True
checks['source_model_hash']=sha(BASE.parent/'model.json')==audit['model_sha256']
assert checks['source_model_hash']
checks['files']={'report_sha256':sha(report),'appendix_sha256':sha(appendix)}
checks['report_ready_for_review']=not errors
checks['scientific_validation_complete']=False
checks['remaining_gap']='Selected-model mapping and allocation remain unassessed; diagnostic execution outcomes remain subject to their recorded restrictions.'
checks['errors']=errors
(RUN/'qa/final_review_verification.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'report_ready_for_review':not errors,'protected_files':len(baseline),'local_docx_links':len(checks['docx_local_links']),'appendix_taxa':len(audit['rows']),'errors':errors},ensure_ascii=False))
if errors:raise SystemExit(1)
