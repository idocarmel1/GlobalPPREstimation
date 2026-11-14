import hashlib,json,math,os,sys,zipfile
from pathlib import Path
from urllib.parse import unquote,urlsplit
from collections import Counter
from lxml import etree as E
import openpyxl

RUN=Path(__file__).resolve().parents[1];VAL=RUN.parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists());sys.path.insert(0,str(ROOT))
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.validation.researcher_review import read_report
from tools.project_core.workbooks.workbooks import read_book,records
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS={'w':W};text=lambda x:''.join(x.itertext())
q=lambda s:f'{{{W}}}{s}'
report=VAL/'validation.docx'
verify_report(report)
with zipfile.ZipFile(report) as z:
    parts={n:z.read(n) for n in z.namelist()}
doc=E.fromstring(parts['word/document.xml']);rels=E.fromstring(parts['word/_rels/document.xml.rels'])
targets={r.get('Id'):r.get('Target') for r in rels}
tables=doc.findall('w:body/w:tbl',NS)
manual=json.loads((RUN/'qa/manual_before.json').read_text(encoding='utf-8'))
fields={text(cells[0]):(row,cells[1]) for row in tables[0].findall('w:tr',NS) if len(cells:=row.findall('w:tc',NS))==2}
manual_equal={key:E.tostring(fields[key][0]).decode()==value for key,value in manual.items()}
assert all(manual_equal.values())
assert 'PAT2024_FalklandShelf_2020_native;' in text(fields['Selected model'][1])
assert not any(v in text(doc) for v in ['MODEL VALIDATED','MODEL DISQUALIFIED'])
links=[]
for h in doc.findall('.//w:hyperlink',NS):
    target=targets.get(h.get(f'{{{R}}}id'),'')
    label=text(h)
    if target and not urlsplit(target).scheme:
        local=(VAL/unquote(target.split('#')[0])).resolve()
        assert local.exists() and local.is_relative_to(ROOT),(label,target)
        assert not Path(target).is_absolute()
        links.append({'label':label,'target':target})
    for r in h.findall('.//w:r',NS):
        assert r.find('w:rPr/w:color',NS).get(q('val'))=='0563C1'
        assert r.find('w:rPr/w:u',NS).get(q('val'))=='single'
assert next(l['target'] for l in links if l['label']=='Canonical source')=='../model.json'
assert next(l['target'] for l in links if l['label']=='Model folder')=='..'
assert next(l['target'] for l in links if l['label']=='Model inventory')=='../../../source_manifest.json'
before=json.loads((RUN/'qa/package_before.json').read_text(encoding='utf-8'))
changed_parts=[name for name,h in before.items() if hashlib.sha256(parts[name]).hexdigest()!=h]
assert set(changed_parts)=={'word/document.xml','word/_rels/document.xml.rels'},changed_parts
protected=json.loads((RUN/'qa/protected_before.json').read_text(encoding='utf-8'))
protected_equal={path:sha(ROOT/path)==h for path,h in protected.items()}
assert all(protected_equal.values()),protected_equal

mapping=json.loads((RUN/'qa/mapping_validation_summary.json').read_text(encoding='utf-8'))
audit=json.loads((VAL/'evidence/source_review/taxon_audit.json').read_text(encoding='utf-8'))
verylow=next(t for t in tables if text(t.find('w:tr/w:tc',NS))=='Affected taxa')
listed=[]
for row in verylow.findall('w:tr',NS)[1:]:listed.extend(text(row.find('w:tc',NS)).split('; '))
expected=[r['taxon'] for r in audit if r['overall_confidence']=='Very low']
assert Counter(listed)==Counter(expected) and len(listed)==196
b=openpyxl.load_workbook(VAL/'taxon_mapping.xlsx')
old=openpyxl.load_workbook(RUN/'inputs/taxon_mapping_before.xlsx')
assert list(b['Taxon mapping'].iter_rows(min_row=8,max_row=257,values_only=True))==list(old['Taxon mapping'].iter_rows(min_row=8,max_row=257,values_only=True))
rows=list(b['Taxon mapping'].iter_rows(min_row=8,max_row=257,values_only=True))
assert len(rows)==250 and len({r[0] for r in rows})==250
assert rows==sorted(rows,key=lambda r:(-(r[3] if isinstance(r[3],(int,float)) else -math.inf),r[0]))
assert math.isclose(sum(r[2] for r in rows),1497627.61997537,abs_tol=1e-8)
assert math.isclose(sum(r[3] for r in rows),142458248.78282157,abs_tol=1e-6)
assert b['Taxon mapping'].freeze_panes=='B8'
assert b['Sources'].freeze_panes=='A5'
assert any(t.ref=='A7:G257' and t.autoFilter.ref=='A7:G257' for t in b['Taxon mapping'].tables.values())
assert any(t.ref=='A4:D28' and t.autoFilter.ref=='A4:D28' for t in b['Sources'].tables.values())
for s in b:
    for row in s:
        for c in row:
            if c.hyperlink and c.hyperlink.target:
                target=c.hyperlink.target
                if not urlsplit(target).scheme:
                    assert (VAL/unquote(target.split('#')[0])).exists(),(s.title,c.coordinate,target)
                assert c.font.underline=='single'
                assert c.font.color.type=='rgb' and c.font.color.rgb[-6:] in ['0563C1','0000FF']
try:read_report(ROOT,report,'PAT2024_FalklandShelf_2020_native')
except ValueError as e:
    assert str(e)=='The report needs an explicit researcher identity, date and one unambiguous decision',str(e)
    parser_status=str(e)
else:raise AssertionError('Report must remain unsigned')

diag=json.loads((VAL/'evidence/ee_floor_on_review/review_summary.json').read_text(encoding='utf-8'))
assert diag['floor']['use_ee_floor'] and diag['floor']['ee_floor']==0.1
for result in diag['methods']:
    assert result['diagnostic']['status']=='WARN'
    assert result['diagnostic']['balance']['is_balanced'] is True
    assert result['source_matrix_review']['shape']==[37,5]
    assert result['source_matrix_review']['negative_count']==0
    assert result['source_matrix_review']['nonfinite_count']==0

out={'checked_date':'2026-11-14','region_id':'LME_014','model_id':'PAT2024_FalklandShelf_2020_native',
     'report_sha256':sha(report),'appendix_sha256':sha(VAL/'taxon_mapping.xlsx'),
     'manual_rows_exact_xml':manual_equal,'package_changed_parts':changed_parts,
     'protected_paths_unchanged':protected_equal,'used_local_links_verified':links,
     'unsigned_parser_status':parser_status,'appendix_scientific_rows_preserved':True,
     'taxa':250,'very_low_taxa_listed_once':196,'all_percentages_current_format':True,
     'reference':{'year':2019,'catch_basis':'landings','catch_t':1497627.61997537,'simple_chain_ppr_tC':142458248.78282157},
     'configuration':{'use_ee_floor':True,'ee_floor':0.1},'scope':'Report and appendix only; new GE/TE diagnostic evidence retained for review; no adoption or publication.',
     'geography':{'A_approx_percent':17,'B_approx_percent':100,'basis':'Conditional reported-area/subarea estimate, not polygon intersection','current_boundary_source':'common_reference_data/geography/boundaries/LMEs.geojson'},
     'template_sha256':sha(ROOT/'tools/templates/validation.docx')}
(RUN/'qa/report_verification.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'passed':True,'manual_rows_preserved':len(manual_equal),'taxa':250,'very_low_taxa':196,'local_links':len(links),'protected_files':len(protected_equal),'changed_package_parts':changed_parts}))
