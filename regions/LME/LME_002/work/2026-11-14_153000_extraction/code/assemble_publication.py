"""Merge independently extracted publication evidence without completing unknown diets."""
from pathlib import Path
from decimal import Decimal
import json,re,sys

RUN=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def norm(s):return re.sub(r'[^a-z0-9]','',s.casefold())

d=read(RUN/'outputs/numeric_writer_input.json')
g=d['groups']; byname={norm(x['name']):x['n'] for x in g}; byid={x['n']:x for x in g}
aliases={}
def alias(target,labels):
    ident=byname[norm(target)]
    for s in labels.split(';'):aliases[norm(s)]=[ident]
alias('Sperm and beaked whale','Sperm and beaked whales')
alias('Gray Whales','Gray whales;Grey whale')
alias('Humpbacks','Humpback whales')
alias('West S.S.L._Juv','West S.S.L_Juv')
alias('W. Pollock_Juv','W. pollock juv')
alias('P. Cod_Juv','P. cod juv')
alias('Herring_Juv','Herring juv')
alias('Arrowtooth','Arrowtooth fl.;Arrowtooth flounder')
alias('Arrowtooth_Juv','Arrowtooth juv')
alias('P. Halibut','Halibut')
alias('P. Halibut_Juv','Halibut juv;P. halibut juv')
alias('YF. Sole','Yellowfin sole')
alias('FH. Sole','Flathead sole')
alias('FH. Sole_Juv','Flathead sole juv;Flathead sold juv')
alias('N. Rock sole','N rock sole')
alias('S. Rock sole','S rock sole')
alias('AK Plaice','Alaska plaice')
alias('Sablefish_Juv','Sablefish juv')
alias('Longnosed skate','Longnose skate')
alias('Other Macruids','Other Macrourids')
alias('Misc. fish deep','Misc. deep fish')
alias('POP','Pacific ocean perch;Pacific o. perch')
alias('POP_Juv','Pacific o. perch juv')
alias('Sharpchin Rock','Sharpchin rockfish;Sharpchin rf.')
alias('Northern Rock','Northern rockfish')
alias('Dusky Rock','Dusky rockfish')
alias('Shortraker Rock','Shortraker rockfish;Shortraker rf.')
alias('Rougheye Rock','Rougheye rockfish;Rougheye rf.')
alias('Shortspine Thorns','Shortspine thornyhead;Sh. thornyhead')
alias('Shortspine Thorns_Juv','Sh. thornyhead juv')
alias('Atka mackerel_Juv','Atka mack juv;Atka mack. juv')
alias('Lg. Sculpins','Large sculpins')
alias('Misc. fish shallow','Misc. shallow fish;Misc shallow fish')
alias('Octopi','Octopus')
alias('Squids','Squid')
alias('Oth. managed forage','Managed forage')
alias('Oth. pelagic smelt','Other pelagic smelt;Oth pel. smelt')
alias('Bairdi','Tanner crab;Tanner crabs')
alias('King Crab','King crabs')
alias('Pandalidae','Pandalid shrimp;Pandalids')
alias('NP shrimp','Non-Pandalid shrimp;Non-Pand. shrimp;Non-pand. sh.')
alias('Sea stars','Sea star')
alias('Brittle stars','Brittle star')
alias('Urchins dollars cucumber','Urchins dollars and cucumbers')
alias('Hermit crabs','Hermit crab')
alias('Misc. crabs','Misc. crab')
alias('Hydroids','Benth. Hydroid;Benthic Hydroid')
alias('Urochordata','Benth. Urochordata;Benthic Urochordata')
alias('Sponges','Sponge')
alias('Polychaetes','Polychaete')
alias('Misc. worms','Misc. worm etc.;Misc. worms etc.;Misc. Worm. Etc.')
alias('Gelatinous filter feeders','Pel. gel. filter feeder')
alias('Pelagic Amphipods','Pel. amphipods')
alias('Mysids','Mysid')
alias('Sleeper shark','Sleeper sharks')
alias('Murres','Murre')
alias('Kittiwakes','Kittiwake')
alias('Auklets','Auklet')
alias('Puffins','Puffin')
alias('Fulmars','Fulmar')
alias('Storm Petrels','Storm Petrel')
aliases[norm('Steller sea lion')]=[byname[norm('West S.S.L.')],byname[norm('Central S.S.L.')]]
aliases[norm('Steller sea lion juv')]=[byname[norm('West S.S.L._Juv')],byname[norm('Central S.S.L._Juv')]]
absent={norm(x) for x in ['Belugas','Bowhead whales','Kamchatka','Kamchatka juv','Gr. turbot','Gr. turbot juv','Yellowfin so. juv','Snow crab','Whiteblotched skate absent']}
def resolve(label):
    k=norm(label.rstrip('*+').strip())
    if k in aliases:return aliases[k]
    if k in byname:return [byname[k]]
    if k in absent:return []
    raise KeyError('Unresolved source group '+label)

pref=read(RUN/'qa/preference_diets.json')['records']
predmap={
 'West S.S.L. / West S.S.L._Juv':['West S.S.L.','West S.S.L._Juv'],
 'Central S.S.L. / Central S.S.L._Juv':['Central S.S.L.','Central S.S.L._Juv'],
 'N. Fur Seal / N. Fur Seal_Juv':['N. Fur Seal','N. Fur Seal_Juv'],
 'Other skates':['Whiteblotched skate','Mud skate'],
}
unknowns={}; additions={}; resolved=[]
for i,r in enumerate(pref,1):
    for predator in predmap.get(r['predator'],[r['predator']]):
        pid=resolve(predator)[0]; juvenile='juv' in predator.casefold()
        members=[]; excluded=[]; absent_labels=[]
        for label in r['prey']:
            if (label.endswith('*') and not juvenile) or (label.endswith('+') and juvenile):
                excluded.append(label);continue
            ids=resolve(label)
            if not ids:absent_labels.append(label)
            members.extend(ids)
        members=list(dict.fromkeys(members))
        # Never use published final group B as a guessed substitute for the unavailable
        # stratum-specific abundance/area denominators used by author preference rules.
        # A published pool reduced to exactly one eligible prey by explicit
        # stage exclusions needs no availability denominator. Its full stated
        # percentage belongs to that prey; retain the original P flag in evidence.
        uncertain=len(members)!=1
        resolved.append([str(i),r['table'],','.join(map(str,r['pdf_pages'])),str(pid),byid[pid]['name'],r['percent_literal'],str(r['preference']),';'.join(r['prey']),';'.join(map(str,members)),';'.join(excluded),';'.join(absent_labels),'allocation_unresolved' if uncertain else 'direct_percentage'])
        if uncertain:unknowns.setdefault(pid,set()).update(members)
        elif members:
            additions.setdefault(pid,{})[members[0]]=additions.setdefault(pid,{}).get(members[0],Decimal(0))+Decimal(r['percent_literal'])/100

for pid in {resolve(x)[0] for r in pref for x in predmap.get(r['predator'],[r['predator']])}:
    cells=d['diet'].setdefault(str(pid),{})
    cells.setdefault('import',None)
    for prey,value in additions.get(pid,{}).items():
        if prey not in unknowns.get(pid,set()):cells[str(prey)]=str(value)
    for prey in unknowns.get(pid,set()):cells[str(prey)]=None

# Source's explicit annual biomass changes, not balancing residuals.
for name,value in [('W. Pollock','-1.35'),('Herring','-0.11'),('Greenlings','-0.002')]:
    byid[resolve(name)[0]]['ba']=value
gs40={'Anemones','Corals','Hydroids','Urochordata','Sea Pens','Sponges','Bivalves','Polychaetes','Misc. worms'}
for x in g:
    if x['n'] in d['consumers']:x['unassim']='0.4' if x['name'] in gs40 else '0.2'
for name in ['Euphausiids','Pelagic microbes','Benthic microbes']:
    byid[byname[norm(name)]]['pq']='0.35'
# Explicit Appendix A statement for this composite; the remaining forage-fish
# allocation is undocumented and remains outside the concrete diet cells.
d['diet'].setdefault(str(byname[norm('Albatross Jaeger')]),{}).update({str(byname[norm('Squids')]):'0.5','import':None})

# Published group-range detritus partition, Table B1 GOA column (PDF213).
# The source starts the second range with juvenile pollock; adult pollock is not filled.
for x in g:
    n=x['n']; benthic=None
    if 1<=n<=31 or 33<=n<=92 or 125<=n<=127:benthic='0.5'
    elif 93<=n<=113 or n==124:benthic='0.9'
    elif 114<=n<=123:benthic='0.3'
    if benthic is not None:
        d['detritus_fate'][str(n)]={'Benthic Detritus':benthic,'Pelagic Detritus':str(1-Decimal(benthic))}
d['metadata']['ba_basis']='whole_model_area'
d['metadata']['model_number']='Aydin2007'

header=['record','table','pdf_pages','predator_seq','predator','source_percent','preference_flag','source_prey_labels','eligible_prey_seq','stage_excluded','absent_from_GOA','interpretation']
d['companions']['Published_preference_pools.csv']={'description':'Published pooled diet specifications and stage restrictions; final allocations unresolved, no inferred numerical split. Exact source percentages retained including rounding sums.','rows':[header]+resolved}
missing=[['predator_seq','predator','prey_seq','prey','status','reason']]
for pid,ids in unknowns.items():
    for prey in sorted(ids):missing.append([str(pid),byid[pid]['name'],str(prey),byid[prey]['name'],'unknown','Final preference allocation not published; known direct components may coexist in the source pool companion.'])
d['companions']['Unresolved_diet_cells.csv']={'description':'Explicit unknown mask for final cell values affected by published aggregate preference pools; standard import blanks must not be read as documented zeros.','rows':missing}
d['companions']['Prose_parameters.csv']={'description':'Source-prose values and deliberate gaps; not new numerical assumptions.','rows':[
 ['field','groups','value','units','pdf_pages','printed_pages','provenance'],
 ['biomass_accumulation','W. Pollock','-1.35','t/km2/year','149','139','Explicit annual decline incorporated by authors'],
 ['biomass_accumulation','Herring','-0.11','t/km2/year','153','143','Explicit annual decline incorporated by authors'],
 ['biomass_accumulation','Greenlings','-0.002','t/km2/year','183','173','Explicit survey trend incorporated by authors'],
 ['biomass_accumulation','Other groups','','t/km2/year','28;39','18;29','Not assigned a numeric zero; source only names three observed negative trends'],
 ['unassimilated_consumption','Other consumers','0.2','proportion','200-205','190-195','Source describes default applied to other groups'],
 ['unassimilated_consumption',';'.join(sorted(gs40)),'0.4','proportion','200-205','190-195','Explicit named source exceptions'],
 ['production_consumption','Euphausiids;Pelagic microbes;Benthic microbes','0.35','proportion','See published_prose_scalars companion','See published_prose_scalars companion','Explicit source P/Q assumption; distinct from GS'],
 ['diet','Albatross Jaeger -> Squids','0.5','proportion','146','136','Explicit source half-squid diet; remainder allocated to forage fish by abundance remains unresolved'],
 ['habitat_area','All','','proportion','28','18','No group-specific fraction; B already whole-model-area density'],
 ['detritus_fate','Published Table B1 ranges','See Detritus_fate.csv','proportion','213','203','No inference for adult pollock or unlisted source/detritus groups'],
 ['model_area','GOA','291840','km2','15-16','5-6','Source area for annual catch density conversion'],
 ]}

# The writer defaults an entirely absent predator's imported food to zero.
# Every consumer must explicitly carry unknown import unless the source gives it.
for predator in d['consumers']:
    d['diet'].setdefault(str(predator),{}).setdefault('import',None)

out=RUN/'outputs/publication_writer_input.json'
out.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'groups':len(g),'consumers':len(d['consumers']),'preference_records':len(pref),'resolved_pool_records':len(resolved),'unknown_preference_cells':sum(map(len,unknowns.values())),'known_diet_cells':sum(v is not None for row in d['diet'].values() for k,v in row.items() if k!='import'),'normalization_applied':False,'model_id':'Aydin2007_Gulf_of_Alaska_1990-1994'}
(RUN/'qa/publication_assembly.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
