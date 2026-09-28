from pathlib import Path
import json,csv,re,sys,subprocess,copy,hashlib
from decimal import Decimal
import fitz
from openpyxl import Workbook,load_workbook
ROOT=Path(__file__).resolve().parents[4]; REVIEW=Path(__file__).resolve().parent; E=REVIEW/'evidence'
SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
NATIVE=json.loads((E/'PAT-2023_native_tables.json').read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def clean(x):
 x=str(x).strip().replace('−','-').replace(' ','').strip('()')
 return None if x in ['','–','-','-9999','-9999.0'] else x
def words(page):
 out=[]
 for w in page.get_text('words'):
  r=fitz.Rect(w[:4])*page.rotation_matrix
  out.append(dict(x0=r.x0,y0=r.y0,x1=r.x1,y1=r.y1,text=w[4]))
 return out
def recttext(ws,x0,y0,x1,y1):
 picked=[w for w in ws if x0<=(w['x0']+w['x1'])/2<x1 and y0<=(w['y0']+w['y1'])/2<y1]
 picked.sort(key=lambda w:(round(w['y0']/3),w['x0']))
 return ' '.join(w['text'] for w in picked)
patdoc=fitz.open(next((ROOT/'regions/LME_014/papers/PAT-2023').glob('*.pdf')))
printed=[]; evidence=[]
for pi in [13,14]:
 if pi==14:patdoc[pi].set_rotation(90)
 ws=words(patdoc[pi]);dump(E/f'PAT_page_{pi+1}_display_words.json',ws)
 anchors=sorted([w for w in ws if w['text'].isdigit() and 48<w['x0']<63 and 80<w['y0']<560],key=lambda w:w['y0'])
 for j,a in enumerate(anchors):
  n=int(a['text']); y0=a['y0']-1;y1=anchors[j+1]['y0']-1 if j+1<len(anchors) else a['y1']+25
  bounds=[75,185,236,300,393,455,535,620,700,771]
  vals=[recttext(ws,bounds[k],y0,bounds[k+1],y1) for k in range(9)]
  row={'n':n,'name':vals[0],**dict(zip(['tl','hab_area','biomass','biomass_model_area_printed','pb','qb','ee','pq'],map(clean,vals[1:])))}
  printed.append(row);evidence.append(dict(table='PAT article Table 4',pdf_page=pi+1,group=n,bbox=[48,y0,771,y1],raw_cells=vals))
assert [g['n'] for g in printed]==list(range(1,37)),printed
dump(E/'PAT_printed_basic.json',printed)
dump(E/'PAT_printed_cell_evidence.json',evidence)

pat_tax=[
'Balaenoptera borealis','Munida gregaria','Micromesistius australis','Schroederichthys bivius; Squalus acanthias','Mancopsetta maculata','Coelorinchus fasciatus','Merluccius australis','Merluccius hubbsi','Macruronus magellanicus','Illex argentinus','Unidentified or Chrysaora','Lessonia flavicans; Lessonia trabeculata; Macrocystis pyrifera','Genypterus blacodes','Cottoperca gobio; Iluocoetes/Patagolycus mix; Psychrolutes marmoratus; Eleginops maclovinus','Corals; Sponges','Doryteuthis gahi — autumn-spawning cohort (ASC)','Doryteuthis gahi — spring-spawning cohort (SSC)','Gymnoscopelus nicholsi','Enteroctopus megalocyathus; Pareledone spp.; Octopus spp.','Seriolella porosa; Allothunnus fallai; Stromateus brasiliensis; Congiopodus peruvianus; Lampris immaculatus; Sprattus fuegensis','Pygoscelis papua; Spheniscus magellanicus; Eudyptes spp.; Aptenodytes patagonicus','not documented — Table 2 names Phytoplankton without species','Salilota australis','Patagonotothen ramsayi','Puffinus gravis; Puffinus griseus; Pygoscelis papua; Thalassarche melanophrys','Arctocephalus australis; Otaria flavescens; Mirounga leonina','Lamna nasus','Bathyraja albomaculata; Bathyraja brachyurops; Dipturus lamillai','Champsocephalus esox; Cottunculus granulosus; Paranotothenia magellanica; Patagonotothen tessellata; Sebastes oculatus','Polychaetes; Scallops; Bivalves; Nematodes','Moroteuthopsis ingens; Martialia hyadesi; Semirossia patagonica','Orcinus orca; Cephalorhynchus commersonii; Lagenorhynchus australis','Dissostichus eleginoides — juvenile','Euphausiacea; Chaetognatha; Amphipoda; Copepoda; Munida gregaria (juv)','Discards — separate prey category for discard feeders/scavengers; article p.9','POM; Detritus; Discards — Table 2 combines these, whereas Table 4/native database separate Discards']
base={'metadata':{'LME':'14 Patagonian Shelf','model_number':'PAT2024','model_name':'Falkland Shelf','model_year':2020},'groups':[],'consumers':[i for i in range(1,35) if i not in [12,22]],'fleets':['Trawling','Jigging'],'landings':{},'discards':{},'detritus_groups':['Discards','Detritus'],'detritus_fate':{},'diet':{},'diet_rows':36}
native=copy.deepcopy(base);native['metadata']['model_number']='PAT2024-native'
idseq={g['GroupID']:g['Sequence'] for g in NATIVE['EcopathGroup']}; seqgroup={g['Sequence']:g for g in NATIVE['EcopathGroup']}
for s,g in sorted(seqgroup.items()):
 row={'n':s,'name':g['GroupName'],'hab_area':str(g['Area']),'biomass':None if g['Biomass']==-9999 else str(Decimal(str(g['Biomass']))/Decimal(str(g['Area']))),'tl':printed[s-1]['tl']}
 for src,dst in [('ProdBiom','pb'),('ConsBiom','qb'),('EcoEfficiency','ee'),('OtherMort','other_mort'),('ProdCons','pq'),('Unassim','unassim'),('DtImports','detritus_import'),('BiomAcc','ba')]:row[dst]=clean(g[src])
 native['groups'].append(row)
 if s in native['consumers']:
  native['diet'][str(s)]={'import':str(g['ImpVar'])}
  for r in NATIVE['EcopathDietComp']:
   if r['PredID']==g['GroupID']:native['diet'][str(s)][str(idseq[r['PreyID']])]=str(r['Diet'])
 native['detritus_fate'][str(s)]={seqgroup[idseq[r['PreyID']]]['GroupName']:str(r['DetritusFate']) for r in NATIVE['EcopathDietComp'] if r['PredID']==g['GroupID'] and idseq[r['PreyID']] in [35,36]}
 for key,src in [('landings','Landing'),('discards','Discards')]:
  native[key][str(s)]={next(f['FleetName'] for f in NATIVE['EcopathFleet'] if f['FleetID']==r['FleetID']):str(r[src]) for r in NATIVE['EcopathCatch'] if r['GroupID']==g['GroupID']}

paper=copy.deepcopy(base);paper['metadata']['model_number']='PAT2024-tables';paper['groups']=copy.deepcopy(printed)
# Preserve native spellings only in native version. Printed Table 4 names remain exact.
paper['detritus_groups']=[paper['groups'][34]['name'],paper['groups'][35]['name']]
pat_sup=json.loads((E/'PAT-2023_supplement.json').read_text(encoding='utf-8'))
for row in pat_sup['tables'][2][2:-2]:
 s=int(row[0])
 for key,cols in [('landings',[2,3]),('discards',[5,6])]:paper[key][str(s)]={fleet:clean(row[c]) for fleet,c in zip(paper['fleets'],cols)}
# S4 Detritus row is number 35 in that table but matches Table4 Detritus=36 by name.
for key,cols in [('landings',[2,3]),('discards',[5,6])]:paper[key]['36']={fleet:clean(pat_sup['tables'][2][-2][c]) for fleet,c in zip(paper['fleets'],cols)}
csvrows=list(csv.reader(next((ROOT/'regions/LME_014/papers/PAT-2023').glob('*.csv')).open()))
# S2 numbers exclude producer groups among consumers; match names explicitly to native aliases.
aliases={'Illex':'I. argentinus'}
name_seq={g['name'].casefold():g['n'] for g in native['groups']}
for ci,name in enumerate(csvrows[0][2:],2):
 s=name_seq[name.casefold()];diet={}
 for r in csvrows[2:]:
  if r[1]=='Sum':continue
  v=clean(r[ci]);key='import' if r[1]=='Import' else str(name_seq[r[1].casefold()])
  diet[key]=str(Decimal(v)/100) if v is not None else None
 paper['diet'][str(s)]=diet

ocdoc=fitz.open(next((ROOT/'regions/LME_014/papers/LME014-OcampoReinaldo-2016').glob('*.pdf')))
ws=words(ocdoc[4]);oc_sup=json.loads((E/'LME014-OcampoReinaldo-2016_supplement.json').read_text(encoding='utf-8'))
names=[r[1] for r in oc_sup['tables'][0][2:-1]]
anchors=sorted([w for w in ws if 130<=w['x0']<146 and 484<w['y0']<740 and re.fullmatch(r'[0-9.]+',w['text'])],key=lambda w:w['y0'])
assert len(anchors)==26,len(anchors)
oc={'metadata':{'LME':'14 Patagonian Shelf','model_number':'OcampoReinaldo2016','model_name':'San Matias Gulf','model_year':1970},'groups':[],'consumers':list(range(1,25)),'fleets':['Trawlers','Long-liners','Jiggers'],'landings':{},'discards':{},'detritus_groups':['Detritus'],'detritus_fate':{},'diet':{},'diet_rows':26}
evidence=[]
for n,(a,name) in enumerate(zip(anchors,names),1):
 y0=a['y0']-1;y1=a['y1']+1
 bounds=[130,169,218,300,385,459,518,565]
 raw=[recttext(ws,bounds[k],y0,bounds[k+1],y1) for k in range(7)]
 vals=list(map(clean,raw));g={'n':n,'name':name,**dict(zip(['tl','biomass','pb','qb','ee','pq','omnivory_index'],vals))}
 if n in [14,15,16]:g['z']=g['pb']
 oc['groups'].append(g);evidence.append(dict(table='Ocampo Table 2',pdf_page=5,printed_page=35,group=n,bbox=[130,y0,565,y1],raw_cells=raw))
for ti in [0,1]:
 t=oc_sup['tables'][ti]
 for c,pred in enumerate(t[1][2:],2):
  d={}
  for ri,r in enumerate(t[2:],3):d['import' if r[1]=='Import' else r[0]]=clean(r[c])
  oc['diet'][pred]=d
dump(E/'Ocampo_basic_cell_evidence.json',evidence)
oc_tax=['Delphinus delphis; Lagenorhynchus obscurus','Otaria flavescens; Arctocephalus australis','Discopyge tschudii; Torpedo puelcha; Milyobatis spp.','Dipturus chilensis; Atlantoraja platana; A. castelnaui; Sympterigia bonapartii','A. cyclophora; Psammobatis spp.; Sympterigia acuta','Notorhynchus cepedianus; Sphyrna zygaena; Carcharias taurus; Carcharinus brachyurus','Squatina guggenheim; Squalus acanthias; Galeorhinus galeus','Juvenile of Large and medium-sized sharks','Mustelus schmitti','Pseudopercis semifasciata; Acanthistius patachonicus; Polyprion americanus','Paralichthys isosceles; P. patagonicus; Xistreurys rasile','Juvenile of Pseudopercis semifasciata and Acanthistius patachonicus; Genypterus brasiliensis; Macruronus magellanicus','Callorhinchus callorhynchus','Merluccius hubbsi — more than 53 cm / 6 years old','Merluccius hubbsi — 24 to 53 cm; already mature','Merluccius hubbsi — juvenile young-of-the-year; less than 23 cm','Genypterus blacodes','Macruronus magellanicus','Parona signata; Stromateus brasiliensis; Seriolella porosa; Scomber japonicus','Engraulis anchoita; Trachurus lathami','Illex argentinus; Loligo sanpaulensis; L. gahi','Pleoticus muelleri; benthic crustaceans; Bivalvia; Polichaeta; other benthic organisms','Ctenophora; Salpidae; Hydrozoa','Euphausiids; Copepods; Cladocerans; Ostracods','Diatoms; Dinoflagellates','Detritus — nonliving pool; Table 1 provides no taxonomic composition']

models=[('PAT2024_FalklandShelf_2020_native',native,pat_tax),('PAT2024_FalklandShelf_2020_published_tables',paper,pat_tax),('OcampoReinaldo2016_SanMatiasGulf_1970',oc,oc_tax)]
for mid,data,tax in models:
 folder=ROOT/'regions/LME_014/models'/mid;folder.mkdir(exist_ok=True)
 dump(folder/'extraction_input.json',data)
 cmd=[sys.executable,str(SKILL/'write_outputs.py'),str(folder/'extraction_input.json'),'--outdir',str(folder),'--dir-name','extracted_tables']
 subprocess.run(cmd,check=True,capture_output=True)
 tab=folder/'extracted_tables'
 wb=Workbook();sh=wb.active;sh.append(['seq','group_name','taxon_descr'])
 for g,t in zip(data['groups'],tax):sh.append([g['n'],g['name'],t])
 wb.save(tab/'Taxonomy.xlsx')
 with (tab/'taxonomy.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(['seq','group_name','taxon_descr','source'])
  for g,t in zip(data['groups'],tax):w.writerow([g['n'],g['name'],t,'Article Table 2 pp7-8 and p9' if mid.startswith('PAT') else 'Article Table 1 PDF p4 / printed p34; hake sizes in prose p34'])
 for script,args,log in [('validate.py',[str(tab)],'validation.txt'),('massbalance_check.py',[str(tab)],'source_massbalance.txt'),('database_json.py',['-d',str(tab),'--update-report'],'converter_output.txt')]:
  p=subprocess.run([sys.executable,str(SKILL/script),*args],capture_output=True,text=True,encoding='utf-8',errors='replace');(tab/log).write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
  print(mid,script,p.returncode)
 generated=list(tab.glob('*_(*).json'));assert len(generated)==1,generated
 canonical=json.loads(generated[0].read_text())
 changes=[]
 for g,src,t in zip(canonical['group'],data['groups'],tax):
  s=str(src['n']);old=copy.deepcopy(g)
  def val(k):return str(src[k]) if src.get(k) is not None else '-9999'
  g.update(taxon_descr=t,gs=val('unassim'),ge=val('pq'),tl=val('tl'),habitat_area=val('hab_area'),detritus_import=val('detritus_import'),diet_imp=str(data['diet'].get(s,{}).get('import') or '-9999'))
  # Zero remains zero, distinct from None.
  if data['diet'].get(s,{}).get('import') is not None:g['diet_imp']=str(data['diet'][s]['import'])
  g['pp']='2' if src['name'] in data['detritus_groups'] else ('1' if (src['n'] in ([12,22] if mid.startswith('PAT') else [25])) else '0')
  g['biomass']=val('biomass_model_area_printed') if 'biomass_model_area_printed' in src else (str(Decimal(str(src['biomass']))*Decimal(str(src.get('hab_area') or '1'))) if src.get('biomass') else '-9999')
  vals=[v for key in ['landings','discards'] for v in data[key].get(s,{}).values()]
  g['export']=str(sum(Decimal(v) for v in vals if v is not None)) if vals and all(v is not None for v in vals) else '-9999'
  if mid.endswith('_native'):
   ng=seqgroup[int(s)];g.update(biomass=clean(ng['Biomass']) or '-9999',diet_imp=str(ng['ImpVar']),immigration=str(ng['Immigration']),emigration=str(ng['Emigration']),emigration_rate=str(ng['EmigRate']),biomass_accum=str(ng['BiomAcc']),biomass_accum_rate=str(ng['BiomAccRate']))
  # Restore source values after converter normalization and default substitution.
  diet=[]
  for prey in data['groups']:
   ps=str(prey['n']);proportion=data['diet'].get(s,{}).get(ps);fate=data['detritus_fate'].get(s,{}).get(prey['name'])
   if s in data['diet'] or fate is not None: diet.append({'prey_seq':ps,'proportion':str(proportion) if proportion is not None else '-9999','detritus_fate':str(fate) if fate is not None else '-9999'})
  g['diet_descr']={'diet':diet} if diet else None
  for key in g:
   if g[key]!=old.get(key):changes.append({'group':s,'field':key,'converter':old.get(key),'canonical':g[key]})
 dump(folder/'model.json',canonical);dump(tab/'converter_canonical_differences.json',changes)
 p=subprocess.run([sys.executable,str(SKILL/'database_json.py'),'-j',str(folder/'model.json')],capture_output=True,text=True,encoding='utf-8',errors='replace');(tab/'canonical_reconstruction.txt').write_text(p.stdout+p.stderr,encoding='utf-8')
 print(mid,'groups',len(data['groups']),'dietsums',[(s,str(sum(Decimal(v) for v in d.values() if v is not None))) for s,d in data['diet'].items()])
dump(REVIEW/'model_ids.json',[m[0] for m in models])
