from pathlib import Path
from urllib.parse import urlsplit,unquote
import hashlib,json,zipfile,sys,math,os
from lxml import etree as E
import openpyxl
run=Path(__file__).resolve().parents[1];v=run.parents[1];m=v.parent;root=Path(__file__).resolve().parents[11]
sys.path.insert(0,str(root));sys.stdout.reconfigure(encoding='utf-8')
from tools.project_core.validation.validation_percentage_format import verify_report,format_percent
from tools.project_core.validation.researcher_review import read_report
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
summary=json.loads((v/'evidence/mapping/coverage_2019_landings_20261114.json').read_text(encoding='utf-8'))
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';n={'w':W};txt=lambda e:''.join(e.xpath('.//w:t/text()',namespaces=n))
def docdata(p):
    with zipfile.ZipFile(p) as z:return {i.filename:z.read(i.filename) for i in z.infolist()}
before=docdata(run/'inputs/validation_before.docx');after=docdata(v/'validation.docx')
d=E.fromstring(after['word/document.xml']);old=E.fromstring(before['word/document.xml'])
def fields(e):return {txt(r.find('w:tc',n)):r for t in e.findall('w:body/w:tbl',n) for r in t.findall('w:tr',n) if len(r.findall('w:tc',n))==2}
of=fields(old);nf=fields(d)
manual=['SPPR calculation','Open issues and next action','Review and reproducibility','Selection rationale']
assert all(E.tostring(of[k])==E.tostring(nf[k]) for k in manual)
assert [k for k in before if before[k]!=after[k]]==['word/document.xml','word/_rels/document.xml.rels']
verify_report(v/'validation.docx')
diag=m/'results/diagnostics/ee_floor_review_20261114'
diagnostics=json.loads((diag/'outputs/report_summary.json').read_text())
integrity=json.loads((diag/'inventory/completeness.json').read_text())
assert diagnostics['configuration']==dict(use_ee_floor=True,ee_floor=0.1,ee_threshold=0.1)
assert integrity['complete'] and not integrity['errors'] and len(integrity['verified_artifacts'])==45
assert 'EE floor ON at 0.1' in txt(nf['Other'])
for method in ['GE','TE']:
    cell=txt(nf[method+' diagnostics']); rec=diagnostics['methods'][method]
    assert 'WARN' in cell and 'PENDING' not in cell and 'No negative SPPR entries' in cell and '94 × 3' in cell
    assert str(len(rec['divergence']['near_singular_te']))+' groups' in cell
    assert format(rec['rho_living'],'.6g') in cell and format(rec['detritus_sppr'][0]['sppr'],'.6g') in cell
    assert rec['overall_status']=='WARN' and rec['matrix_shape']==[94,3] and not rec['negative_source_group_pairs'] and rec['nonfinite_entries']==0
try:read_report(root,v/'validation.docx',m.name)
except ValueError as e:assert str(e)=='The report needs an explicit researcher identity, date and one unambiguous decision'
else:raise AssertionError('Unexpected signed review')
links=[]
for rel in E.fromstring(after['word/_rels/document.xml.rels']):
    if not rel.get('Type','').endswith('/hyperlink'):continue
    target=rel.get('Target');u=urlsplit(target)
    if u.scheme: assert u.scheme in ('http','https','mailto');continue
    path=(v/unquote(u.path)).resolve();assert path.exists() and path.is_relative_to(root),target
    links.append(target)
for h in d.findall('.//w:hyperlink',n):
    for r in h.findall('.//w:r',n):
        assert r.find('w:rPr/w:color',n).get('{'+W+'}val')=='0563C1'
        assert r.find('w:rPr/w:u',n).get('{'+W+'}val')=='single'
wb=openpyxl.load_workbook(v/'taxon_mapping.xlsx',data_only=False)
ws=wb['Taxon mapping'];rows=list(ws.iter_rows(min_row=8,max_row=356,values_only=True))
assert len(rows)==len(set(r[0] for r in rows))==349
assert math.isclose(sum(r[2] for r in rows),summary['total_catch_tonnes'],rel_tol=1e-12)
assert math.isclose(sum(r[3] for r in rows),summary['simple_chain_ppr_tC'],rel_tol=1e-12)
assert rows==sorted(rows,key=lambda r:(-r[3],r[0]))
for category,data in summary['categories'].items():assert sum(r[5]==category for r in rows)==data['taxa_count']
vl_names=[taxon for rec in summary['very_low_decisions'] for taxon in rec['taxa']]
assert set(vl_names)=={r[0] for r in rows if r[5]=='Very low'} and len(vl_names)==190
vl_table=next(t for t in d.findall('w:body/w:tbl',n) if txt(t.find('w:tr',n)).startswith('Affected taxa'))
doc_names=[]
for row in vl_table.findall('w:tr',n)[1:]:doc_names.extend(txt(row.find('w:tc',n)).split('; '))
assert set(doc_names)==set(vl_names) and len(doc_names)==190
conf=next(t for t in d.findall('w:body/w:tbl',n) if txt(t.find('w:tr',n)).startswith('Overall confidence'))
assert len(conf.findall('w:tr',n))==6
for row,(category,data) in zip(conf.findall('w:tr',n)[1:],summary['categories'].items()):
    assert [txt(c) for c in row.findall('w:tc',n)]==[category,str(data['taxa_count']),format_percent(data['catch_percent']),format_percent(data['ppr_percent'])]
for k in ['membership_rules','allocation_rules']:assert math.isclose(sum(r['ppr_percent'] for r in summary[k]),100,abs_tol=1e-8)
for sheet in wb:
    assert sheet.freeze_panes
    for table in sheet.tables.values():assert table.autoFilter is not None
    for row in sheet:
        for cell in row:
            if cell.hyperlink:
                assert cell.font.u=='single' and cell.font.color.rgb in ('FF0563C1','000563C1')
                target=cell.hyperlink.target
                if target and not urlsplit(target).scheme:assert (v/unquote(urlsplit(target).path)).resolve().exists()
            if cell.data_type=='f':
                import re
                target=re.match(r'=HYPERLINK\("([^"]+)"',cell.value,re.I)
                if target and not urlsplit(target[1]).scheme:assert (v/unquote(urlsplit(target[1]).path)).resolve().exists()
before_hashes=json.loads((run/'qa/protected_before.json').read_text())
assert all(sha(root/p)==h for p,h in before_hashes.items())
evidence_files=['source_review/configuration_review_20261114.json','mapping/review_rows_20261114.json','mapping/coverage_2019_landings_20261114.json','mapping/mapping_verification_20261114.json','mapping/ee_floor_appendix_link_verification_20261114.json']
indexpath=v/'evidence/evidence_index.json';index=json.loads(indexpath.read_text()) if indexpath.exists() else {'schema_version':1,'unit_id':'LME_003','model_id':m.name}
index['report_review_20261114']={'scope':'Report and appendix refresh and explicitly authorized review-only GE/TE with EE floor ON0.1; no adoption','artifacts':[{'path':'../'+name,'sha256':sha(v/name)} for name in ['validation.docx','taxon_mapping.xlsx']],'supporting_evidence':[{'path':name,'sha256':sha(v/'evidence'/name)} for name in evidence_files],'diagnostic_evidence_index':{'path':'../../results/diagnostics/ee_floor_review_20261114/inventory/evidence_index.json','sha256':sha(diag/'inventory/evidence_index.json')},'historical_evidence_role':'Retained audits/results reused only within matching scopes; old GE/TE diagnostics and retained regional GE/TE coefficients are not ON0.1. Appendix PPR shares use the unchanged independent simple-chain method.','researcher_decision':'None supplied or registered'}
indexpath.write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
render=json.loads((run/'qa/render_verification.json').read_text())
assert render['docx_sha256']==sha(v/'validation.docx') and render['all_pages_visually_inspected']
preservationpath=run/'qa/document_preservation.json';preservation=json.loads(preservationpath.read_text())
preservation['final_sha256']=sha(v/'validation.docx')
preservation.pop('diagnostic_gap',None)
preservation['diagnostic_review']='Explicitly authorized GE and TE run complete with EE floor ON0.1; both WARN; no adoption or decision registration'
preservationpath.write_text(json.dumps(preservation,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(run/'qa/link_verification.json').write_text(json.dumps([{'target':target,'exists':True,'inside_repo':True,'resolved':str((v/unquote(urlsplit(target).path)).resolve())} for target in links],indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
qa={'docx_sha256':sha(v/'validation.docx'),'appendix_sha256':sha(v/'taxon_mapping.xlsx'),'all_final_pages_visually_inspected':True,'page_count':render['page_count'],'render':'Separate hidden Word read-only PDF export, rasterized with bundled pypdfium2','manual_cells_and_selection_preserved':True,'all_349_taxa_and_all_190_very_low_names_reconciled':True,'totals_rules_and_confidence_reconciled':True,'local_docx_links_checked':len(links),'appendix_filters_freeze_links_checked':True,'protected_regional_model_results_templates_unchanged':True,'signed_review':'Absent; parser rejects unsigned document as expected','diagnostics':'GE WARN / TE WARN, EE floor ON0.1; full finite nonnegative94x3 matrices;45 indexed artifacts verified; independent scientific evidence review passed','registration_project_map_trends':'Not changed by this task','source_bundles':'Existing paper/diet/geography/mapping evidence reused with identity checks; no fresh extraction'}
(run/'qa/final_verification.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(qa,indent=2,ensure_ascii=False))
