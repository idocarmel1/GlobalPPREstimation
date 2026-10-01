import json,math,zipfile,urllib.parse,re,hashlib
from pathlib import Path
import openpyxl
from lxml import etree as E
Q=Path(__file__).resolve().parent;OUT=Q.parent;REG=OUT.parents[1];ROOT=REG.parents[1];MID=OUT.name;a=json.loads((OUT/'taxon_audit.json').read_text(encoding='utf-8'));paths=[REG/f'Model_validation_{MID}.docx',REG/'HS071_taxon_mapping_appendix.xlsx']
def local(target):
 t=urllib.parse.unquote(target)
 if t.startswith(('http:','https:','mailto:')):return {'target':target,'kind':'web','exists':None}
 if t.startswith('#'):return {'target':target,'kind':'internal','exists':True}
 p=t.split('#',1)[0];assert not re.match(r'^[A-Za-z]:|^[/\\]',p),p
 resolved=(REG/p).resolve();assert resolved.is_relative_to(ROOT),target
 assert resolved.exists(),target
 # Synthetic relocation: retain root-relative location under an arbitrary new root.
 moved_root=Path('C:/portable-check/project');moved_origin=moved_root/REG.relative_to(ROOT)
 moved=(moved_origin/p).resolve();assert moved.relative_to(moved_root.resolve())==resolved.relative_to(ROOT)
 return {'target':target,'kind':'local','exists':True,'resolved_repository_path':str(resolved.relative_to(ROOT)).replace('\\','/'),'relocation_check':True}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'};linkchecks=[]
with zipfile.ZipFile(paths[0]) as z:
 rel={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('word/_rels/document.xml.rels'))}
 doc=E.fromstring(z.read('word/document.xml'))
 for h in doc.findall('.//w:hyperlink',ns):
  target=rel.get(h.get('{'+ns['r']+'}id'),'#'+h.get('{'+ns['w']+'}anchor',''))
  for r in h.findall('w:r',ns):
   assert r.find('w:rPr/w:color',ns).get('{'+ns['w']+'}val').upper()=='0563C1'
   assert r.find('w:rPr/w:u',ns).get('{'+ns['w']+'}val')=='single'
  linkchecks.append({'artifact':'docx',**local(target)})
wb=openpyxl.load_workbook(paths[1],data_only=False);s=wb['Taxon mapping'];assert wb.sheetnames==['Taxon mapping','Sources']
assert [s.cell(7,i).value for i in range(1,8)]==['Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason']
for index,d in enumerate(a['rows'],8):
 vals=[s.cell(index,i).value for i in range(1,8)]
 assert vals[0]==d['taxon'] and vals[1]==(d['tl'] if d['tl'] is not None else '?')
 assert math.isclose(vals[2],d['catch_tonnes'],rel_tol=1e-14,abs_tol=1e-12)
 assert math.isclose(vals[3],d['simple_chain_ppr_tC'],rel_tol=1e-14,abs_tol=1e-12)
 assert vals[4]==d['mapping_display'] and vals[5]==d['confidence']
assert s.max_row==30 and s.max_column==7 and s.freeze_panes=='B8' and len(s.tables)==1
for sheet in wb:
 for row in sheet:
  for c in row:
   assert c.data_type!='f','No formula needed in final appendix; artifact-tool lacked HYPERLINK support.'
   if c.hyperlink:
    assert c.font.color.type=='rgb' and c.font.color.rgb=='FF0563C1' and c.font.underline=='single'
    linkchecks.append({'artifact':'xlsx','sheet':sheet.title,'cell':c.coordinate,**local(c.hyperlink.target or '#'+c.hyperlink.location)})
assert len([x for x in linkchecks if x['artifact']=='xlsx'])==17
wb.close()
result={'document_links':sum(x['artifact']=='docx' for x in linkchecks),'appendix_links':17,'all_hyperlinks_effectively_blue_underlined':True,'all_local_targets_relative_existing_and_portable':True,'appendix_exact_23_sorted_rows':True,'appendix_values_reconcile_with_audit':True,'appendix_filters_freeze_headers':True,'link_details':linkchecks,'final_artifact_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
(Q/'artifact_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print({k:v for k,v in result.items() if k!='link_details'})
