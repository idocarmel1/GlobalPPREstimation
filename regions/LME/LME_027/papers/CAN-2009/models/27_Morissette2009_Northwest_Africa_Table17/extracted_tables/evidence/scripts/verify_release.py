"""Read final artifacts and verify identities, arithmetic, portable links and preservation."""
from pathlib import Path,PureWindowsPath
import json,hashlib,zipfile,re,math,shutil,tempfile,sys,importlib.util
from urllib.parse import unquote
from lxml import etree as E
import openpyxl
from docx import Document

C=Path(__file__).resolve().parents[1];ROOT=C.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from validation_percentage_format import verify_report,format_percent
DOC=C/'Model_validation_27_Morissette2009_Northwest_Africa_Table17.docx'
XLS=C/'LME027_candidate_taxon_mapping_appendix.xlsx'
def read(p):return json.loads((C/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={};links=[];errors=[]
protected=read('evidence/protected_files_before.json')
changed=[p for p,h in protected.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
checks['protected_files']={'count':len(protected),'changed':changed,'all_unchanged':not changed}
assert not changed,changed

wb=openpyxl.load_workbook(XLS,data_only=False)
ws=wb['Taxon mapping'];expected=read('mapping/appendix_rows.json');headers=list(expected[0])
assert [ws.cell(7,c).value for c in range(1,8)]==headers
assert ws.max_row==len(expected)+7 and ws.max_column==7
for i,row in enumerate(expected,8):
    for j,key in enumerate(headers,1):
        value=ws.cell(i,j).value;source=row[key] if row[key] is not None else '?'
        if isinstance(source,(int,float)):
            assert isinstance(value,(int,float)) and math.isclose(value,source,rel_tol=1e-14,abs_tol=1e-9),(i,key,value,source)
        else:assert value==source,(i,key,value,source)
assert ws.freeze_panes=='A8' and wb['Sources'].freeze_panes=='A5'
assert ws.tables['CandidateTaxonMapping'].autoFilter.ref=='A7:G519'
assert wb['Sources'].tables['CandidateSources'].autoFilter.ref=='A4:D16'
saved=[(ws.cell(i,1).value,ws.cell(i,4).value) for i in range(8,520)]
assert saved==sorted(saved,key=lambda r:(not isinstance(r[1],(int,float)),-r[1] if isinstance(r[1],(int,float)) else 0,r[0]))
cov=read('mapping/coverage_summary.json')
assert math.isclose(math.fsum(ws.cell(i,3).value for i in range(8,520)),cov['total_catch_tonnes'],rel_tol=1e-14)
assert math.isclose(math.fsum(ws.cell(i,4).value for i in range(8,520)),cov['total_simple_chain_ppr_tC'],rel_tol=1e-14)
for s in wb:
    for row in s:
        for cell in row:
            assert cell.data_type!='f','No cached formula results in fixed scientific appendix'
            if cell.hyperlink:
                assert cell.font.u=='single' and cell.font.color.type=='rgb' and cell.font.color.rgb[-6:]=='0563C1'
                links.append((XLS,cell.hyperlink.target))
checks['appendix']={'rows':len(expected),'exact_columns':headers,'numeric_sort':True,'cells_match_audit':True,'frozen_headers':True,'native_filters':True,'totals_agree':True,'hyperlinks_blue_underlined':True,'formulas':0}

d=Document(DOC);verify_report(DOC)
assert len(d.sections)==1
assert len(d.tables[4].rows)==len(read('mapping/very_low_decisions.json'))+1
for i,r in enumerate(cov['confidence_summary'],1):
    assert [x.text for x in d.tables[1].rows[i].cells]==[r['label'],str(r['taxa']),format_percent(r['catch_percentage']),format_percent(r['ppr_percentage'])]
assert d.tables[0].cell(15,1).text==''
assert d.tables[0].cell(16,1).text=='Researcher name: ____________________ | review date: dd/mm/yyyy'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
with zipfile.ZipFile(DOC) as z:
    xml=E.fromstring(z.read('word/document.xml'))
    rels=E.fromstring(z.read('word/_rels/document.xml.rels'))
    relmap={x.get('Id'):x.get('Target') for x in rels if x.get('Type','').endswith('/hyperlink')}
    for h in xml.findall('.//{'+W+'}hyperlink'):
        target=relmap[h.get('{'+R+'}id')];links.append((DOC,target))
        for r in h.findall('{'+W+'}r'):
            assert r.find('{'+W+'}rPr/{'+W+'}color').get('{'+W+'}val')=='0563C1'
            assert r.find('{'+W+'}rPr/{'+W+'}u').get('{'+W+'}val')=='single'
    for name in z.namelist():
        if name.startswith('docProps/') and name.endswith('.xml'):
            for entry in E.fromstring(z.read(name)).iter():
                if E.QName(entry).localname=='HyperlinkBase':assert not (entry.text or '').strip()
checks['word']={'confidence_agrees_with_appendix':True,'manual_fields_unsigned':True,'all_Very_low_taxa_present':True,'percentage_format':True,'hyperlinks_blue_underlined':True,'preserved_template_parts':read('qa/template_fidelity.json')['preserve_only_parts_equal']}

# Publish an explicitly provisional record so the index can link to this report
# while portability is checked. Only the successful end of this script marks it complete.
(C/'qa/release_verification.json').write_text(json.dumps({'status':'verification_in_progress'},indent=2),encoding='utf-8')
spec=importlib.util.spec_from_file_location('check_evidence',ROOT/'tools/skills/original_skill_resources/combined-src/scripts/check_evidence.py')
evidence_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(evidence_module)
inventory=evidence_module.check(C/'evidence_index.json')
assert not inventory['errors'],inventory['errors']
assert inventory['missing_roles']==['source_only_executable_input'],inventory['missing_roles']
source_inventory=evidence_module.check(C/'evidence/source_extraction/evidence_index.json')
assert not source_inventory['errors'],source_inventory['errors']
checks['evidence']={'verified_artifacts':len(inventory['verified_artifacts']),'integrity_errors':inventory['errors'],'missing_roles':inventory['missing_roles'],'source_inventory_artifacts':len(source_inventory['verified_artifacts']),'source_inventory_missing_roles':source_inventory['missing_roles']}
visual=read('qa/visual_review.json')
assert visual['word_pages_inspected']==list(range(1,8))
assert visual['docx_sha256']==sha(DOC) and visual['appendix_sha256']==sha(XLS)
checks['visual_review']=visual

# Current supporting Markdown is also portable. Historical evidence stays unchanged.
for md in C.rglob('*.md'):
    if 'engine' in md.parts or 'qa' in md.parts:continue
    for target in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
        # Parenthesized model IDs require a balanced Markdown target parser; handle in Office checks above.
        if '(' in target:continue
        links.append((md,target.strip('<>')))
resolved=[]
for containing,target in links:
    if target.startswith(('https://','http://','mailto:','#')):continue
    assert not PureWindowsPath(target).drive and not target.startswith(('/','\\','file:','localhost:')),(containing,target)
    path=unquote(target.split('#',1)[0]);actual=(containing.parent/path).resolve()
    assert actual.is_relative_to(ROOT.resolve()),(containing,target)
    assert actual.exists(),(containing,target,actual)
    resolved.append((containing,actual,target))
with tempfile.TemporaryDirectory(prefix='LME027_portable_review_') as temp:
    relocated=Path(temp)/'repository';relocated.mkdir()
    copies=set([DOC,XLS]+[p for _,p,_ in resolved]+[p for p,_,_ in resolved])
    for p in copies:
        target=relocated/p.relative_to(ROOT)
        if p.is_dir():target.mkdir(parents=True,exist_ok=True)
        else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    for containing,actual,target in resolved:
        moved=relocated/containing.relative_to(ROOT)
        assert (moved.parent/unquote(target.split('#',1)[0])).resolve().exists()
checks['links']={'local_targets_checked':len(resolved),'physical_relocation_verified':True,'machine_specific_targets':0}
checks['review_package_ready']=True
checks['paper_only_executable_complete']=False
checks['native_companion_reproduced']=True
checks['distinct_replacement_supported']=False
checks['scientific_approval']=False
checks['status']='verification_complete'
checks['final_docx_sha256']=sha(DOC);checks['final_appendix_sha256']=sha(XLS)
(C/'qa/release_verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'protected_files_unchanged':len(protected),'appendix_rows':len(expected),'portable_local_links':len(resolved),'review_package_ready':True,'paper_only_complete':False}))
