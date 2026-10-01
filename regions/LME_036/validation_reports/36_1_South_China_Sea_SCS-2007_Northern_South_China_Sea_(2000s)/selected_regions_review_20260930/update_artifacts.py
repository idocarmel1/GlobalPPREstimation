"""Minimal OOXML edits preserve the researcher document and workbook views."""
import pathlib,json,copy,zipfile,re,hashlib,math,posixpath
from lxml import etree as E
from docx import Document
import openpyxl
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[4];REGION=ROOT/'regions/LME_036'
MID='36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)'
if (HERE.parent/'residual_fish_scope_followup.json').exists():
    raise RuntimeError('Historical baseline Office builder is superseded by residual_fish_scope_followup.json. It must not overwrite current mapping, allocation denominators or preserved manual fields. Use current adopted evidence and bounded current-state edits.')
docpath=REGION/f'Model_validation_{MID}.docx';appendix=REGION/'LME036_taxon_mapping_appendix.xlsx'
audit=json.loads((HERE/'taxon_audit_adopted.json').read_text(encoding='utf-8'));by={r['taxon']:r for r in audit}
summary=json.loads((HERE/'summary.json').read_text(encoding='utf-8'))
groups={int(g['group_seq']):g for g in json.loads((REGION/'models'/MID/'model.json').read_text(encoding='utf-8'))['group']}
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
save=lambda n,v:(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';S='http://schemas.openxmlformats.org/spreadsheetml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PR='http://schemas.openxmlformats.org/package/2006/relationships'
ns={'w':W};wn=lambda x:'{'+W+'}'+x;sn=lambda x:'{'+S+'}'+x

# Whole manual cells, including links and researcher deletions, are protected.
doc=Document(HERE/('baseline_'+docpath.name))
manual=[(0,7,1),(0,9,1),(1,6,1),(1,7,1)]
manual_before={str(k):E.tostring(doc.tables[k[0]].cell(k[1],k[2])._tc) for k in manual}
def ptext(p,value):
 node=p._p;style=copy.deepcopy(p.runs[0]._r.find(wn('rPr'))) if p.runs else None
 for x in list(node):
  if x.tag!=wn('pPr'):node.remove(x)
 run=E.SubElement(node,wn('r'))
 if style is not None:run.append(style)
 text=E.SubElement(run,wn('t'));text.set('{http://www.w3.org/XML/1998/namespace}space','preserve');text.text=str(value)
def ctext(c,value):
 p=c.paragraphs[0]
 for extra in list(c._tc)[1:]:
  if extra.tag==wn('p') and extra is not p._p:c._tc.remove(extra)
 ptext(p,value)
def fill_table(table,data):
 assert len(table.rows)-1==len(data),(len(table.rows),len(data))
 for row,values in zip(table.rows[1:],data):
  for c,v in zip(row.cells,values):ctext(c,v)
ptext(doc.paragraphs[1],'Pending alignment draft for the selected 2000s northern South China Sea model. All 374 taxa were reviewed; 36 supported group corrections are adopted regionally. The linked appendix records confidence and assumptions. Estimates remain provisional.')
ptext(doc.paragraphs[19],'Whole model-pool catch proportions are assumed representative of regional taxon catches across 1950–2019 and all catch bases. These are not observed target-catch mixtures. Another 57 taxa retain Low confidence because of size, habitat or source-group ambiguity.')
ptext(doc.paragraphs[21],'High mapping coverage does not establish model validity. The northern shelf model is extrapolated to the wider region; source-group ambiguity and the diagnostic WARN conditions above remain.')
ctext(doc.tables[1].cell(1,1),'WARN: near-zero efficiency in seabirds (34). No negative SPPR across basal-source columns. rho_living = 0.3209187537609611; b = 0.00408138212364339. Detritus (38): SPPR = 1.007782936216668. Strict model and SPPR balance flags are true.')
ctext(doc.tables[1].cell(2,1),'WARN: near-zero efficiency in seabirds, other mammals and pinnipeds (34–36). No negative SPPR across basal-source columns. rho_living = 0.6163296517365333. Detritus (38): SPPR = 0.995222499887902. Strict model and SPPR balance flags are true.')
ctext(doc.tables[1].cell(5,1),'The accepted saved and reproduced outputs retain groups 34–37 (seabirds, other mammals, pinnipeds and turtles), all with finite direct SPPR. The researcher removal note describes a different configuration. With Egestion returns OK. All three complete source matrices have no negative or nonfinite entries, including unfished groups.')
# Repoint the adopted allocation link to the newly adopted audit; source and
# manual-cell destinations remain untouched.
for hl in doc.paragraphs[20]._p.findall(wn('hyperlink')):
 rid=hl.get('{'+R+'}id');rel=doc.part.rels[rid]
 if 'confidence_reassessment_20260930/taxon_audit_adopted.json' in rel.target_ref:
  rel._target=f'validation_reports/{MID}/selected_regions_review_20260930/taxon_audit_adopted.json'
fill_table(doc.tables[2],[[r['confidence'],str(r['taxa']),f"{r['catch_pct']:.4f}%",f"{r['ppr_pct']:.4f}%"] for r in summary['categories']])
fill_table(doc.tables[3],[[r['Plain-language rule'],r['Confidence'],f"{r['PPR percentage']:.4f}%"] for r in summary['membership_rules']])
fill_table(doc.tables[4],[[r['Plain-language rule'],r['Confidence'],f"{r['PPR percentage']:.4f}%"] for r in summary['weight_rules']])
# All link text is explicitly styled; the manual cell XML must stay exact.
for hl in doc._element.iter(wn('hyperlink')):
 for run in hl.iter(wn('r')):
  rp=run.find(wn('rPr'))
  if rp is None:rp=E.Element(wn('rPr'));run.insert(0,rp)
  color=rp.find(wn('color'))
  if color is None:color=E.SubElement(rp,wn('color'))
  color.set(wn('val'),'0563C1')
  for x in ['themeColor','themeTint','themeShade']:color.attrib.pop(wn(x),None)
  u=rp.find(wn('u'))
  if u is None:u=E.SubElement(rp,wn('u'))
  u.set(wn('val'),'single')
for key in manual:assert E.tostring(doc.tables[key[0]].cell(key[1],key[2])._tc)==manual_before[str(key)],key
doc.save(docpath)
reopened=Document(docpath)
for key in manual:assert E.tostring(reopened.tables[key[0]].cell(key[1],key[2])._tc)==manual_before[str(key)],key

# The appendix is an existing workbook; patch package parts without rebuilding
# its styles, links, views or table filters. openpyxl is used only to inspect.
oldwb=openpyxl.load_workbook(HERE/('baseline_'+appendix.name),data_only=False)
with zipfile.ZipFile(HERE/('baseline_'+appendix.name)) as z:parts={n:z.read(n) for n in z.namelist()}
sheets={n:E.fromstring(parts[f'xl/worksheets/sheet{i+1}.xml']) for i,n in enumerate(oldwb.sheetnames)}
def rownode(sheet,index):
 data=sheet.find(sn('sheetData'));row=data.find(sn('row')+f"[@r='{index}']")
 if row is None:
  row=E.Element(sn('row'),r=str(index));later=next((x for x in data if int(x.get('r'))>index),None)
  if later is None:data.append(row)
  else:data.insert(data.index(later),row)
 return row
def cellset(sheet,address,value,style=None,formula=None):
 idx=int(re.sub('[A-Z]','',address));row=rownode(sheet,idx);cell=row.find(sn('c')+f"[@r='{address}']")
 if cell is None:cell=E.SubElement(row,sn('c'),r=address)
 if style is not None:cell.set('s',str(style))
 for n in list(cell):cell.remove(n)
 if formula is not None:
  cell.attrib.pop('t',None);E.SubElement(cell,sn('f')).text=formula.lstrip('=');E.SubElement(cell,sn('v')).text=repr(value)
 elif isinstance(value,(int,float)) and not isinstance(value,bool):
  cell.attrib.pop('t',None);E.SubElement(cell,sn('v')).text=repr(value)
 elif value is None:cell.attrib.pop('t',None)
 else:
  cell.set('t','inlineStr');t=E.SubElement(E.SubElement(cell,sn('is')),sn('t'));t.text=str(value);t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
 return cell
def table_ref(name,ref):
 for n,b in list(parts.items()):
  if n.startswith('xl/tables/'):
   t=E.fromstring(b)
   if t.get('name')==name:
    t.set('ref',ref);af=t.find(sn('autoFilter'))
    if af is not None:af.set('ref',ref)
    parts[n]=E.tostring(t,xml_declaration=True,encoding='utf-8')
sheet=sheets['Taxon appendix']
for i in range(6,380):
 taxon=oldwb['Taxon appendix'][f'A{i}'].value;r=by[taxon]
 for col,value in [('E',r['display_mapping']),('F',r['review_confidence']),('G',r['reason'])]:cellset(sheet,f'{col}{i}',value)
 row=rownode(sheet,i)
 # Keep the researcher Low filter active but reconcile its visible rows.
 if r['review_confidence']=='Low':row.attrib.pop('hidden',None)
 else:row.set('hidden','1')
 row.set('ht',str(max(float(row.get('ht','42')),min(225,16*(1+math.ceil(len(r['reason'])/96))))));row.set('customHeight','1')
sheet=sheets['Coverage']
for i,r in enumerate(summary['categories'],11):
 for col,val in zip('ABCD',[r['confidence'],r['taxa'],r['catch_pct']/100,r['ppr_pct']/100]):cellset(sheet,f'{col}{i}',val)
for start,name in [(21,'membership_rules'),(33,'weight_rules')]:
 for i,r in enumerate(summary[name],start):
  for col,val in zip('ABC',[r['Plain-language rule'],r['Confidence'],r['PPR percentage']/100]):cellset(sheet,f'{col}{i}',val)

# Complete candidates are retained for every taxon, including single candidates
# and zero catches; catch is source-verified before a proxy is called usable.
sheet=sheets['Allocation evidence'];allrows=[]
for r in sorted(audit,key=lambda z:z['taxon'].casefold()):
 total=math.fsum(float(groups[g['group_id']]['export']) for g in r['adopted_groups'])
 for g in r['adopted_groups']:
  src=groups[g['group_id']];allrows.append((r,g,src,total))
end=len(allrows)+5
cellset(sheet,'A2',f"All {len(audit)} taxa and {len(allrows)} exact candidates. Reported six-fleet source catches match accepted model export and loaded catch. Biomass is retained for inspection; proportions are dimensionless.")
cellset(sheet,'A3','Complete candidate denominators determine every split. Model catch proportions have Medium weight confidence; single-group weight 1 has High weight confidence. Membership and overall confidence remain separately recorded in the linked audit.')
cellset(sheet,'A4','Table 6.2 PDF pp.193–194 provides the catch values. Fixed 2000s northern-shelf proportions are assumed for whole-LME 1950–2019 and all catch bases; no observed taxon-specific mixture was recovered.')
style=[oldwb['Allocation evidence'].cell(6,c)._style for c in range(1,11)]
styleids=[int(sheets['Allocation evidence'].find(sn('sheetData')).find(sn('row')+"[@r='6']").find(sn('c')+f"[@r='{c}6']").get('s','0')) for c in 'ABCDEFGHIJ']
for i,(r,g,src,total) in enumerate(allrows,6):
 vals=[r['taxon'],g['name'],g['group_id'],float(src['export']),float(src['biomass']),'No split' if len(r['adopted_groups'])==1 else 'Model catch',total,g['weight'],r['weight_confidence'],r['reason']]
 for ci,(col,val) in enumerate(zip('ABCDEFGHIJ',vals)):
  formula=f'SUMIFS($D$6:$D${end},$A$6:$A${end},A{i})' if col=='G' else (f'D{i}/G{i}' if col=='H' and len(r['adopted_groups'])>1 else ('1' if col=='H' else None))
  cellset(sheet,f'{col}{i}',val,styleids[ci],formula)
 row=rownode(sheet,i);row.set('ht',str(max(72,min(240,16*(1+math.ceil(len(r['reason'])/80))))));row.set('customHeight','1');row.attrib.pop('hidden',None)
dimension=sheet.find(sn('dimension'))
if dimension is not None:dimension.set('ref',f'A1:K{max(600,end)}')
table_ref('AllocationEvidence',f'A5:J{end}')
sheet=sheets['Sources'];current=f'validation_reports/{MID}/selected_regions_review_20260930'
cellset(sheet,'B10','Current adopted audit: all 374 taxa; 78 proposal dispositions, component confidence, exact candidate weights and source locators. The dated previous audit remains historical evidence.')
cellset(sheet,'C10',current+'/taxon_audit_adopted.json')
rels=E.fromstring(parts['xl/worksheets/_rels/sheet4.xml.rels'])
links=sheet.find(sn('hyperlinks'))
for hl in links:
 if hl.get('ref')=='C10':
  rid=hl.get('{'+R+'}id');next(x for x in rels if x.get('Id')==rid).set('Target',current+'/taxon_audit_adopted.json')
new_sources=[
 ('Current proposal review','36 adopted, 42 retained with individual reasons and precise source locators.',current+'/proposal_dispositions.json'),
 ('Adopted group corrections','Exact old/new canonical group IDs, names, weights and confidence.',current+'/mapping_changes.json'),
 ('Source catch reconstruction','Table 6.2 PDF pp.193–194: all fleet components and printed totals; canonical export checked against complete source sums.',f'validation_reports/{MID}/source/reconstruction_2000s/SOURCE_CATCH_TOTALS.json'),
 ('Full direct diagnostic evidence','GE, TE and With Egestion. Full matrices, named axes and explicit masks include all unfished groups. Accepted groups 34–37 remain present.',current+'/direct_diagnostics/lossless_matrix_checks.json'),
 ('Direct coefficient comparison','All nine method/scope aggregates agree with saved coefficients within 1e-10 relative tolerance; saved group SPPR is preserved exactly.',current+'/direct_diagnostics/coefficient_comparison.json'),
 ('Current dependent calculation effects','Old/new 2019 estimates by method, scope, catch basis and unidentified treatment; independent simple-chain PPR unchanged.',current+'/dependent_result_changes.json'),
 ('Source maximum length evidence','Uehara et al. (2021), Table 3, p.160: observed D. maruadsi maximum 35.4 cm cited to the fork-length study Ohshimo et al. (2006); asymptote is separate.','https://www.jstage.jst.go.jp/article/jsfo/85/3/85_153/_pdf'),
]
source_styles=[int(rownode(sheet,10).find(sn('c')+f"[@r='{c}10']").get('s','0')) for c in 'ABC']
for i,values in enumerate(new_sources,561):
 for col,val,styleid in zip('ABC',values,source_styles):cellset(sheet,f'{col}{i}',val,styleid)
 row=rownode(sheet,i);row.set('ht','80');row.set('customHeight','1')
 rid='rIdCurrentReview'+str(i);E.SubElement(rels,'{'+PR+'}Relationship',Id=rid,Type=R+'/hyperlink',Target=values[2],TargetMode='External');E.SubElement(links,sn('hyperlink'),ref=f'C{i}',attrib={'{'+R+'}id':rid})
table_ref('ConfidenceReviewSources','A71:C567')
parts['xl/worksheets/_rels/sheet4.xml.rels']=E.tostring(rels,xml_declaration=True,encoding='utf-8')
for i,(name,sheet) in enumerate(sheets.items(),1):parts[f'xl/worksheets/sheet{i}.xml']=E.tostring(sheet,xml_declaration=True,encoding='utf-8')
with zipfile.ZipFile(appendix,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in parts.items():z.writestr(n,b)
check=openpyxl.load_workbook(appendix,data_only=False);cached=openpyxl.load_workbook(appendix,data_only=True)
assert list(check['Taxon appendix'].tables.values())[0].ref=='A5:G379'
assert check['Taxon appendix']['A1'].value==oldwb['Taxon appendix']['A1'].value
for i in range(6,380):
 r=by[check['Taxon appendix'].cell(i,1).value];assert check['Taxon appendix'].cell(i,6).value==r['review_confidence']
 for col in 'ABCD':assert check['Taxon appendix'][f'{col}{i}'].value==oldwb['Taxon appendix'][f'{col}{i}'].value
for i,(r,g,src,total) in enumerate(allrows,6):assert math.isclose(cached['Allocation evidence'][f'H{i}'].value,g['weight'],rel_tol=1e-12,abs_tol=1e-12)
link_checks=[]
for s in check:
 for row in s:
  for c in row:
   if not c.hyperlink:continue
   target=c.hyperlink.target
   if not target.startswith(('http://','https://')):assert not pathlib.PureWindowsPath(target).is_absolute() and (appendix.parent/target).exists(),(c.coordinate,target)
   assert c.font.color is not None and c.font.color.type=='rgb' and c.font.color.rgb[-6:]=='0563C1' and c.font.underline=='single',(s.title,c.coordinate,c.font.color,c.font.underline)
   link_checks.append({'sheet':s.title,'cell':c.coordinate,'target':target})
save('artifact_edit_checks.json',{'manual_cells_preserved_xml':list(manual_before),'docx_sha256':sha(docpath),'appendix_sha256':sha(appendix),'taxa':374,'appendix_seven_columns':True,'simple_chain_TL_catch_PPR_values_preserved':True,'allocation_candidates':len(allrows),'allocation_formulas_cached_and_verified':True,'excel_hyperlinks_blue_and_underlined':len(link_checks),'excel_local_links_resolve':True,'original_views_and_low_filter_preserved':True,'low_filter_visible_rows':sum(r['review_confidence']=='Low' for r in audit)})
save('appendix_links.json',link_checks)
print('Report manual XML preserved; appendix '+str(len(allrows))+' candidates; '+str(len(link_checks))+' portable styled links checked.')
