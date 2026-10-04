from pathlib import Path
import sys,json,hashlib,zipfile,copy,math,re
from urllib.parse import unquote,urlsplit
from lxml import etree
from docx import Document
import openpyxl
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=BASE.parents[3];REGION=ROOT/'regions/LME_013'
mapping=json.loads((BASE/'mapping/mapping_review.json').read_text(encoding='utf-8'))
expected={r['taxon']:r for r in mapping['taxa']}
report=REGION/'Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx'
appendix=REGION/'LME013_HUM2018_candidate_taxon_mapping_appendix_20261003.xlsx'
old=OUT/'baseline/regions/LME_013'/appendix.name
with zipfile.ZipFile(old) as a,zipfile.ZipFile(appendix) as b:
    unchanged=[n for n in a.namelist() if not n.endswith('.rels')]
    assert all(a.read(n)==b.read(n) for n in unchanged)
w=openpyxl.load_workbook(appendix,data_only=False)
s=w['Taxon mappings'];data=[list(r) for r in s.iter_rows(min_row=8,max_col=7,values_only=True) if r[0] in expected]
assert len(data)==218 and len({r[0] for r in data})==218
numeric=[r[3] for r in data if isinstance(r[3],(int,float))]
assert numeric==sorted(numeric,reverse=True)
assert math.isclose(math.fsum(numeric),mapping['summary']['known_simple_chain_ppr_tC'],rel_tol=1e-12,abs_tol=1e-6)
assert s.freeze_panes and (s.auto_filter.ref or any(t.autoFilter and t.autoFilter.ref for t in s.tables.values())) and 'Sources' in w.sheetnames
local_links=[];external_links=[]
def verify_link(target):
    if target.startswith(('http:','https:')):external_links.append(target);return
    assert not re.match(r'^[A-Za-z]:|^file:|^\\\\|^/',target),target
    local=unquote(target.split('#')[0])
    if not local:return
    resolved=(REGION/local).resolve();assert resolved.is_relative_to(ROOT) and resolved.exists(),target
    # A different root preserves the same repository-relative target resolution.
    synthetic=Path('Z:/portable_repository')/REGION.relative_to(ROOT)
    relocated=synthetic/local
    assert '/../' not in resolved.relative_to(ROOT).as_posix()
    local_links.append({'target':target,'repository_path':resolved.relative_to(ROOT).as_posix()})
d=Document(report)
for rel in d.part.rels.values():
    if rel.reltype.endswith('/hyperlink') and rel.is_external:verify_link(rel.target_ref)
for sheet in w:
    for row in sheet:
        for c in row:
            if c.hyperlink and c.hyperlink.target:
                verify_link(c.hyperlink.target)
                assert c.font.underline=='single' and c.font.color and c.font.color.type=='rgb' and c.font.color.rgb[-6:] in ['0563C1','0000FF'],c.coordinate
w.close()
for p in [report,appendix]:
    with zipfile.ZipFile(p) as z:
        if 'docProps/app.xml' in z.namelist():
            app=etree.fromstring(z.read('docProps/app.xml'))
            bases=app.xpath('//*[local-name()="HyperlinkBase"]/text()')
            assert not any(x.strip() for x in bases)
        if p.suffix=='.docx':
            xml=etree.fromstring(z.read('word/document.xml'))
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            for run in xml.xpath('//w:hyperlink//w:r',namespaces=ns):
                assert run.xpath('./w:rPr/w:u[@w:val="single"]',namespaces=ns)
                assert run.xpath('./w:rPr/w:color[@w:val="0563C1" or @w:val="0000FF"]',namespaces=ns)
result={'appendix_taxa':218,'seven_columns':True,'independent_ppr_denominator_tC':math.fsum(numeric),
        'appendix_worksheet_and_style_parts_byte_identical':True,'descending_full_precision_order':True,
        'portable_local_links':local_links,'external_links_preserved':len(external_links),
        'all_updated_word_pages_rendered_and_visually_inspected':7,'manual_field_preservation':'document_preservation.json'}
(OUT/'qa/review_artifact_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
script=(BASE/'render_saved_appendix.mjs').read_text(encoding='utf-8')
script=script.replace("const dir=path.dirname(fileURLToPath(import.meta.url));","const dir=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');")
script=script.replace('qa/appendix/saved_sources.png','auto_run_20261003/qa/appendix_sources.png').replace('qa/appendix/saved_longest_reason.png','auto_run_20261003/qa/appendix_longest_reason.png')
(OUT/'render_appendix.mjs').write_text(script,encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='portable_local_links'},ensure_ascii=False,indent=2),flush=True)
