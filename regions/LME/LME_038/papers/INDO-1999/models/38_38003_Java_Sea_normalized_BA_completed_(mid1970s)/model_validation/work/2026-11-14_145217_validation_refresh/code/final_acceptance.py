from pathlib import Path
from zipfile import ZipFile
from urllib.parse import unquote, urlsplit
from lxml import etree as E
import hashlib, json, math, sys, shutil
import openpyxl

RUN = Path(__file__).resolve().parents[1]
V = RUN.parents[1]
ROOT = next(p for p in V.parents if (p / 'Project.xlsx').exists())
sys.path.insert(0, str(ROOT))
from tools.project_core.validation.researcher_review import read_report
from tools.project_core.validation.validation_percentage_format import verify_report, format_percent

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS = {'w': W, 'r': R}
tx = lambda e: ''.join(e.xpath('.//w:t/text()', namespaces=NS))
report, appendix = V/'validation.docx', V/'taxon_mapping.xlsx'
verify_report(report)
protected = read(RUN/'inputs/protected_hashes.json')
for path, digest in protected.items(): assert sha(ROOT/path) == digest, path

with ZipFile(report) as z:
    doc = E.fromstring(z.read('word/document.xml'))
    rels = E.fromstring(z.read('word/_rels/document.xml.rels'))
    part_hashes = {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
with ZipFile(RUN/'inputs/validation_before.docx') as z:
    before = E.fromstring(z.read('word/document.xml'))
    expected_parts = {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
changed = {n for n in part_hashes if part_hashes[n] != expected_parts[n]}
assert changed == {'word/document.xml','word/_rels/document.xml.rels'}
manual = ['SPPR calculation', 'Open issues and next action', 'Review and reproducibility', 'Selection rationale']
def field_cells(x):
    return {tx(tr.findall('w:tc',NS)[0]):tr.findall('w:tc',NS)[1] for tr in x.findall('.//w:tr',NS) if len(tr.findall('w:tc',NS))==2}
old_fields, fields = field_cells(before), field_cells(doc)
for name in manual:
    assert E.tostring(old_fields[name]) == E.tostring(fields[name]), name
try:
    read_report(ROOT,report,V.parent.name)
except ValueError as e:
    assert str(e) == read(RUN/'inputs/signoff_before.json')['message']
else: raise AssertionError('Draft must remain unsigned')

link_checks=[]
for rel in rels:
    if rel.get('Type') != R+'/hyperlink': continue
    target=rel.get('Target'); u=urlsplit(target)
    if u.scheme in ('https','http','mailto'): continue
    assert not u.scheme and not target.startswith(('\\','/')),target
    path=(V/unquote(u.path)).resolve()
    assert path.is_relative_to(ROOT) and path.exists(),target
    link_checks.append({'target':target,'exists':True,'within_repository':True})
for h in doc.findall('.//w:hyperlink',NS):
    for run in h.findall('.//w:r',NS):
        assert run.find('w:rPr/w:color',NS).get('{'+W+'}val')=='0563C1'
        assert run.find('w:rPr/w:u',NS).get('{'+W+'}val')=='single'

m=read(V/'evidence/mapping/validation_refresh_20261114.json')
tables=doc.findall('w:body/w:tbl',NS)
summary=next(t for t in tables if tx(t.find('w:tr/w:tc',NS))=='Overall confidence')
actual=[[tx(c) for c in tr.findall('w:tc',NS)] for tr in summary.findall('w:tr',NS)[1:]]
expected=[[x['label'],str(x['taxa']),format_percent(x['catch_percentage']),format_percent(x['ppr_percentage'])] for x in m['confidence_summary']]
assert actual==expected
assert sum(x['taxa'] for x in m['confidence_summary'])==181
for key in ['confidence_summary','membership_summary','allocation_summary']:
    assert math.isclose(sum(x['ppr_percentage'] for x in m[key]),100,abs_tol=1e-8)
vl=next(t for t in tables if tx(t.find('w:tr/w:tc',NS))=='Affected taxa')
names=[n.strip() for row in vl.findall('w:tr',NS)[1:] for n in tx(row.find('w:tc',NS)).split(';')]
assert len(names)==len(set(names))==36 and set(names)=={x['taxon'] for x in m['very_low_decisions']}

wb=openpyxl.load_workbook(appendix,data_only=False)
ws=wb['Taxon mapping']
header=next(row for row in ws if row[0].value=='Taxon name')
start=header[0].row+1
rows=list(ws.iter_rows(min_row=start,max_row=start+180,values_only=True))
assert [r[0] for r in rows]==[r['taxon'] for r in m['rows']]
for r,x in zip(rows,m['rows']):
    assert math.isclose(r[2],x['catch_tonnes'],abs_tol=1e-8)
    assert math.isclose(r[3],x['simple_chain_ppr_tC'],abs_tol=1e-7)
    assert r[5]==x['overall_confidence']
assert ws.freeze_panes and (ws.auto_filter.ref or any(ws.tables[n].autoFilter is not None and ws.tables[n].autoFilter.ref for n in ws.tables))
assert math.isclose(sum(r[3] for r in rows),m['total_simple_chain_ppr_tC'],abs_tol=1e-6)
wb.close()

# Actual relocated copies verify representative document, workbook and evidence links.
relocated=RUN/'qa/portability_copy'
representatives=[report,appendix,ROOT/'regions/LME/LME_038/LME_038.xlsx',V.parent/'model.json',V.parent/'model_notes.md',V/'evidence/mapping/validation_refresh_20261114.json',V.parent/'results/diagnostics/validation_20261114/direct_reports.json']
for src in representatives:
    dest=relocated/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
new_v=relocated/V.relative_to(ROOT)
for target in ['taxon_mapping.xlsx','../../../../../LME_038.xlsx','../model.json','../model_notes.md','../results/diagnostics/validation_20261114/direct_reports.json','evidence/mapping/validation_refresh_20261114.json']:
    assert (new_v/target).resolve().is_file(),target

e=V/'evidence'
promotions={
 'source_review/validation_refresh_20261114.json':RUN/'outputs/source_geography_review.json',
 'mapping/very_low_decisions_20261114.json':RUN/'outputs/very_low_table.json',
}
for dest,src in promotions.items():
    (e/dest).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,e/dest)
idx=e/'evidence_index.json'
index=read(idx) if idx.exists() else {'schema_version':1,'entries':[]}
index['validation_refresh_20261114']={
 'unit_id':'LME_038','model_id':V.parent.name,'reference_year':2019,'catch_basis':'landings',
 'operation':'Validation report and appendix refresh; authorized missing SPPR diagnostics; no decision registration or publication',
 'canonical_model_sha256':sha(V.parent/'model.json'),
 'report':{'path':'../validation.docx','sha256':sha(report)},
 'appendix':{'path':'../taxon_mapping.xlsx','sha256':sha(appendix)},
 'source_review':{'path':'source_review/validation_refresh_20261114.json','sha256':sha(e/'source_review/validation_refresh_20261114.json')},
 'mapping_review':{'path':'mapping/validation_refresh_20261114.json','sha256':sha(e/'mapping/validation_refresh_20261114.json')},
 'very_low_decisions':{'path':'mapping/very_low_decisions_20261114.json','sha256':sha(e/'mapping/very_low_decisions_20261114.json')},
 'direct_diagnostics':'../../results/diagnostics/validation_20261114/evidence_index.json',
 'diagnostic_configuration':'Audited pinned baseline; no EE floor; GE OK, TE WARN, With Egestion OK',
 'limits':['Macrozoobenthos source diet totals 0.660; 0.340 unexplained; runtime normalization does not repair canonical input','28 BA completions remain computational, not measured','Whole diet matrix primary-source fidelity not newly established','Geography remains low-confidence prose-bound reconstruction','No researcher decision registered; regional outputs and project views unchanged'],
 'verification':'../work/2026-11-14_145217_validation_refresh/qa/final_acceptance.json'
}
idx.write_text(json.dumps(index,indent=2),encoding='utf-8')
result={
 'status':'passed','report_sha256':sha(report),'appendix_sha256':sha(appendix),
 'protected_hashes_unchanged':protected,'manual_cells_byte_identical':manual,
 'unsigned_parser_state_preserved':True,'changed_docx_parts':sorted(changed),
 'all_docx_links':link_checks,'visible_links_blue_underlined':True,'relative_link_relocation_checked':True,
 'word_excel_arithmetic_reconciles':True,'taxa':181,'very_low_taxa_once':36,
 'current_diagnostics_complete':read(V.parent/'results/diagnostics/validation_20261114/completeness.json')['complete'],
 'render':{'renderer':'Separate hidden Word instance; PDF rasterized with bundled pypdfium2','pages':9,'all_pages_visually_inspected':True,'issues':[]},
 'independent_content_review':read(RUN/'qa/independent_report_review.json'),
 'appendix_verification':read(RUN/'qa/appendix_verification.json')['visual_review'],
}
(RUN/'qa/final_acceptance.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','report_sha256','appendix_sha256','word_excel_arithmetic_reconciles','taxa','very_low_taxa_once','current_diagnostics_complete']},indent=2))
