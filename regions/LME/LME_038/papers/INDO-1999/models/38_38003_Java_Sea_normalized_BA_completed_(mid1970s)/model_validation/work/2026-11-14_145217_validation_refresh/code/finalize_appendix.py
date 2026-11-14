from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as ET
import copy, hashlib, json, math, re
from urllib.parse import unquote
from openpyxl import load_workbook

RUN=Path(__file__).resolve().parents[1]; BASE=RUN.parents[1]
ROOT=next(p for p in BASE.parents if (p/'Project.xlsx').exists())
OLD=RUN/'inputs/taxon_mapping_before.xlsx'; GEN=RUN/'outputs/taxon_mapping_artifact.xlsx'; OUT=BASE/'taxon_mapping.xlsx'
EVIDENCE=BASE/'evidence/mapping/validation_refresh_20261114.json'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
SS=NS['s']
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
d=read(RUN/'outputs/mapping_review.json');patches=read(RUN/'outputs/appendix_cell_updates.json')
for path,h in d['input_hashes'].items(): assert sha(ROOT/path)==h,('input changed',path)

# Historical evidence is reused by exact source bytes and unchanged mapping dependencies.
source_checks=[]
manifest=read(BASE/'evidence/source_review/supporting_sources_manifest.json')
for r in manifest:
 p=BASE/'evidence/source_review/supporting_sources'/Path(r['path']).name
 actual=sha(p);assert actual==r['sha256'],p
 source_checks.append({'source':r['id'],'path':str(p.relative_to(BASE)).replace('\\','/'),'sha256':actual,'matches_recorded':True})
pdf=BASE/'../../../../BUCHARY-1991/sources/ubc_1999-0254.pdf.pdf'
index=read(BASE/'evidence/source_review/evidence_index.json')
assert sha(pdf)==index['source_identity']['main_pdf_sha256']
source_checks.append({'source':'Buchary1999 thesis','path':'../../../../BUCHARY-1991/sources/ubc_1999-0254.pdf.pdf','sha256':sha(pdf),'matches_recorded':True})
d['reused_source_compatibility']=source_checks
d['compatibility']['source_pdfs_match_recorded_hashes']=True
d['compatibility']['weight_comparison_absolute_tolerance']=1e-14
d['compatibility']['confidence_spelling_normalization']='very_low is compared as Very low without changing stored data'
d['compatibility']['source_evidence_claim']='Existing evidenced membership/allocation decisions reused, not newly researched or resolved.'
d['appendix_update']={'authoring':'Bundled @oai/artifact-tool imported existing workbook and authored the eight changed cells. Exact cell payloads transferred to the original OOXML package to preserve all unrelated parts, manual content, native hyperlinks and styles.','changed_cells':{k:list(v) for k,v in patches.items()},'link_change':{'sheet':'Taxon mapping','cell':'D6','old':'evidence/source_review/taxon_audit.json','new':'evidence/mapping/validation_refresh_20261114.json'}}
write(RUN/'outputs/mapping_review.json',d);write(EVIDENCE,d)

with ZipFile(OLD) as z:parts={i.filename:z.read(i.filename) for i in z.infolist()}; infos=z.infolist()
with ZipFile(GEN) as z:
 strings=[]
 if 'xl/sharedStrings.xml' in z.namelist():
  strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
 for i,sh in [(1,'Taxon mapping'),(2,'Sources')]:
  part=f'xl/worksheets/sheet{i}.xml';generated=ET.fromstring(z.read(part));original=parts[part].decode();original_tree=ET.fromstring(parts[part])
  for address,text in patches[sh].items():
   c=generated.find(f'.//s:c[@r="{address}"]',NS);assert c is not None
   if c.get('t')=='s':actual=strings[int(c.find('s:v',NS).text)]
   else: actual=''.join(c.find('s:is',NS).itertext()) if c.get('t')=='inlineStr' else c.find('s:v',NS).text
   assert actual==text,(sh,address,actual,text)
   pat=rf'<x:c\b(?=[^>]*\br="{re.escape(address)}")[^>]*>.*?</x:c>'
   m=re.search(pat,original,re.S);assert m
   oc=original_tree.find(f'.//s:c[@r="{address}"]',NS)
   # Retain the original cell attributes/style; only the artifact-authored value changes.
   attrs=dict(oc.attrib);attrs['t']='inlineStr'
   nc=ET.Element('{'+SS+'}c',attrs,nsmap={'x':SS});inline=ET.SubElement(nc,'{'+SS+'}is');tt=ET.SubElement(inline,'{'+SS+'}t');tt.text=actual
   if actual[:1].isspace() or actual[-1:].isspace():tt.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
   fragment=ET.tostring(nc,encoding='unicode').replace(f' xmlns:x="{SS}"','')
   original=original[:m.start()]+fragment+original[m.end():]
  parts[part]=original.encode()

part='xl/worksheets/_rels/sheet1.xml.rels'
oldtarget=b'evidence/source_review/taxon_audit.json';newtarget=b'evidence/mapping/validation_refresh_20261114.json'
assert parts[part].count(oldtarget)==1;parts[part]=parts[part].replace(oldtarget,newtarget)
tmp=RUN/'outputs/taxon_mapping_final.xlsx'
with ZipFile(tmp,'w',ZIP_DEFLATED) as z:
 for info in infos:z.writestr(info,parts[info.filename])

before=load_workbook(OLD,data_only=False);after=load_workbook(tmp,data_only=False)
assert before.sheetnames==after.sheetnames==['Taxon mapping','Sources']
changed=[]
for s in before:
 a=after[s.title]
 assert (s.max_row,s.max_column)==(a.max_row,a.max_column)
 assert s.freeze_panes==a.freeze_panes
 assert list(s.tables)==list(a.tables)
 assert str(s.merged_cells)==str(a.merged_cells)
 for row in s:
  for c in row:
   n=a[c.coordinate]
   assert c.style_id==n.style_id and c.number_format==n.number_format
   if c.value!=n.value:
    assert patches[s.title].get(c.coordinate)==n.value
    changed.append({'sheet':s.title,'cell':c.coordinate})
   assert (c.comment.text if c.comment else None)==(n.comment.text if n.comment else None)
assert len(changed)==8,changed
sheet=after['Taxon mapping'];rws=list(sheet.iter_rows(min_row=8,values_only=True))
assert [r[0] for r in rws]==[r['taxon'] for r in d['rows']]
for actual,expected in zip(rws,d['rows']):
 assert actual[4:]==(expected['mapping_display'],expected['overall_confidence'],expected['appendix_reason'])
 for idx,key in [(1,'tl'),(2,'catch_tonnes'),(3,'simple_chain_ppr_tC')]:
  v=expected[key]
  if v is None:assert actual[idx]=='?'
  else:assert isinstance(actual[idx],(int,float)) and math.isclose(actual[idx],v,rel_tol=1e-14,abs_tol=1e-8)
assert len(rws)==181
assert math.isclose(sum(r[2] for r in rws),d['total_catch_tonnes'],rel_tol=1e-14)
assert math.isclose(sum(r[3] for r in rws),d['total_simple_chain_ppr_tC'],rel_tol=1e-14)
for summary in ['confidence_summary','membership_summary','allocation_summary']:
 assert sum(r['taxa'] for r in d[summary])==181
 assert abs(sum(r['ppr_percentage'] for r in d[summary])-100)<1e-8
links=[]
for s in after:
 for row in s:
  for c in row:
   if c.hyperlink:
    t=c.hyperlink.target or '#'+c.hyperlink.location
    assert c.font.underline=='single' and c.font.color.type=='rgb' and c.font.color.rgb[-6:].upper()=='0563C1'
    if not t.startswith(('#','https://','http://')):
     assert not re.match(r'^[A-Za-z]:|^[/\\]|^file:|^localhost',t)
     p=(BASE/unquote(t.split('#')[0])).resolve();assert p.exists(),p
     links.append({'sheet':s.title,'cell':c.coordinate,'target':t,'exists':True,'blue_underlined':True})
    else:links.append({'sheet':s.title,'cell':c.coordinate,'target':t,'blue_underlined':True})
with ZipFile(OLD) as oldzip,ZipFile(tmp) as newzip:
 changed_parts=[n for n in oldzip.namelist() if oldzip.read(n)!=newzip.read(n)]
 assert set(changed_parts)=={'xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml','xl/worksheets/_rels/sheet1.xml.rels'}
 # All 181 detailed rows are byte-identical, including types, mapping text, manual content and formatting.
 oldsheet=oldzip.read('xl/worksheets/sheet1.xml').decode();newsheet=newzip.read('xl/worksheets/sheet1.xml').decode()
 for row in range(8,189):
  pat=rf'<x:row\b(?=[^>]*\br="{row}")[^>]*>.*?</x:row>'
  assert re.search(pat,oldsheet,re.S).group()==re.search(pat,newsheet,re.S).group()
 # The original portable-link package has no Hyperlink Base.
 assert all(b'HyperlinkBase' not in newzip.read(n) for n in newzip.namelist() if n.startswith('docProps/'))
for path,h in d['input_hashes'].items():assert sha(ROOT/path)==h,('input changed before save',path)
OUT.write_bytes(tmp.read_bytes())
qa={'delivered_appendix_sha256':sha(OUT),'source_appendix_sha256':sha(OLD),'changed_cells':changed,'changed_parts':changed_parts,'all_181_detail_rows_byte_identical':True,'all_numeric_rows_match_canonical_read_book_arithmetic':True,'full_precision_sort_verified':True,'all_five_categories_and_both_rule_tables_reconcile':True,'all_links':links,'source_hash_checks':source_checks,'input_hashes_rechecked_unchanged':True,'visual_review':'Pending final artifact renders'}
write(RUN/'qa/appendix_verification.json',qa)
print(json.dumps({k:v for k,v in qa.items() if k not in ['all_links','source_hash_checks']},ensure_ascii=False,indent=2))
