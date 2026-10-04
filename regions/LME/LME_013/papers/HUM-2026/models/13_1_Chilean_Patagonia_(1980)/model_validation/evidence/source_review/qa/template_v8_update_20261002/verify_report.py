from pathlib import Path
from collections import Counter, defaultdict
from zipfile import ZipFile
from urllib.parse import urlsplit, unquote
from lxml import etree
import sys, json, math, hashlib, subprocess, re, shutil
import openpyxl
QA=Path(__file__).resolve().parent
ROOT=QA.parents[5]
REGION=ROOT/'regions/LME_013'
EVIDENCE=QA.parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,overview,records
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def near(a,b):return math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-8)
print('Reading authoritative regional workbook',flush=True)
book=read_book(REGION/'LME_013.xlsx')
o=overview(book)
assert o['selected_model_id']=='13_1_Chilean_Patagonia_(1980)' and o['taxon_detail_year']==2019 and o['catch_basis']=='landings'
audit=json.loads((EVIDENCE/'taxon_audit.json').read_text(encoding='utf-8'))
summary=json.loads((EVIDENCE/'coverage_summary.json').read_text(encoding='utf-8'))
bytax={r['taxon']:r for r in audit}
catch={r['taxon']:r for r in records(book,'Catch','Catch') if r['catch_basis']=='landings'}
classic={r['taxon']:r for r in records(book,'Classic PPR','Taxa')}
matches=defaultdict(list)
for r in records(book,'PPR','Matching'):
    assert r['model_id']==o['selected_model_id']
    matches[r['taxon']].append(r)
assert set(catch)==set(bytax)==set(matches) and len(catch)==218
for taxon,row in bytax.items():
    assert near(catch[taxon][2019],row['catch_tonnes'])
    coeff=classic.get(taxon,{}).get('sppr')
    computed=0 if catch[taxon][2019]==0 else catch[taxon][2019]*coeff/9
    assert near(computed,row['simple_chain_ppr_tC'])
    assert classic.get(taxon,{}).get('tl')==row['tl']
    current={r['group']:r['weight'] for r in matches[taxon]}
    adopted={r['group_name']:r['weight'] for r in row['groups']}
    assert current.keys()==adopted.keys(),taxon
    assert all(near(current[k],adopted[k]) for k in current),taxon
    assert near(sum(current.values()),1),taxon
    assert all(r['confidence'].lower()==row['overall_confidence'].lower() for r in matches[taxon]),taxon
print('All 218 adopted mappings and report-arithmetic rows agree',flush=True)
wb=openpyxl.load_workbook(REGION/'LME013_taxon_mapping_appendix.xlsx',data_only=False)
sheet=wb['Taxon mapping']; rows=list(sheet.values)[7:]
assert [c.value for c in sheet[7]]==['Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason']
assert sheet.freeze_panes and any(t.autoFilter is not None and t.autoFilter.ref=='A7:G225' for t in sheet.tables.values())
assert set(r[0] for r in rows)==set(bytax) and len(rows)==218
assert rows==sorted(rows,key=lambda r:(-r[3] if isinstance(r[3],(int,float)) else math.inf,r[0]))
for r in rows:
    a=bytax[r[0]]
    assert near(r[2],a['catch_tonnes']) and near(r[3],a['simple_chain_ppr_tC']) and r[5]==a['overall_confidence']
    assert r[4]==a['mapping_display']
for rec in summary['confidence_summary']:
    group=[r for r in rows if r[5]==rec['label']]
    assert len(group)==rec['taxa']
    assert near(sum(r[2] for r in group),rec['catch_tonnes']) and near(sum(r[3] for r in group),rec['ppr_tC'])
for key in ['membership','allocation']:
    computed=defaultdict(float)
    for a in audit:computed[(a[key+'_rule'],a[key+'_confidence'])]+=a['simple_chain_ppr_tC']
    for rec in summary[key+'_summary']:
        assert near(100*computed[(rec['rule'],rec['confidence'])]/summary['total_simple_chain_ppr_tC'],rec['ppr_percentage'])
    assert abs(sum(r['ppr_percentage'] for r in summary[key+'_summary'])-100)<1e-8
assert summary['membership_summary']==sorted(summary['membership_summary'],key=lambda r:-r['ppr_percentage'])
matrix=json.loads((EVIDENCE/'matrix_inspection.json').read_text(encoding='utf-8'))
assert matrix['canonical_sha256']==sha(REGION/o['model_path'])==o['results_model_sha256']
for m in matrix['methods']:
    assert sha((EVIDENCE/m['saved_full_direct_return']).resolve())==m['sha256']
    assert m['overall_status']=='WARN'
    assert all(math.isfinite(v) and v>=0 for r in m['source_matrix']['values'] for v in r)
print('Appendix types, order, totals, weights and retained diagnostic identities verified',flush=True)
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W,'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
report=REGION/'Model_validation_13_1_Chilean_Patagonia_(1980).docx'
with ZipFile(report) as z:doc=etree.fromstring(z.read('word/document.xml'))
with ZipFile(QA/'baseline.docx') as z:baseline=etree.fromstring(z.read('word/document.xml'))
def text(n):return ''.join(n.xpath('.//w:t/text()',namespaces=NS))
main=doc.find('w:body/w:tbl',NS)
fields=[text(r.find('w:tc',NS)) for r in main.findall('w:tr',NS)]
assert fields==['Field','Region','Catch source','Selected article','Other known articles','Selected model','Other models from the same article','Selection rationale','Model extraction','GE diagnostics','TE diagnostics','SPPR calculation','Geographic fit','Temporal fit','Other','Open issues and next action','Review and reproducibility']
for label in ['SPPR calculation','Open issues and next action','Review and reproducibility']:
    old=next(r for r in baseline.xpath('.//w:tr',namespaces=NS) if text(r.find('w:tc',NS))==label)
    new=next(r for r in main.findall('w:tr',NS) if text(r.find('w:tc',NS))==label)
    assert etree.tostring(old,method='c14n')==etree.tostring(new,method='c14n')
decision=next(t for t in doc.xpath('.//w:tbl',namespaces=NS) if text(t.find('w:tr',NS))=='Affected taxaWhy confidence is very low')
names=[]
for r in decision.findall('w:tr',NS)[1:]:names.extend(text(r.find('w:tc',NS)).split('; '))
assert len(names)==len(set(names))==121 and set(names)=={r[0] for r in rows if r[5]=='Very low'}
assert not re.search(r'\b[MW]\d+:',text(doc))

tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode('utf-8').split('\0'))
links=[]
for path in [report,REGION/'LME013_taxon_mapping_appendix.xlsx']:
    with ZipFile(path) as z:
        for part in z.namelist():
            if not part.endswith('.rels'):continue
            rel=etree.fromstring(z.read(part))
            for r in rel:
                if not r.get('Type','').endswith('/hyperlink'):continue
                target=r.get('Target')
                parsed=urlsplit(target)
                assert parsed.scheme not in ['file'] and not re.match(r'^[A-Za-z]:',target) and not target.startswith('\\\\')
                if parsed.scheme in ['http','https','mailto']:continue
                if target.startswith('#'):continue
                resolved=(path.parent/unquote(parsed.path).replace('\\','/')).resolve()
                assert resolved.exists(),(path.name,target)
                relpath=resolved.relative_to(ROOT).as_posix()
                assert relpath in tracked or (resolved.is_dir() and any(k.startswith(relpath+'/') for k in tracked)),(relpath,'not versioned')
                links.append({'file':path.name,'target':target,'destination':relpath})
        if path.suffix=='.docx':
            for link in doc.xpath('.//w:hyperlink',namespaces=NS):
                for run in link.findall('w:r',NS):
                    if not text(run):continue
                    color=run.find('w:rPr/w:color',NS);underline=run.find('w:rPr/w:u',NS)
                    assert color is not None and color.get('{'+W+'}val') in ['0563C1','0000FF']
                    assert underline is not None and underline.get('{'+W+'}val') not in ['none','0','false']
        for part in z.namelist():
            if part.startswith('docProps/') and part.endswith('.xml'):
                props=etree.fromstring(z.read(part))
                assert all(not (n.text or '').strip() for n in props.iter() if etree.QName(n).localname=='HyperlinkBase')
for s in wb:
    for row in s:
        for c in row:
            if c.hyperlink or (c.data_type=='f' and 'HYPERLINK(' in c.value.upper()):
                assert c.font.underline=='single'
                assert c.font.color and c.font.color.type=='rgb' and c.font.color.rgb[-6:] in ['0563C1','0000FF']
wb.close()
relocated=QA/'relocation_check'
for link in links:
    original=ROOT/link['destination'];dest=relocated/link['destination']
    if original.is_dir():dest.mkdir(parents=True,exist_ok=True)
    else:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,dest)
for path in [report,REGION/'LME013_taxon_mapping_appendix.xlsx']:
    dest=relocated/path.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
for link in links:
    dest=relocated/'regions/LME_013'/link['file']
    assert (dest.parent/unquote(urlsplit(link['target']).path)).resolve().exists()
record=json.loads((QA/'update_verification.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/k)==v for k,v in record['protected_inputs_sha256'].items())
checks={'authoritative_taxa':218,'very_low_taxa_once':121,'all_adopted_mappings_equal':True,'classic_arithmetic_equal':True,'all_confidence_and_rule_totals_equal':True,'manual_row_xml_equal':True,'appendix_numeric_sort_filters_and_freeze_verified':True,'saved_diagnostic_identity_verified':True,'relative_tracked_links':len(links),'physical_relocation_verified':True,'hyperlink_blue_underlined':True,'protected_scientific_inputs_unchanged':True,'report_sha256':sha(report),'renderer':'independent hidden Microsoft Word read-only export after bundled LibreOffice unavailable','map_adoption':'deferred by user'}
(QA/'acceptance_verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks),flush=True)
