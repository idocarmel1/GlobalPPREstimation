from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET,sys,csv,re,subprocess,math,copy,zipfile
from decimal import Decimal
from openpyxl import load_workbook,Workbook
import numpy as np
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'regions/LME_029';O=Path(__file__).parent;M=R/'models/BEN2020_Southern_Benguela_1978';T=M/'extracted_tables';D=M/'diagnostics';SK=Path('C:/Users/idoca/.agents/skills/ecopath-extraction')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
ex=load(O/'extraction_input.json');can=load(M/'model.json');ev=load(O/'pdf_cell_evidence.json')
# Independent Poppler words validate PyMuPDF table cells, with native PDF coordinates.
ns={'x':'http://www.w3.org/1999/xhtml'}
pages={name:ET.parse(O/file).getroot().findall('.//x:page',ns) for name,file in [('supplement','supplement_poppler_bbox.html'),('main','main_poppler_bbox.html')]}
coord=[]
for e in ev:
 if 'bbox' not in e:continue
 x0,y0,x1,y1=e['bbox'];found=[]
 for w in pages[e['source']][e['page']-1].findall('x:word',ns):
  cx=(float(w.attrib['xMin'])+float(w.attrib['xMax']))/2;cy=(float(w.attrib['yMin'])+float(w.attrib['yMax']))/2
  if x0-.3<=cx<=x1+.3 and y0-1<=cy<=y1+1:found.append(w.text or '')
 raw=''.join(found).strip();v=e.get('printed',e['value']);okay=raw==v
 if not okay:
  try:okay=Decimal(raw)==Decimal(v)
  except:pass
 coord.append({'table':e['table'],'page':e['page'],'group':e.get('prey',e.get('group',e.get('group_name'))),'column':e.get('predator',e.get('fleet',e.get('field'))),'pymupdf':v,'poppler':raw,'match':okay})
dump(O/'independent_pdf_cell_verification.json',{'checks':len(coord),'mismatches':[r for r in coord if not r['match']],'cells':coord})
assert all(r['match'] for r in coord),[r for r in coord if not r['match']][:8]
# Source extraction vs database canonical: all scalar fields, every diet and catch, all taxonomy.
checks=0
for s,g in zip(ex['groups'],can['group']):
 assert s['n']==int(g['group_seq']) and s['name']==g['group_name']
 for sk,gk in [('biomass','biomass'),('pb','pb'),('qb','qb'),('ee','ee'),('pq','ge'),('unassim','gs'),('z','source_total_mortality'),('tl','source_trophic_level')]:
  sv=s.get(sk);gv=g[gk];assert (gv=='-9999') if sv is None else Decimal(sv)==Decimal(gv),(s['name'],sk,sv,gv);checks+=1
 if str(s['n']) in ex['diet']:
  diet=g['diet_descr']['diet'];diet=[diet] if isinstance(diet,dict) else diet;by={x['prey_seq']:x['proportion'] for x in diet}
  for prey,v in ex['diet'][str(s['n'])].items():
   val=g['diet_imp'] if prey=='import' else by.get(prey,'0');assert Decimal(v)==Decimal(val);checks+=1
 if str(s['n']) in ex['landings']:
  assert math.isclose(float(g['export']),sum(map(float,ex['landings'][str(s['n'])].values())),rel_tol=1e-14,abs_tol=1e-15);checks+=1
 assert g['taxon_descr'];checks+=1
# Reconstruct all eight EwE parameter artifacts from canonical source fields and retained fleet records.
def known(v):return None if str(v)=='-9999' else v
back={'metadata':ex['metadata'],'groups':[],'consumers':[],'fleets':can['source_metadata']['source_fleets'],'landings':can['source_metadata']['source_fleet_catch'],'discards':{},'detritus_groups':[],'detritus_fate':{},'diet':{},'diet_rows':49,'landings_rows':48,'discards_rows':48}
for g in can['group']:
 n=int(g['group_seq']);s={'n':n,'name':g['group_name'],'biomass':known(g['biomass_habitat_area']),'hab_area':known(g['habitat_area']),'z':known(g['source_total_mortality']),'pb':known(g['pb']),'qb':known(g['qb']),'ee':known(g['ee']),'pq':known(g['ge']),'unassim':known(g['gs']),'tl':known(g['source_trophic_level']),'detritus_import':known(g['detritus_import'])}
 if n==47:s['ba']=g['biomass_accum'] # canonical source_metadata explicitly labels WC lobster BA absolute
 elif g['biomass_accum_rate']!='-9999':s['ba_rate']=g['biomass_accum_rate']
 elif g['biomass_accum']!='-9999':s['ba']=g['biomass_accum']
 back['groups'].append(s)
 if g['pp']=='2':back['detritus_groups'].append(g['group_name'])
 if g['pp']=='0':
  back['consumers'].append(n);d={str(i):'0' for i in range(1,50)};d['import']=g['diet_imp'];entries=g['diet_descr']['diet'];entries=[entries] if isinstance(entries,dict) else entries
  d.update({v['prey_seq']:v['proportion'] for v in entries});back['diet'][str(n)]=d
back['consumers'].sort();dump(O/'canonical_roundtrip_input.json',back)
subprocess.run([sys.executable,str(SK/'scripts/write_outputs.py'),str(O/'canonical_roundtrip_input.json'),'--outdir',str(M),'--dir-name','roundtrip_imports'],check=True,capture_output=True)
roundtrip=[]
for f in ['Basic_input.csv','Biomass_accumulation.csv','Detritus_fate.csv','Diet_composition.csv','Discards.csv','Landings.csv','TL.xlsx','Metadata.xlsx']:
 if f.endswith('.csv'):
  a=list(csv.reader((T/f).open(encoding='utf-8')));b=list(csv.reader((M/'roundtrip_imports'/f).open(encoding='utf-8')))
 else:
  a=list(load_workbook(T/f,data_only=True).active.values);b=list(load_workbook(M/'roundtrip_imports'/f,data_only=True).active.values)
 assert len(a)==len(b),(f,len(a),len(b));nc=0
 for ar,br in zip(a,b):
  assert len(ar)==len(br)
  for av,bv in zip(ar,br):
   okay=av==bv
   if not okay:
    try:okay=Decimal(str(av))==Decimal(str(bv))
    except:pass
   assert okay,(f,av,bv);nc+=1
 roundtrip.append({'file':f,'cells':nc,'semantic_match':True})
# Actual source production checks; no unreported BA, GS or PB filled in these source rows.
source_balance=[]
for g in ex['groups']:
 n=g['n'];pred=sum(float(ex['groups'][int(j)-1]['biomass'])*float(ex['groups'][int(j)-1]['qb'])*float(d.get(str(n),0)) for j,d in ex['diet'].items());catch=sum(map(float,ex['landings'].get(str(n),{}).values()));pb=g['pb'];prod=float(g['biomass'])*float(pb) if pb else None;ba=float(g['ba']) if g.get('ba') is not None else float(g['ba_rate'])*float(g['biomass']) if g.get('ba_rate') is not None else None
 source_balance.append({'seq':n,'group':g['name'],'production':prod,'predation':pred,'catch':catch,'BA':ba,'EE_printed':g['ee'],'EE_without_unreported_BA':(pred+catch+(ba or 0))/prod if prod else None,'interpretation':'known BA' if ba is not None else 'BA unknown: zero omitted from arithmetic only; no balance assertion'})
dump(T/'source_production_budget.json',source_balance)
# Source-estimated bold cells captured explicitly from native text font metadata.
import pymupdf as fitz
pdf=fitz.open(R/'papers/BEN-2020/pdf-00952390.pdf');estimated=[]
for e in ev:
 if e['source']!='main' or 'bbox' not in e:continue
 x0,y0,x1,y1=e['bbox']
 for block in pdf[e['page']-1].get_text('dict')['blocks']:
  for ln in block.get('lines',[]):
   for sp in ln['spans']:
    a,b,c,d=sp['bbox']
    if abs(a-x0)<.5 and abs(b-y0)<.5 and ('Bold' in sp['font'] or sp['font'].endswith('-Bd') or sp['flags']&16):estimated.append(e)
dump(T/'source_model_estimated_cells.json',estimated)
manifest=load(O/'source_manifest.json');assert all(hashlib.sha256((ROOT/v['file']).read_bytes()).hexdigest()==v['sha256'] for v in manifest)
returns={o:load(D/(o.lower().replace(' ','_')+'_direct_return.json')) for o in ['GE','TE','With Egestion']}
# Diagnostic report contains only the direct method outputs and links to separate source review.
diag='# Full direct SPPR diagnostic returns\n\nModel: `BEN2020_Southern_Benguela_1978` (documented P/Q-completed diagnostic input).\n\nCalls: `PPRCalculator.diagnose_sppr(TE_option=..., short=False, flat=False)`. Source qualifications and staging details are in `../extracted_tables/REPORT.md` and `staging_transformations.json`.\n'
for option,result in returns.items():diag+='\n## '+option+'\n\n```json\n'+json.dumps(result,indent=2,ensure_ascii=False)+'\n```\n'
(D/'DIRECT_SPPR_REPORT.md').write_text(diag,encoding='utf-8')
spatial={'unit_id':'LME_029','study_area_km2':220000,'source':'main PDF page3 methods and Figure1','extent':'Orange River mouth approximately29S to East London28E; southern Benguela west and south coasts','fit':'partial; excludes northern Benguela off Namibia','target_coverage_ratio':None,'legacy_ratio':0.5,'legacy_ratio_status':'unverified inherited estimate; not adopted as measured overlap','legacy_footprint':'14–28E,37–29S rectangle is only a search/display envelope, not the blue-shaded shelf polygon','figure_evidence':'renders/main_3.png','no_false_precision':'No precise coverage percentage computed from this bounding box.'}
dump(O/'spatial_fit_review.json',spatial)
results={'unit_id':'LME_029','model_id':M.name,'paper_id':'BEN-2020','year':1978,'publication_year':2020,'groups':49,'consumers':45,'primary_producers':3,'detritus':1,'fleets':31,'selected':False,'production_eligible':False,'source_status':'complete transcription with explicit missing fields and multistanza interpretation caveat','diagnostic_status':{o:r['status'] for o,r in returns.items()},'diagnostic_input':'P/Q×Q/B completion for two missing deep-water hake PB values only; source canonical remains unknown; standard documented defaults','numerical_repair':False,'diagnostics':{o:{'status':r['status'],'input_status':r['model_input']['status'],'max_production_relative_residual':r['model_input']['p_max_rel_residual'],'PP_budget_status':r['balance']['status'],'PP_budget_relative_gap':r['balance']['rel_gap'],'strict_balance':r['balance']['is_balanced']} for o,r in returns.items()},'spatial':spatial,'source_files_verified_unchanged':True,'central_registration':'proposal only; parent owns Project.xlsx','regional_workbook_modified':False}
dump(O/'results_record.json',results)
proposal={'unit_id':'LME_029','paper_updates':[{'article_id':'BEN-2020__LME_029','title':'Exploring Temporal Variability in the Southern Benguela Ecosystem Over the Past Four Decades Using a Time-Dynamic Ecosystem Model','authors':'Shannon LJ; Ortega-Cisneros K; Lamont T; Winker H; Crawford R; Jarre A; Coll M','publication_year':2020,'doi':'10.3389/fmars.2020.00540','model_years':'1978 baseline; Ecosim fitted1978–2015','functional_groups':49,'supplement_status':'downloaded_verified_and_numerically_used','model_file_status':'source-faithful extraction completed; native EwE file not supplied','target_coverage_ratio':None,'geometry_note':'Southern Benguela220000km2, Orange River29S to East London28E. Legacy50% estimate unverified; retained bbox not exact footprint.','selected':False,'extraction_readiness':'completed with source qualifications'}],'models_to_upsert':[{'unit_id':'LME_029','model_id':M.name,'article_id':'BEN-2020__LME_029','source':'Shannon et al.2020 doi10.3389/fmars.2020.00540 Table2 and supplementS1–S4','model_year':1978,'functional_groups':49,'model_path':str((M/'model.json').relative_to(ROOT)),'coverage_class':'partial','target_coverage_ratio':None,'selected':False,'production_eligible':False,'status':'extracted; direct GE/TE/With Egestion allFAIL on documented P/Q-completed diagnostic input','notes':'Unresolved multistanza Z/PB and sardine BA conventions. No biological repair or model adoption.'}],'report_path':str((T/'REPORT.md').relative_to(ROOT))}
dump(O/'central_metadata_proposal.json',proposal)
verification={'status':'PASS','independent_Poppler_numeric_cell_checks':len(coord),'source_canonical_field_checks':checks,'eight_file_semantic_roundtrip':roundtrip,'estimated_bold_cells_retained':len(estimated),'source_files_unchanged':True,'canonical_missing_PB_groups':[30,31],'source_diet_sums_retained':{'Apex Chondrichthyans':1.0001,'Cape Cormorant':1.0002},'important_limit':'PASS means transcription/roundtrip integrity, not scientific model balance. All three direct diagnostics FAIL. Metadata supplied from extraction context in roundtrip; parameter and fleet data reconstructed from canonical.','canonical_sha256':hashlib.sha256((M/'model.json').read_bytes()).hexdigest()}
dump(O/'VERIFICATION.json',verification)
print('verified',verification['independent_Poppler_numeric_cell_checks'],'PDF cells',checks,'canonical fields',sum(x['cells'] for x in roundtrip),'roundtrip cells')
