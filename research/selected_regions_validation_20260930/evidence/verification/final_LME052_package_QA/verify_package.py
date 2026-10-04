from pathlib import Path
import json,hashlib,zipfile,shutil,re
from urllib.parse import unquote,urlsplit
from lxml import etree as ET
import openpyxl
R=Path.cwd(); B=R/'original_research_archive/research/selected_regions_validation_20260930'; Q=B/'work/final_LME052_package_QA'; Q.mkdir(parents=True,exist_ok=True)
E=R/'regions/LME_052/validation_reports/52_1_Sea_of_Okhotsk_NE_(1980)'
H=E/'coordination_handoff.json'; h=json.loads(H.read_text(encoding='utf-8-sig')); v=json.loads((E/'visual_qa_manifest.json').read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p):return {'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def resolve(s,base):
 p=Path(s)
 if p.is_absolute():return p
 return R/p if s.startswith(('regions/','tools/','original_research_archive/','src/','scripts/')) or (R/p).exists() else base/p
checks=[]
def check(s,expected,base,context):
 if not isinstance(s,str) or s.startswith(('http:','https:')):return
 p=resolve(s,base); actual=sha(p) if p.is_file() else None
 checks.append({'context':context,'path':s,'expected':expected,'actual':actual,'pass':actual==expected})
def walk(x,base,ctx):
 if isinstance(x,dict):
  if 'sha256' in x and ('path'in x or 'file'in x):check(x.get('path',x.get('file')),x['sha256'],base,ctx)
  for k,y in x.items():
   if isinstance(y,str) and re.fullmatch('[0-9a-f]{64}',y) and ('/'in k or '\\'in k):check(k,y,base,ctx+'/'+k)
   else:walk(y,base,ctx+'/'+k)
 elif isinstance(x,list):
  for i,y in enumerate(x):walk(y,base,ctx+'/'+str(i))
for n in ['coordination_handoff.json','visual_qa_manifest.json','retained_evidence_manifest.json','independent_source_review/selected_evidence_manifest.json','independent_source_review/candidate_vector_verification.json','independent_source_review/findings.json']:
 p=E/n;walk(json.loads(p.read_text(encoding='utf-8-sig')),p.parent,n)
doc=R/v['report']['path']; app=R/v['appendix']['path']; template=R/v['template']['path'];ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def xml_doc(p):
 with zipfile.ZipFile(p) as z:return ET.fromstring(z.read('word/document.xml'))
d=xml_doc(doc);t=xml_doc(template)
text=lambda x:''.join(x.xpath('.//w:t/text()',namespaces=ns))
manual=[]
for tr in t.xpath('//w:tr',namespaces=ns):
 st=text(tr)
 if any(s in st for s in ['SPPR calculation','Open issues and next action','Review and reproducibility']):
  label=text(tr.xpath('./w:tc',namespaces=ns)[0]); found=[x for x in d.xpath('//w:tr',namespaces=ns) if text(x.xpath('./w:tc',namespaces=ns)[0])==label]
  manual.append({'label':label,'match_count':len(found),'exact_xml':len(found)==1 and ET.tostring(tr)==ET.tostring(found[0])})
sec=ET.tostring(t.xpath('//w:sectPr',namespaces=ns)[-1])==ET.tostring(d.xpath('//w:sectPr',namespaces=ns)[-1])
links=[]
with zipfile.ZipFile(doc) as z:
 rel=ET.fromstring(z.read('word/_rels/document.xml.rels'));rels={x.get('Id'):x.get('Target') for x in rel}
 for node in d.xpath('//w:hyperlink',namespaces=ns):
  target=rels.get(node.get('{'+ns['r']+'}id')) or '#'+(node.get('{'+ns['w']+'}anchor')or'')
  runs=node.xpath('.//w:r',namespaces=ns); formats=[]
  for rr in runs:
   if not text(rr):continue
   rp=rr.find('w:rPr',namespaces=ns); c=rp.find('w:color',namespaces=ns) if rp is not None else None;u=rp.find('w:u',namespaces=ns) if rp is not None else None;s=rp.find('w:rStyle',namespaces=ns) if rp is not None else None
   formats.append({'color':c.get('{'+ns['w']+'}val') if c is not None else None,'underline':u.get('{'+ns['w']+'}val') if u is not None else None,'style':s.get('{'+ns['w']+'}val') if s is not None else None})
  blue=all(x['color'] in ('0563C1','0000FF') and x['underline'] not in (None,'none','0') or x['style']=='Hyperlink' for x in formats)
  links.append({'container':doc.relative_to(R).as_posix(),'label':text(node),'target':target,'blue_underlined':blue,'formats':formats})
wb=openpyxl.load_workbook(app,data_only=False)
for s in wb:
 for row in s:
  for c in row:
   if c.hyperlink:
    target=c.hyperlink.target or '#'+(c.hyperlink.location or '')
    color=c.font.color; blue=color is not None and color.type=='rgb' and color.rgb[-6:] in ['0563C1','0000FF'] and c.font.underline is not None
    links.append({'container':app.relative_to(R).as_posix(),'sheet':s.title,'cell':c.coordinate,'label':str(c.value),'target':target,'blue_underlined':blue})
local=[]
for l in links:
 target=l['target'];parsed=urlsplit(target)
 if parsed.scheme in ['http','https','mailto']:l['destination_type']='external';continue
 if target.startswith('#'):
  l['destination_type']='internal'; anchor=target[1:];l['destination_exists']=True
  if 'sheet'in l:
   if '!'in anchor:
    sheet,cell=anchor.split('!',1);sheet=sheet.strip("'").replace("''", "'");l['destination_exists']=sheet in wb.sheetnames
  else:l['destination_exists']=bool(d.xpath('//w:bookmarkStart[@w:name=$name]',namespaces=ns,name=anchor))
  continue
 container=R/l['container'];path=(container.parent/unquote(parsed.path)).resolve();l['destination_type']='relative';l['destination_exists']=path.is_file();l['absolute_or_escape']=Path(parsed.path).is_absolute() or not path.is_relative_to(R)
 if path.is_file():
  l['destination_hash']=sha(path); local.append((container,path,parsed.fragment))
relocated=Q/'relocated_repository'; copied=[]
for path in sorted(set([doc,app]+[p for _,p,_ in local])):
 if not path.is_relative_to(R):raise RuntimeError('external local destination')
 dest=relocated/path.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest);copied.append({'source':path.relative_to(R).as_posix(),'sha256':sha(path),'relocated_sha256':sha(dest)})
for l in links:
 if l.get('destination_type')=='relative':
  cont=relocated/l['container'];dest=(cont.parent/unquote(urlsplit(l['target']).path)).resolve();l['relocated_exists']=dest.is_file();l['relocated_hash_matches']=dest.is_file() and sha(dest)==l.get('destination_hash')
a=json.loads((E/'taxon_audit.json').read_text(encoding='utf-8-sig')); scar=[x for x in a if x['taxon']=='Scaridae']; appendix_rows=[]
for s in wb:
 for row in s:
  vals=[c.value for c in row]
  if any(isinstance(x,str) and ('Scaridae'in x or '125557'in x or '151787'in x or '398089'in x) for x in vals):appendix_rows.append({'sheet':s.title,'row':row[0].row,'values':vals,'links':[c.hyperlink.target if c.hyperlink else None for c in row]})
texts=[text(x) for x in d.xpath('//w:p',namespaces=ns)]; terms=['TE','unavailable','DIVERGED','near-singular','Very low','Original','unrecovered','source','1980']
science=[x for x in texts if any(y.lower() in x.lower() for y in terms)]
report={'status':'PRELIMINARY automated checks; visual inspection pending','ownership':'Read-only regional production; scratch writes only final_LME052_package_QA','handoff':obj(H),'artifact_bindings':[obj(doc),obj(app),obj(template)],'manifest_hash_checks':checks,'manifest_hash_failures':[c for c in checks if not c['pass']],'manual_researcher_rows':manual,'section_geometry_identical':sec,'actual_link_count':len(links),'links':links,'relative_link_count':len(local),'physical_relocation':copied,'link_failures':[l for l in links if not l['blue_underlined'] or l.get('destination_exists') is False or l.get('absolute_or_escape') or l.get('relocated_hash_matches') is False],'Scaridae_audit':scar,'Scaridae_appendix':appendix_rows,'science_disclosure_paragraphs':science,'visual_files':v['word_pages']+v['appendix_views'],'science_approval':False}
(Q/'automated_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checks':len(checks),'hash_failures':report['manifest_hash_failures'],'manual':manual,'section':sec,'links':len(links),'local':len(local),'link_failures':report['link_failures'],'Scaridae_audit':scar,'Scaridae_appendix':appendix_rows,'science':science},ensure_ascii=True,indent=2))
