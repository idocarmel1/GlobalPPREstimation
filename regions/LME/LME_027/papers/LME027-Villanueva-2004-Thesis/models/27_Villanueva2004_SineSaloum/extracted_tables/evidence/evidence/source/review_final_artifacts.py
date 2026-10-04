from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from collections import Counter
import openpyxl,json,hashlib,math
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'Model_validation_27_Villanueva2004_SineSaloum_Thesis_1991-1992.docx'
XLS=ROOT/'LME027_Villanueva2004_thesis_taxon_mapping_appendix.xlsx'
z=ZipFile(DOC);xml=etree.fromstring(z.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
text='\n'.join(x.text or '' for x in xml.findall('.//w:t',ns))
word_tables=[[''.join(t.text or '' for t in c.findall('.//w:t',ns)) for c in r.findall('w:tc',ns)] for r in xml.findall('.//w:tr',ns)]
rows=json.loads((ROOT/'mapping/appendix_rows.json').read_text(encoding='utf-8'))
members=json.loads((ROOT/'mapping/table3_3_literal_membership.json').read_text(encoding='utf-8'))
wb=openpyxl.load_workbook(XLS,read_only=False,data_only=False)
data=list(wb['Taxon mapping'].values)[7:]
expected_headers=list(rows[0]);bad=[]
for idx,(source,actual) in enumerate(zip(rows,data),8):
 for col,key in enumerate(expected_headers):
  a=actual[col];b=source[key]
  if isinstance(b,(int,float)) and not isinstance(b,bool):
   equal=isinstance(a,(int,float)) and math.isclose(a,b,rel_tol=1e-14,abs_tol=1e-7)
  else:equal=(a==b)
  if not equal:bad.append({'row':idx,'field':key,'source':b,'artifact':a})
bytaxon={r['Taxon name']:r for r in rows}
confidence_counts=Counter(r['Confidence level'] for r in rows)
confidence_table={r[0]:r for r in word_tables if len(r)==4 and r[0] in ['High','Medium','Low','Very low','Unresolved']}
confidence_summary_matches=all(k in confidence_table and confidence_table[k][1]==str(confidence_counts.get(k,0)) for k in ['High','Medium','Low','Very low','Unresolved'])
totalcatch=sum(r['Catch (t)'] for r in rows);totalppr=sum(r['Simple-chain PPR (t C)'] for r in rows)
percent_mismatches=[]
for level,r in confidence_table.items():
 for col,key,total in [(2,'Catch (t)',totalcatch),(3,'Simple-chain PPR (t C)',totalppr)]:
  actual=sum(x[key] for x in rows if x['Confidence level']==level)/total*100
  token=r[col].rstrip('%');shown=float(token);places=len(token.split('.')[1]) if '.' in token else 0
  if abs(actual-shown)>0.5*10**(-places)+1e-10:percent_mismatches.append({'confidence':level,'field':key,'exact_percent':actual,'display':r[col]})
misclassified=[{'taxon':m['species_literal'],'pool':m['pool_label_inherited'],'source_page':m['pdf_page'],'confidence':bytaxon[m['species_literal']]['Confidence level']} for m in members if m.get('Saloum') in ['+','*'] and m['species_literal'] in bytaxon and bytaxon[m['species_literal']]['Confidence level']=='Very low']
links=[]
for s in wb:
 for row in s:
  for cell in row:
   if cell.hyperlink:
    target=cell.hyperlink.target
    if not target.startswith(('http://','https://')):links.append({'sheet':s.title,'cell':cell.coordinate,'target':target,'resolves':(ROOT/target.split('#')[0]).resolve().exists()})
checks={'word_source37groups_and1991_1992':'37-group' in text and '1991–1992' in text,'word_fraction_caption_and_exact_sums':'fractions despite its percent caption' in text and '0.999–1.000' in text,'word_group20_conflict_disclosed':'Epinephelus aeneus' in text and 'Hemichromis fasciatus' in text and 'Group 20 is unresolved' in text,'word_GE_TE_egestion_NOT_RUN':text.count('NOT_RUN')>=3,'word_no_adoption_unsigned':'unsigned candidate review draft' in text and 'active selection remains EcoBase 118' in text,'word_researcher_name_and_date_blank':'Researcher name: ____________________' in text and 'review date: dd/mm/yyyy' in text,'word_calculation_choices_manual':'[Researcher calculation choices and notes]' in text,'xlsx512records':len(data)==len(rows)==512,'xlsx_all_values_match_saved_evidence':not bad,'xlsx_local_sources_links_resolve':all(l['resolves'] for l in links),'word_no_blanket_other_models_outside_claim':'These lie outside the target LME' not in text,'source_member_confidence_fallthrough_absent':not misclassified}
checks['word_confidence_counts_match512records']=confidence_summary_matches
checks['word_confidence_percentages_correctly_rounded']=not percent_mismatches
findings=[]
if misclassified:findings.append({'id':'F1','severity':'requires_correction','issue':'Explicit Saloum source member classified Very low as unlisted analogue','evidence':misclassified})
if not checks['word_no_blanket_other_models_outside_claim']:findings.append({'id':'F2','severity':'requires_clarification','issue':'Blanket statement that Gambia, Ebrie and Nokoue are outside Canary Current exceeds the audited geographic evidence for Gambia. Use separate-model/applicability-not-evaluated wording.'})
if not confidence_summary_matches or percent_mismatches:findings.append({'id':'F3','severity':'requires_correction','issue':'Word confidence summary differs from final512record mapping evidence.','counts':dict(confidence_counts),'percent_mismatches':percent_mismatches})
result={'reviewer':'independent source-extraction agent','method':'Read-only DOCX XML and all XLSX cells; checked thesis Tables6.5,3.3,AnnexIIA and extracted/mapping evidence. Visual artifact rendering is the coordinator review.','docx_sha256':hashlib.sha256(DOC.read_bytes()).hexdigest(),'xlsx_sha256':hashlib.sha256(XLS.read_bytes()).hexdigest(),'checks':checks,'xlsx_cells_checked':len(rows)*7,'xlsx_cell_mismatches':bad,'source_members_misclassified':misclassified,'local_hyperlinks':links,'findings':findings,'status':'PASS' if not findings and all(checks.values()) else 'CORRECTIONS_REQUIRED'}
out=ROOT/'evidence/source/final_artifact_review.json'
if out.exists():
 prior=json.loads(out.read_text(encoding='utf-8'))
 if prior.get('docx_sha256')!=result['docx_sha256'] or prior.get('xlsx_sha256')!=result['xlsx_sha256']:
  result['prior_review']={k:prior[k] for k in ['docx_sha256','xlsx_sha256','findings','status']}
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'checks':checks,'findings':findings},ensure_ascii=True))
