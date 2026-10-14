from pathlib import Path
from decimal import Decimal
from datetime import datetime, timezone
import json, re, csv, hashlib, shutil, sys, subprocess
import pdfplumber
from docx import Document
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[6]
REGION = ROOT / 'regions/EEZ/EEZ_939'
WORK = Path(__file__).resolve().parents[1]
PAPER = REGION / 'papers/Corrales-2010'
RESOURCE = ROOT / 'tools/skills/paper-to-ppr/resources/extraction'
RUN = WORK.name
NAMES = ['Phytoplankton','Benthic primary producers','Micro and mesozooplankton',
 'Macrozooplankton','Gelatinous plankton','Polychaetes','Suprabenthos',
 'Native shrimps','Alien shrimps','Native crabs','Alien crabs','Benthic invertebrates',
 'Benthic cephalopods','Benthopelagic cephalopods','Mullets','Goatfishes','Hake',
 'Flatfishes','Rocky fishes','Small native dem. fishes','Large native dem. fishes',
 'Alien herbivores','Earlier alien dem. fishes','New alien dem. fishes','Alien lizardfish',
 'Demersal fishes (upper slope)','Benthopelagic fishes','Mesopelagic fishes',
 'Demersal sharks','Rays and skates','Small pelagic fishes','Horse mackerel','Mackerel',
 'Native medium pelagic fishes','Alien medium pelagic fishes','Large pelagic fishes',
 'Turtles','Sea birds','Dolphins','Detritus','Discards']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, value): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def safe(p):
 p=p.resolve(); assert p.is_relative_to(ROOT); return p

sources = [('1-s2.0-S0924796316302329-main.pdf','sources','article'),
 ('1-s2.0-S0924796316302329-mmc1.docx','sources/supplements','author_supplement')]
manifest=[];dispositions=[]
for filename, folder, role in sources:
 old=PAPER/filename; target=safe(PAPER/folder/filename)
 if old.exists():
  original_hash=sha(old); target.parent.mkdir(parents=True,exist_ok=True)
  assert not target.exists(); shutil.move(str(safe(old)),str(target)); assert sha(target)==original_hash
  dispositions.append([old.relative_to(ROOT).as_posix(),target.relative_to(ROOT).as_posix(),original_hash,original_hash,'relocation','User requested agreed paper source layout; original bytes preserved','EEZ_939','',RUN])
 manifest.append({'path':target.relative_to(PAPER).as_posix(),'sha256':sha(target),'bytes':target.stat().st_size,'role':role,'publication_year':2017,'numerical_use':'Both published periods; table/cell locators retained per model','original_filename':filename,'retrieval':'Downloaded by researcher and provided locally; download timestamp unknown'})
if dispositions:
 ledger=ROOT/'common_reference_data/provenance/source_paths.csv'
 with ledger.open('a',encoding='utf-8',newline='') as f: csv.writer(f,lineterminator='\n').writerows(dispositions)
dump(PAPER/'source_manifest.json',{'schema_version':1,'article_id':'Corrales-2017-ICS','folder_alias':'Corrales-2010','citation':'Corrales X, Ofir E, Coll M, Goren M, Edelist D, Heymans JJ, Gal G (2017). Modeling the role and impact of alien species and fisheries on the Israeli marine continental shelf ecosystem. Journal of Marine Systems 170:88–102.','doi':'10.1016/j.jmarsys.2017.02.004','modeled_periods':['1990–1994','2008–2012'],'model_area_km2':'3725','files':manifest,'identity_note':'The researcher-supplied folder alias is retained. Publication year is 2017, not 2010.'})
pdf=PAPER/'sources'/sources[0][0]; doc=PAPER/'sources/supplements'/sources[1][0]
supp=Document(doc)
raw_tables=[[[c.text for c in row.cells] for row in table.rows] for table in supp.tables]

def read_numeric_grid(page_index, ncols, first_x, step):
 with pdfplumber.open(pdf) as d:
  p=d.pages[page_index-1]
  markers=[w for w in p.extract_words(x_tolerance=.6,y_tolerance=2) if 47<w['x0']<50 and w['text'].isdigit() and 100<w['top']<480]
  assert [int(w['text']) for w in markers]==list(range(1,42))
  out={}; ledger=[]
  for marker in markers:
   sid=int(marker['text']); vals=[]
   for ci in range(ncols):
    left=first_x+step*ci; box=(left-3,marker['top']-2.3,left+step-3,marker['top']+7)
    chars=[c for c in p.chars if box[0]<=c['x0']<box[2] and box[1]<=(c['top']+c['bottom'])/2<=box[3]]
    text=''.join(c['text'] for c in sorted(chars,key=lambda c:c['x0'])).strip()
    assert text in ('','–','−','-') or re.fullmatch(r'\d+\.\d+',text),(sid,ci,text)
    val=None if text in ('','–','−','-') else text
    vals.append(val); ledger.append({'source_group_id':sid,'column_index':ci,'literal':text,'value':val,'bold':any('Bold' in c['fontname'] or c['fontname'].endswith('.B') for c in chars),'pdf_page':page_index,'printed_page':87+page_index,'bbox':box})
   out[sid]=vals
  return out,ledger

basic,basic_ledger=read_numeric_grid(4,14,166.34,28.6015)
outputs,output_ledger=read_numeric_grid(6,12,173.82,32.71)
# Derive output-table anchors from the full first row instead of assuming spacing.
with pdfplumber.open(pdf) as d:
 p=d.pages[5]; ww=p.extract_words(x_tolerance=.6,y_tolerance=2)
 first=[w for w in ww if 115<=w['top']<120 and w['x0']>180]
 print('Output anchors',[(w['text'],w['x0']) for w in first])

definitions={};provenance={};current=None
for ri,row in enumerate(raw_tables[0]):
 m=re.match(r'^(\d+)\.\s*(.*)',row[0].strip(),re.S)
 if m:
  current=int(m.group(1)); definitions[current]=m.group(2).strip();provenance[current]=[]
 elif current and row[0].strip(): provenance[current].append({'field':row[0].strip(),'text':row[1],'docx_table':0,'row':ri})
assert len(definitions)==41

common_companions={
 'Supplement_parameter_provenance.csv':{'description':'Verbatim online supplement section 1 parameter sources and group descriptions; source grid','layout':'source_grid','rows':raw_tables[0]},
 'Supplement_alien_species.csv':{'description':'Online supplement section 2 alien species, arrival dates and stated group memberships; source grid','layout':'source_grid','rows':raw_tables[1]},
 'Supplement_balanced_outputs.csv':{'description':'Online supplement section 3 R/A R/B P/R and net efficiency; both periods, source grid','layout':'source_grid','rows':raw_tables[2]},
 'Supplement_pedigree.csv':{'description':'Online supplement section 6 uncertainty option/index/CI definitions; source grid','layout':'source_grid','rows':raw_tables[7]},
 'Supplement_PREBAL.csv':{'description':'Verbatim author PREBAL rationale and adjustments, online supplement section 4','rows':[['paragraph_index','text']]+[[str(i),p.text] for i,p in enumerate(supp.paragraphs) if p.text.strip() and 'References' not in p.text and i<60]},
}
indicator_names=['Number of functional groups','Number of primary producers','Number of alive functional groups','Total system throughput','Primary production / respiration','Primary production / biomass','System omnivory index','Finn cycling index','Finn mean path length','Total biomass excluding detritus','Mean trophic level of community','Community trophic level excluding TL1','Total catches','Total landings','Total discards','Mean trophic level of catch','Primary production required including PP and detritus','Mean transfer efficiency','Ecopath pedigree index']
indicator_values=[['39','41','count'],['2','2','count'],['37','39','count'],['646.36','631.89','t/km2/year'],['4.26','4.26','ratio'],['28.32','27.28','per year'],['0.19','0.19','index'],['5.72','5.78','percent TST'],['2.62','2.63','length'],['8.69','8.80','t/km2'],['1.35','1.34','TL'],['2.62','2.60','TL'],['0.94','0.93','t/km2/year'],['0.80','0.64','t/km2/year'],['0.14','0.29','t/km2/year'],['3.38','3.37','TL'],['10.36','11.34','percent'],['18.90','19.00','percent'],['0.54','0.54','index']]
common_companions['Article_ecosystem_indicators.csv']={'description':'Verbatim numerical outputs from Article Table 3, PDF8 printed95; period outputs not importer parameters','rows':[['indicator','1990_1994','2008_2012','units','source']]+[[name]+values+['Article Table3 PDF8 printed95'] for name,values in zip(indicator_names,indicator_values)]}
for period,pi,tids in [('1990_1994',0,[3,4]),('2008_2012',1,[5,6])]:
 ids=[i for i in range(1,42) if pi==1 or i not in (24,35)]
 seq={sid:i+1 for i,sid in enumerate(ids)}
 groups=[];landings={};discards={};diets={};cells=[];source_params=[]
 for sid in ids:
  n=seq[sid];v=basic[sid];o=outputs[sid];roles={}
  for fld,col in [('biomass',0),('pb',2),('qb',4),('ee',6),('pq',8)]:
   ev=next(x for x in basic_ledger if x['source_group_id']==sid and x['column_index']==col+pi)
   roles[fld]='published_input' if ev['bold'] else 'balanced_reported'
  if any(x['field']=='B' and 'Estimated' in x['text'] for x in provenance[sid]):roles['biomass']='model_estimated'
  groups.append({'n':n,'name':NAMES[sid-1],'biomass':v[pi],'pb':v[2+pi],'qb':v[4+pi],'ee':v[6+pi],'pq':v[8+pi],'tl':o[pi],'parameter_roles':roles,'source_status':{'published_group_id':sid,'published_table':'Article Table 1','absent_period_groups':[24,35] if pi==0 else []}})
  landings[str(n)]={'Reported aggregate fisheries':v[10+pi]};discards[str(n)]={'Reported aggregate fisheries':v[12+pi]}
  for col,field in enumerate(['B_1990s','B_2010s','PB_1990s','PB_2010s','QB_1990s','QB_2010s','EE_1990s','EE_2010s','PQ_1990s','PQ_2010s','Landings_1990s','Landings_2010s','Discards_1990s','Discards_2010s']):
   if col%2==pi:
    ev=next(x for x in basic_ledger if x['source_group_id']==sid and x['column_index']==col)
    source_params.append([str(sid),str(n),NAMES[sid-1],field,ev['literal'],'published_numeric' if ev['value'] is not None else 'printed_dash_or_blank',str(ev['bold']),'4','91',str(ev['bbox']),sha(pdf)])
 for ti in tids:
  table=supp.tables[ti];grid=raw_tables[ti]
  for ci,consumer in enumerate(grid[0][1:],1):
   sid=int(consumer);n=seq[sid];diets[str(n)]={}
   for ri,row in enumerate(grid[1:],1):
    label=row[0].strip();literal=row[ci].strip();cell=table.rows[ri].cells[ci]
    sh=cell._tc.xpath('.//w:shd');gray=bool(sh and sh[0].get(qn('w:fill'))=='BFBFBF')
    if label=='Total':
     cells.append([str(sid),str(n),'Total','',literal,'published_total','',str(ti),str(ri),str(ci),sha(doc)]);continue
    prey=seq[int(label)] if label.isdigit() else 'import'
    if literal: diets[str(n)][str(prey)]=literal
    elif gray:diets[str(n)][str(prey)]=None
    elif prey=='import':diets[str(n)]['import']=None
    status='censored_less_than_0.01' if gray else ('published_numeric' if literal else 'unprinted_blank')
    cells.append([str(sid),str(n),label,str(prey),literal,status,'0.01' if gray else '',str(ti),str(ri),str(ci),sha(doc)])
 companions=dict(common_companions)
 companions['Source_group_crosswalk.csv']={'description':'Exact published identities and compact EwE import sequence; source IDs 24 and 35 are absent only in 1990–1994','rows':[['published_group_id','import_seq','group_name','source_definition','definition_source']]+[[str(s),str(seq[s]),NAMES[s-1],definitions[s],'Supplement section 1'] for s in ids]}
 companions['Source_basic_cells.csv']={'description':'Article Table 1 source literals, missing markers, bold input markings and exact geometry','rows':[['published_group_id','import_seq','group_name','field_period','source_literal','source_status','bold_initial_input','pdf_page','printed_page','bbox_points','source_sha256']]+source_params}
 companions['Source_diet_cells.csv']={'description':'Online supplement section 5 exact numeric/blank/censored cells; no hidden fraction reconstructed or normalized','rows':[['published_consumer_id','consumer_seq','published_prey_id','prey_seq','source_literal','status','upper_bound_exclusive','docx_table_index','row_index','cell_index','source_sha256']]+cells}
 companions['Article_group_outputs.csv']={'description':'Article Table 2 output fields for the exact period; TL, F, M2, M0, F/Z and detritus flow retained as outputs','rows':[['published_group_id','import_seq','group_name','TL','F_per_year','M2_per_year','M0_per_year','F_over_Z','FD_t_per_km2_year','source']]+[[str(s),str(seq[s]),NAMES[s-1]]+[outputs[s][2*j+pi] or '' for j in range(6)]+['Article Table 2 PDF6 printed93'] for s in ids]}
 for ti in tids:companions[f'Supplement_diet_block_{ti}.csv']={'description':f'Verbatim source grid supplement section 5 table {1 if pi==0 else 2}, block {ti}; gray-cell status in Source_diet_cells','layout':'source_grid','rows':raw_tables[ti]}
 extraction={'metadata':{'LME':'EEZ_939 Israel Mediterranean','model_number':f'ICS_{period}','model_name':'Israeli Mediterranean continental shelf','model_year':period.replace('_','–'),'biomass_basis':'whole_model_area','publication_year':2017,'area_km2':'3725','doi':'10.1016/j.jmarsys.2017.02.004','model_identifier_basis':'Project publication-period identifier; no EcoBase accession asserted'},'groups':groups,'consumers':[seq[s] for s in ids if 3<=s<=39],'fleets':['Reported aggregate fisheries'],'landings':landings,'discards':discards,'diet':diets,'diet_rows':len(ids),'detritus_groups':['Detritus','Discards'],'detritus_fate':{},'companions':companions}
 inputfile=WORK/f'inputs/extraction_{period}.json';dump(inputfile,extraction)
 outparent=WORK/f'outputs/{period}';outparent.mkdir(parents=True,exist_ok=True)
 command=[sys.executable,'-X','utf8',str(RESOURCE/'scripts/write_outputs.py'),str(inputfile),'--outdir',str(outparent)]
 result=subprocess.run(command,text=True,encoding='utf-8',capture_output=True);print(result.stdout);print(result.stderr);assert result.returncode==0
 stage=next(p for p in outparent.iterdir() if p.is_dir())
 (stage/'REPORT.md').write_text(f'# Israeli Mediterranean continental shelf {period.replace("_","–")}\n\nSource: Corrales et al. (2017), doi:10.1016/j.jmarsys.2017.02.004.\n\nConversion is source-faithful and retains missingness. Final evidence and limitations are recorded after checks.\n',encoding='utf-8')
 dump(WORK/f'outputs/stage_{period}.json',{'path':str(stage),'model_id':f'Corrales_2017_ICS_{period}','source_group_ids':ids,'source_sha256':sha(pdf),'supplement_sha256':sha(doc)})
 print(period,len(groups),'groups',sum(r[5]=='censored_less_than_0.01' for r in cells),'censored diet cells')
