"""Fresh source-cell assembly; no old extraction/model is read."""
from pathlib import Path
import json,csv,hashlib,sys,copy,importlib.util
from decimal import Decimal
ROOT=Path(__file__).resolve().parent
E=ROOT/'evidence'
N=ROOT/'resolved_native'; N.mkdir(exist_ok=True)
C=ROOT/'computational'; C.mkdir(exist_ok=True)
def jwrite(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=json.loads((E/'supplement_cells.json').read_text(encoding='utf-8'))
S={s['name']:s for s in raw['sheets']}
cells={n:{(c['row'],c['column']):c for c in s['cells']} for n,s in S.items()}
ledger=[]
def val(sheet,r,c,field=None,gid=None,consumer=None,prey=None):
    cell=cells[sheet][r,c]
    v=cell['value']
    if field:
        ledger.append({'group_id':gid,'consumer_id':consumer,'prey_id':prey,'field':field,'source_file':'../../../papers/HUM-2018/Supplementary material revised and final.xls','source_sha256':raw['source_sha256'],'sheet':sheet,'cell':cell['address'],'native_value':v,'literal':None if v is None else str(v),'number_format':cell['number_format'],'missingness':'source_blank' if v is None else 'source_numeric_zero' if v==0 else 'source_numeric','estimated_by_model':cell['bold'],'adopted_value':v,'transformation':'none'})
    return v
taxonomy={
1:('Diatoms; species not enumerated.','focal group name; inherited plankton structure Tam2008 p353','generic group definition'),
2:('Dinoflagellates and silicoflagellates; species not enumerated.','focal name; Tam2008 p353','generic group definition'),
3:('Microzooplankton, 20–200 µm; source inherited size class.','Tam2008 PDFp2/printedp353, Methods2.1','size class'),
4:('Mesozooplankton, 200–2000 µm; source inherited size class.','Tam2008 PDFp2/printedp353, Methods2.1','size class'),
5:('Macrozooplankton, 2–20 mm; source inherited size class.','Tam2008 PDFp2/printedp353, Methods2.1','size class'),
6:('Small gelatinous zooplankton; taxa not enumerated; excludes the separately added Chrysaora plocamia group.','focal PDFp3/printedp30; TableE B13','generic group definition'),
7:('Chrysaora plocamia medusae, large scyphozoan jellyfish; top 7.5 m layer used for biomass integration.','focal PDFp2–3/printedp29–30','single species'),
8:('Macrobenthos; species composition not documented in the focal or inspected predecessor methods.','TableA B13; Tam2008 p353','not documented'),
9:('Sardinops sagax.','focal PDFp2/printedp29; Tam2008 p353','single species'),
10:('Engraulis ringens.','focal PDFp2/printedp29; Tam2008 p353','single species'),
11:('Mesopelagic fishes: Vinciguerria lucetia, Lampanyctus spp., Leuroglossus spp.; source spellings retained.','Tam2008 PDFp2/printedp353, Methods2.1','enumerated members; exhaustiveness unspecified'),
12:('Dosidicus gigas.','Tam2008 PDFp2/printedp353, Introduction','single species'),
13:('Other cephalopods: Loligo gahi, Octopus vulgaris, Logigunculla sp.; historical source spellings retained.','Tam2008 PDFp2/printedp353, Methods2.1','enumerated members; exhaustiveness unspecified'),
14:('Other small pelagic fishes; Anchoa nasus is an explicit example. Scomberesox saurus, Exocoetidae and Sufflogobius bibarbatus in predecessor Table1 are parameter analogues, not established local members.','Tam2008 PDFp2/printedp353 Methods2.1; Table1 p355','representative example'),
15:('Trachurus murphyi.','Tam2008 PDFp2/printedp353, Methods2.1','single species'),
16:('Scomber japonicus, source historical name.','Tam2008 PDFp2/printedp353, Methods2.1','single species'),
17:('Other large pelagic fishes; explicit examples Sarda chiliensis, Coryphaena hippurus and Thunnus albacares.','Tam2008 PDFp2/printedp353, Methods2.1','representative examples'),
18:('Merluccius gayi peruanus, small hake <29 cm. Source does not specify length convention and leaves the printed boundary gap unresolved.','Tam2008 PDFp2/printedp353, Methods2.1','size class within species'),
19:('Merluccius gayi peruanus, medium hake 30–49 cm. Source does not specify length convention.','Tam2008 PDFp2/printedp353, Methods2.1','size class within species'),
20:('Merluccius gayi peruanus, large hake >50 cm. Source does not specify length convention and leaves the printed boundary gap unresolved.','Tam2008 PDFp2/printedp353, Methods2.1','size class within species'),
21:('Flatfishes: Paralichthys adspersus, Hippoglosina sp.; source spelling retained.','Tam2008 PDFp2/printedp353, Methods2.1','enumerated members; exhaustiveness unspecified'),
22:('Small demersal fishes; examples Odonthestes regia, Labrisomus philippi, Ctenosciaena peruviana; source spellings retained. No numerical size limit documented.','Tam2008 PDFp2/printedp353, Methods2.1','representative examples'),
23:('Benthic elasmobranchs; source does not enumerate species.','TableA B28; Tam2008 p353','generic group definition'),
24:('Butter fishes: Trachinotus paitensis, Stromateus stellatus, Peprilus medius.','Tam2008 PDFp2/printedp353, Methods2.1','enumerated members; exhaustiveness unspecified'),
25:('Congers; species not enumerated.','TableA B30; Tam2008 p353','generic group definition'),
26:('Medium demersal fishes; explicit examples Paralabrax humeralis, Hemanthias peruanus, Mugil cephalus. No numerical size limit documented.','Tam2008 PDFp2/printedp353, Methods2.1','representative examples'),
27:('Medium sciaenids; species and numerical size bounds not documented in inspected methods.','TableA B32; Tam2008 p353','generic group definition'),
28:('Prionotus stephanophrys.','Tam2008 PDFp2/printedp353, Methods2.1','single species'),
29:('Galeichtys peruvianus; historical source spelling retained.','Tam2008 PDFp2–3/printedp353–354, Methods2.1','single species'),
30:('Chondrichthyans; species not enumerated. Benthic elasmobranchs are modeled separately.','TableA B35; Tam2008 p354','generic group definition'),
31:('Phalacrocorax bougainvillii, Sula variegata, Pelecanus thagus; historical source names.','Tam2008 PDFp3/printedp354, Methods2.1','enumerated members; exhaustiveness unspecified'),
32:('Otaria flavescens, Arctocephalus australis; source names.','Tam2008 PDFp3/printedp354, Methods2.1','enumerated members; exhaustiveness unspecified'),
33:('Cetaceans; species not enumerated in inspected source methods.','TableA B38; Tam2008 p354','generic group definition'),
34:('Chelonia mydas; green turtles. Source biomass calculation used mean curved carapace length 58.7 cm.','focal PDFp3/printedp30, Methods','single species; mean is not stage boundary'),
35:('Dermochelys coriacea; leatherback turtles. Source biomass calculation used mean curved carapace length 139.6 cm.','focal PDFp3/printedp30, Methods','single species; mean is not stage boundary'),
36:('Engraulis ringens eggs. Listed among living groups in prose but nonfeeding pool in source tables; receives 25% of anchovy production-fate flow in TableC.','focal PDFp3/printedp30; TableC C13','egg stage; pool representation conflict'),
37:('Fishery offal; detrital pool receiving fishery discard fate.','TableA B42; TableC D43:D44','detrital pool'),
38:('Pelagic detritus; detrital pool.','TableA B43; TableC','detrital pool'),
39:('Benthic detritus; detrital pool, residual export1 in TableC.','TableA B44; TableC G42','detrital pool')}
fleets=['Artisanal','Commercial']
groups=[];landings={};discards={};diet={};fates={};groupmap=[]
for n in range(1,40):
    r=n+5; sh='Table A-resolved parameters'
    name=val(sh,r,2,'group_name',n)
    g={'n':n,'name':name,'biomass':val(sh,r,3,'biomass',n),'pb':val(sh,r,4,'pb',n),'qb':val(sh,r,5,'qb',n),'pq':val(sh,r,6,'pq',n),'ae':val(sh,r,7,'ae',n),'ee':val(sh,r,8,'ee',n),'hab_area':None,'z':None,'other_mort':None,'detritus_import':None,'ba':None,'ba_rate':None,'tl':None,'unassim':None,'taxon_descr':taxonomy[n][0]}
    if g['ae'] is not None:
        g['unassim']=str(Decimal(1)-Decimal(str(g['ae'])))
        ledger.append({'group_id':n,'field':'unassim','source_file':'../../../papers/HUM-2018/Supplementary material revised and final.xls','source_sha256':raw['source_sha256'],'sheet':sh,'cell':f'G{r}','native_value':g['ae'],'adopted_value':g['unassim'],'transformation':'GS = 1 - AE; exact decimal complement','missingness':'source_derived'})
    groups.append(g)
    landings[str(n)]={f:str(val(sh,r,c,'landings_'+f,n)) for f,c in zip(fleets,[9,10])}
    discards[str(n)]={f:str(val(sh,r,c,'discards_'+f,n)) for f,c in zip(fleets,[11,12])}
    # Full native zeros retained, including nonfeeding columns.
    diet[str(n)]={str(p):str(val('Table B-resolved diet',p+3,n+1,'diet',n,n,p)) for p in range(1,40)}
    diet[str(n)]['import']=str(val('Table B-resolved diet',43,n+1,'diet_import',n,n,None))
    fates[str(n)]={name:str(val('Table C-resolved detritus fate',n+3,c,'detritus_fate_'+name,n)) for c,name in enumerate(['Anchovy eggs','Fishery offal','Pelagic detritus','Benthic detritus','Export'],3)}
    groupmap.append({'seq':n,'group_name':name,'source_node_type':'primary_producer' if n<3 else 'consumer' if n<=35 else 'eggs_nonfeeding_pool' if n==36 else 'detritus','calculator_pp':'1' if n<3 else '0' if n<=35 else '2','source_row':r,'taxon_descr':taxonomy[n][0],'taxonomy_evidence':taxonomy[n][1],'membership_scope':taxonomy[n][2]})
model={'metadata':{'LME':'13 Humboldt Current','model_number':'HUM2018_resolved_native','model_name':'Northern Humboldt Current','model_year':'1995-1998','publication_year':2018,'doi':'10.1016/j.pocean.2018.04.009','area_km2':165000,'variant':'fresh_native_supplement_uncorrected','source_sha256':raw['source_sha256']},'groups':groups,'consumers':list(range(3,36)),'fleets':fleets,'landings':landings,'discards':discards,'detritus_groups':['Anchovy eggs','Fishery offal','Pelagic detritus','Benthic detritus'],'detritus_fate':fates,'diet':diet,'diet_rows':39,'landings_rows':39,'discards_rows':39,'source_structure':{'source_nodes':41,'living_as_stated':36,'fisheries_nodes':[40,41],'detritus_as_stated':[37,38,39],'nonfeeding_egg_pool':36,'calculator_stock_nodes':39,'operational_detritus_ids':[36,37,38,39]},'source_conflicts':['Sardine landings native supplement5.6513425 versus paper methods1.4','Chrysaora native diet total1.045','Egg pool prose living vs table nonfeeding','Aggregation group codes for eggs/offal/pelagic inconsistent across TableE/printedTable1']}
jwrite(N/'extraction.json',model)
jwrite(N/'GROUP_IDENTITY.json',groupmap)
jwrite(N/'SOURCE_CELLS.json',ledger)
with (N/'taxonomy.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,lineterminator='\r\n');w.writerow(['seq','group_name','taxon_descr']);w.writerows((g['n'],g['name'],g['taxon_descr']) for g in groups)
with (N/'GROUP_CATCH_BIOMASS.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,lineterminator='\r\n');w.writerow(['seq','group_name','biomass_t_km2','landings_artisanal_t_km2_y','landings_commercial_t_km2_y','landings_total_t_km2_y','discards_artisanal_t_km2_y','discards_commercial_t_km2_y','discards_total_t_km2_y','catch_total_t_km2_y','status','source']);
    for g in groups:
        n=str(g['n']); ls=[Decimal(landings[n][f]) for f in fleets];ds=[Decimal(discards[n][f]) for f in fleets]
        w.writerow([g['n'],g['name'],g['biomass'],*ls,sum(ls),*ds,sum(ds),sum(ls+ds),'all stored numeric; zeros explicit',f'Table A C{g["n"]+5}:L{g["n"]+5}'])
fleet_fate={str(n):{name:val('Table C-resolved detritus fate',n+3,c) for c,name in enumerate(['Anchovy eggs','Fishery offal','Pelagic detritus','Benthic detritus','Export'],3)} for n in [40,41]}
jwrite(N/'FLEET_DETRITUS_FATE.json',{'source_fleet_nodes':{'40':'Artisanal fisheries','41':'Commercial fisheries'},'fate':fleet_fate,'basis':'discard fate, not all landings','source':'Table C rows43–44','not_encoded_as_biological_stocks':True})
# Reuse official EwE table builders, but preserve authentic native name whitespace.
spec=importlib.util.spec_from_file_location('source_writer',Path.cwd()/'tools/skills/original_skill_resources/claude/ecopath-extraction/scripts/write_outputs.py')
wr=importlib.util.module_from_spec(spec);spec.loader.exec_module(wr)
wr.cell=lambda v:'' if v is None else str(v)
tables={'Basic_input.csv':wr.basic_input(model),'Diet_composition.csv':wr.diet_composition(model),'Landings.csv':wr.catch_table(model,'landings'),'Discards.csv':wr.catch_table(model,'discards'),'Detritus_fate.csv':wr.detritus_fate(model),'Biomass_accumulation.csv':wr.biomass_accumulation(model)}
for name,rows in tables.items():
    with (N/name).open('w',encoding='utf-8',newline='') as f:csv.writer(f,lineterminator='\r\n',quoting=csv.QUOTE_MINIMAL).writerows(rows)
canonical=[]
unknown='-9999'
for g in groups:
    n=g['n']; ns=str(n)
    def s(v):return unknown if v is None else str(v)
    entries=[{'prey_seq':str(p),'proportion':diet[ns][str(p)],'detritus_fate':fates[ns].get(groups[p-1]['name'],'0')} for p in range(1,40)]
    entry={'group_name':g['name'],'group_seq':ns,'habitat_area':unknown,'biomass_habitat_area':s(g['biomass']),'b_hab_area_input':'true','biomass':s(g['biomass']),'vbk':unknown,'pb':s(g['pb']),'pb_input':'false' if g['pb'] is None else 'true','ee':s(g['ee']),'ee_input':'true','biomass_accum':unknown,'biomass_accum_rate':unknown,'qb':s(g['qb']),'qb_input':'false' if g['qb'] is None else 'true','pp':groupmap[n-1]['calculator_pp'],'detritus_import':unknown,'respiration':unknown,'immigration':unknown,'emigration':unknown,'emigration_rate':unknown,'other_mort':unknown,'export':str(sum(Decimal(landings[ns][f])+Decimal(discards[ns][f]) for f in fleets)),'gs':s(g['unassim']),'shadow_price':unknown,'ge':s(g['pq']),'ge_input':'false' if g['pq'] is None else 'true','diet_imp':diet[ns]['import'],'diet_descr':{'diet':entries},'taxon_descr':g['taxon_descr'],'pedigree_assignment_descr':None}
    canonical.append(entry)
jwrite(N/'model.json',{'metadata':model['metadata'],'source_structure':model['source_structure'],'group':canonical})
runtime=copy.deepcopy(canonical); transforms=[]
for g in runtime:
    n=int(g['group_seq'])
    for field,v,reason in [('habitat_area','1','Whole source model-area density; no separate habitat fraction reported; explicit reconstruction convention'),('biomass_accum','0','Paper explicitly describes steady-state baseline; computational convention; source CSV remains blank'),('biomass_accum_rate','0','Same steady-state computational convention'),('immigration','0','Source silent; explicit zero-migration computational convention'),('emigration','0','Source silent; explicit zero-migration computational convention'),('emigration_rate','0','Source silent; explicit zero-migration computational convention'),('detritus_import','0','No external detritus import reported; explicit computational zero-import convention')]:
        old=g[field];g[field]=v;transforms.append({'group_id':n,'field':field,'source_value':old,'computational_value':v,'reason':reason})
    if n<=2 or n>=36:
        old=g['gs'];g['gs']='0';transforms.append({'group_id':n,'field':'gs','source_value':old,'computational_value':'0','reason':'Nonfeeding basal/pool structural field, unused as biological assimilation estimate'})
    if n==36:transforms.append({'group_id':n,'field':'pp','source_value':'source calls eggs living; source PB/QB absent and TableC routes eggs as pool','computational_value':'2','reason':'Explicit operational nonfeeding egg-pool representation; no invented PB'})
compmeta=dict(model['metadata'],variant='native_supplement_explicit_defaults',source_canonical_sha256=sha(N/'model.json'))
jwrite(C/'model.json',{'metadata':compmeta,'group':runtime})
jwrite(C/'TRANSFORMATION_LEDGER.json',{'source_file':'../resolved_native/model.json','source_sha256':sha(N/'model.json'),'computational_file':'model.json','computational_sha256':sha(C/'model.json'),'normalized':False,'transforms':transforms,'unsupported_native_features':['fleet node discard returns are retained in companion but not added to this computational input','ECOTRAN nutrient pools excluded from Ecopath stock representation']})
native_sums=[]
for n in range(1,40):
    total=sum(Decimal(v) for v in diet[str(n)].values())
    native_sums.append({'consumer_id':n,'consumer_name':groups[n-1]['name'],'prey_sum':str(total-Decimal(diet[str(n)]['import'])),'import':diet[str(n)]['import'],'sum':str(total),'difference_from_one':str(total-1),'feeding':3<=n<=35,'normalization_applied':False})
jwrite(N/'DIET_SOURCE_SUMS.json',{'source_table_sha256':sha(N/'Diet_composition.csv'),'consumers':native_sums})
aggregate={n:S[n] for n in ['Table E-trophic aggregations','Table F-aggregated diet','Table G-aggregate detritus fate','Table H-agg. production matrix','Table I-aggregated pedigree']}
jwrite(ROOT/'aggregated_alternative_source.json',aggregate)
worksheet_rows={'TL':[[None,None,'TL']]+[[g['n'],g['name'],None] for g in groups], 'Metadata':[[k,model['metadata'][k]] for k in ['LME','model_number','model_name','model_year']], 'Taxonomy':[['seq','group_name','taxon_descr']]+[[g['n'],g['name'],g['taxon_descr']] for g in groups]}
recon={'Groups':[['group_seq','group_name','biomass','pb','qb','ee','ge','gs','pp','diet_imp','export','habitat_area','biomass_accum','biomass_accum_rate']]+[[int(g['group_seq']),g['group_name']]+[None if g[k]==unknown else float(g[k]) for k in ['biomass','pb','qb','ee','ge','gs','pp','diet_imp','export','habitat_area','biomass_accum','biomass_accum_rate']] for g in canonical], 'Diet':[['prey_seq','prey_name']]+[], 'Catch':tables['Landings.csv'],'Discards':tables['Discards.csv'],'Fate':tables['Detritus_fate.csv']}
recon['Diet']=tables['Diet_composition.csv']
jwrite(ROOT/'workbook_payload.json',{'artifacts':worksheet_rows,'reconstruction':recon,'native_sheets':{n:S[n] for n in ['Table A-resolved parameters','Table B-resolved diet','Table C-resolved detritus fate']}})
print('SOURCE:',N/'model.json'); print('COMPUTATIONAL:',C/'model.json');print('Raw diet deviation group7',native_sums[6]['sum']);print('Known biology complete groups1–35; eggs operational pool, source conflict retained.')
