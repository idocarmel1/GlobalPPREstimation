"""Source-priority taxon decisions and reproducible, fixed catch-composition weights."""
from pathlib import Path
import sys,json,csv,math
from collections import defaultdict
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import set_setting
REG=ROOT/'regions/LME_038'; path=REG/'LME_038.xlsx'; b=read_book(path);mid=overview(b)['selected_model_id']; dest=REG/'models'/mid;ev=dest/'evidence'
gs={int(r['seq']):r for r in records(b,'Selected model groups','Groups')};inv=json.loads((ev/'catch_taxa_inventory.json').read_text(encoding='utf8'));taxa={r['taxon']:r for r in inv}
dec={}
def assign(names,ids,basis='direct',note=None,confidence=None):
 for t in names.split(';'):
  if t not in taxa:raise ValueError(t)
  assert t not in dec,t
  dec[t]={'ids':ids,'basis':basis,'confidence':confidence or ('high' if basis=='direct' else 'medium'),'explanation':note or 'Table3.1 PDF58-59 printed49-50: explicit named membership or contained genus/family; dedicated group and named exceptions take precedence.'}
assign('Decapterus;Decapterus russelli',[18])
assign('Rastrelliger;Rastrelliger brachysoma;Rastrelliger kanagurta',[19])
assign('Sardinella;Sardinella lemuru;Stolephorus;Engraulidae;Clupeidae;Pellona ditchela;Hilsa kelee;Anodontostoma chacunda;Tenualosa toli',[20])
assign('Dussumieria acuta',[20],note='Clupeoid in historical Clupeidae classification used by source; FAO identification sheet explicitly places Dussumieria acuta in Clupeidae: https://www.fao.org/4/e9163e/e9163e1l.pdf . Modern Dussumieriidae is not a biological reassignment.')
assign('Leiognathus;Leiognathidae',[15])
assign('Lutjanus;Lutjanus argentimaculatus;Lethrinidae;Lethrinus;Polynemidae;Sphyraena;Sphyraena barracuda;Sphyraenidae;Balistidae;Sparidae;Tetraodontidae',[8])
assign('Scolopsis',[21],note='Source Small demersals explicitly includes Nemipteridae. FAO1990 catalogue places Scolopsis in Nemipteridae: https://www.fao.org/4/t0416e/t0416e00.htm ; no verified source-specific exception identifies this genus with SAF Pentapodidae.',confidence='medium')
assign('Nemipterus;Nemipterus hexodon;Nemipteridae;Caesionidae;Caesio;Pampus argenteus;Siganus;Siganidae;Synodontidae;Stromateidae;Priacanthus;Saurida;Sillago;Cynoglossus;Gerres;Pennahia;Drepane;Mullidae;Upeneus',[21])
assign('Cephalopholis boenak',[21],note='Serranidae explicitly included in small demersals; local catch class Small reef-associated fish selects the small source size group.',confidence='medium')
assign('Mugilidae;Rachycentron canadum;Psettodes erumei',[22])
assign('Hemiramphus;Hemiramphidae;Auxis;Auxis thazard;Auxis rochei;Lactarius lactarius',[14])
assign('Selaroides leptolepis;Parastromateus niger;Megalaspis cordyla;Selar crumenophthalmus;Scomberoides;Alepes;Elagatis bipinnulata;Seriola',[14],note='Source Misc. pelagics includes pelagic Carangidae; genus is not the dedicated Decapterus group. Local catch pelagic class supports this member placement.',confidence='medium')
assign('Caranx;Seriolina nigrofasciata',[8],note='Source SAF explicitly includes demersal Carangidae; local catch reef-associated class supports SAF rather than Misc. pelagics.',confidence='medium')
assign('Scomberomorus commerson;Scomberomorus guttatus;Scomberomorus;Katsuwonus pelamis;Trichiuridae;Trichiurus;Trichiurus lepturus;Chirocentrus;Chirocentrus dorab;Euthynnus affinis;Thunnus albacares;Thunnus obesus;Thunnus tonggol;Thunnus alalunga;Thunnus orientalis;Thunnus;Acanthocybium solandri;Sarda orientalis',[12,25],'model_catch','Source Chirocentridae/large Scombridae/Trichiuridae split into juveniles/adults. Catch has no stage; fixed source Harvest shares .116/.051 estimate fishery stage composition, not measured regional ages.')
assign('Carcharhinidae;Carcharhinus;Carcharhinus falciformis;Carcharhinus longimanus;Carcharhinus amblyrhynchos;Prionace glauca;Sphyrna;Sphyrnidae;Sphyrna lewini;Sphyrna zygaena;Muraenesox;Muraenesox cinereus',[23,26],'model_catch','Explicit Table3.1 large demersal predator membership takes precedence over modern habitat label. Juvenile/adult split uses source Harvest .066/.020; ages in regional catch are unknown.')
assign('Netuma thalassina',[23,26],'model_catch','Arius thalassinus is accepted as Netuma thalassina (WoRMS https://marinespecies.org/traits/aphia.php?p=taxlist&pid=154659&rComp=%3E%3D&tRank=220). Named source exception overrides generic Ariidae small demersals. Stage shares use source Harvest .066/.020.')
assign('Dasyatidae',[24])
assign('Penaeus indicus;Penaeus;Metapenaeus;Penaeidae;Dendrobranchiata;Penaeus merguiensis;Penaeus semisulcatus;Penaeus latisulcatus;Penaeus monodon',[11,13],'model_catch','Source groups include all juvenile/adult shrimps; catch is not staged. Fixed source Harvest .008/.014 estimates juvenile/adult shares; no invented age observation.')
assign('Acetes japonicus;Acetes;Sergestidae',[4],note='Source Table3.1 explicitly includes sergestids in large herbivorous zooplankton. This specific membership overrides all-shrimp broad wording in juvenile/adult penaeid groups. Group4 has reported harvest .008; not an invented basal assignment.',confidence='medium')
assign('Portunus pelagicus;Scylla serrata;Panulirus longipes;Panulirus;Thenus orientalis',[16])
assign('Teuthida;Loliginidae;Sepia;Sepiidae;Sepioteuthis lessoniana;Octopodidae',[17])
assign('Tegillarca granosa;Veneridae;Bivalvia;Crassostrea;Modiolus;Perna viridis;Echinodermata',[9],note='Source macrozoobenthos explicitly includes commercially sized cockles, clams, oysters, mussels and echinoderms (>1mm); not larvae/infauna. Tegillarca granosa synonym Anadara (Tegillarca) granosa confirmed by WoRMS https://www.marinespecies.org/aphia.php?p=taxlist&tName=Tegillarca .')
assign('Rhizostomeae;Scyphozoa;Cephea',[6])
assign('Marine fishes not identified',[21,22],'catch_composition','SAU Medium demersals class and source adjacent small/medium demersal guilds constrain the unidentified pool. Fixed1950-2019 identified-catch shares; excludes pelagics, reef-specialist SAF, mammals, basal groups and named large sharks. Proxy does not demonstrate species identities or full spatial representativeness.',confidence='low')
assign('Decapoda',[16],'functional_group','SAU Lobsters, crabs class narrows coarse Decapoda to source Crabs + Lobsters; no larval/plankton or shrimp assignment.')
assign('Miscellaneous marine crustaceans',[11,13],'model_catch','SAU Shrimps class narrows residual crustaceans to source juvenile/adult shrimp pools. Model Harvest .008/.014 gives stage shares; unresolved species identity remains explicit.',confidence='low')
assign('Mollusca',[9],'functional_group','SAU Other demersal invertebrates class and source commercial mollusc size identify macrozoobenthos; separately identified cephalopods are mapped to group17.')
assign('Sciaenidae',[14,21],'catch_composition','Source places Kathala axillaris in Misc. pelagics, other Sciaenidae in Small demersals. Coarse family spans both; fixed identified-catch composition estimates shares, not observed family species proportions.',confidence='low')
assign('Carangidae',[8,14,18],'catch_composition','Family contains source demersal SAF, pelagic Misc. pelagics and dedicated Decapterus. Fixed identified catch across candidates is a proxy, not measured carangid species composition.')
assign('Scombridae',[12,14,19,25],'catch_composition','Source explicitly separates Auxis, Rastrelliger and juvenile/adult large Scombridae. Composite weights from identified local catch; no family-wide generic reassignment.')
assign('Clupeiformes',[12,20,25],'catch_composition','Includes source clupeoids and Chirocentridae juvenile/adult large pelagics. Composite weights use identified local catch.')
assign('Perciformes',[21,22],'catch_composition','Broad legacy order contains both source Small and Medium demersal families. SAU Medium demersals class constrains the coarse pool to these adjacent size guilds; no pelagic, shark or reef-specialist group is inferred.',confidence='low')
assign('Pleuronectiformes',[21,22],'catch_composition','Source Cynoglossidae in Small demersals and Psettodidae in Medium demersals provide the two represented flatfish homes; fixed identified-catch weights are an uncertain proxy.',confidence='low')
assign('Lutjanidae;Pristipomoides',[8,22],'catch_composition','Source named Pristipomoides typus exception in Medium demersals, other Lutjanidae in SAF. Coarse genus/family spans both; proxy weights from identified local catch.',confidence='low')
assign('Ariidae',[21,23,26],'catch_composition','Source Arius thalassinus (=Netuma thalassina) exception in large demersal J/A, other Ariidae small demersals. Composite retains all source placements.')
assign('Serranidae;Epinephelus',[21,22,23,26],'catch_composition','Small/medium source Serranidae and named Epinephelus lanceolatus large J/A exception; no catch sizes/species proportions available, proxy composition retained.',confidence='low')
assign('Pomadasys argenteus',[21,22],'model_catch','Source Haemulidae appears in both Small and Medium demersals. Catch lacks source-specific size split, source group Harvest .066/.015 used as proxy.',confidence='low')
assign('Batoidea',[23,24,26],'catch_composition','Source Dasyatidae/Myliobatidae in Demersal rays and Pristidae/Rhinidae/Rhinobatidae large J/A. Coarse source-containing composite; no ray family proportions.',confidence='low')
assign('Elasmobranchii;Chondrichthyes',[14,23,24,26],'catch_composition','Coarse cartilaginous fishes include source Mobulidae miscellaneous pelagics, demersal rays and large J/A sharks/rays. Source domain does not explicitly represent every possible oceanic family; proxy marked low.',confidence='low')
assign('Marine pelagic fishes not identified',[12,14,18,19,20,25],'catch_composition','SAU pelagic class and source pelagic fish groups constrain pool; fixed identified-catch shares, no demersal or basal groups.',confidence='low')
# Do not create ecological homes for unlisted families or open-ocean billfish.
for t in taxa:
 if t not in dec:dec[t]={'ids':[],'basis':'unresolved','confidence':'unresolved','explanation':'No defensible explicit source member placement established in Table3.1; source Java Sea shelf coverage is incomplete for the full LME. Retained missing, not assigned by trophic level or target coverage.'}
def source_weights(ids):
 v=[gs[i]['catch'] for i in ids];assert math.fsum(v)>0;return [x/math.fsum(v) for x in v]
# First resolve single and source-harvest stage/size mappings. No circular coarse weights.
for t,d in dec.items():
 ids=d['ids']
 if not ids:d['weights']=[]
 elif len(ids)==1:d['weights']=[1.]
 elif d['basis']=='model_catch':d['weights']=source_weights(ids)
composition=defaultdict(float)
for t,d in dec.items():
 if 'weights' in d and not taxa[t]['unidentified']:
  for i,w in zip(d['ids'],d['weights']):composition[i]+=taxa[t]['all_years_tonnes']*w
for t,d in dec.items():
 if 'weights' not in d:
  v=[composition[i] for i in d['ids']]
  if sum(v)>0:d['weights']=[x/math.fsum(v) for x in v];d['weight_basis']='identified total catch1950-2019, stage mappings first; no coarse-pool recursion'
  else:d['weights']=source_weights(d['ids']);d['weight_basis']='source model Harvest fallback; identified candidate catch empty'
 else:d['weight_basis']=d['basis']
rows=[]
for t in sorted(taxa):
 d=dec[t];assert not d['ids'] or math.isclose(sum(d['weights']),1,abs_tol=1e-12)
 for i,w in zip(d['ids'],d['weights']):
  assert i not in [1,2,3,5,7,10,27,28,29]
  rows.append([mid,t,gs[i]['group_name'],w,d['confidence'],'Buchary1999 Table3.1 PDF58-59; '+d['basis'],d['explanation']+' Weight basis: '+d['weight_basis']+'.'])
 if not d['ids']:rows.append([mid,t,None,None,'unresolved','source_scope_gap',d['explanation']])
b['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],rows)
set_setting(b,'production_eligible',True)
set_setting(b,'mapping_limitation','Fixed source-Harvest stage weights and1950-2019 identified-catch coarse shares; unresolved source-scope taxa remain missing. Full-LME use extrapolates subregional mid1970s model; TE WARN retained.')
write_book(path,b)
with (ev/'CATCH_MAPPING.csv').open('w',encoding='utf8',newline='') as f:w=csv.writer(f);w.writerow(b['PPR']['Matching'][0]);w.writerows(rows)
(ev/'MAPPING_DECISIONS.json').write_text(json.dumps({'model_id':mid,'source':'source candidate evidence/taxonomy_evidence.csv','fixed_composition_tonnes_by_seq':dict(composition),'taxa':dec},indent=2,ensure_ascii=False),encoding='utf8')
coverage={}
for basis in ['landings','catch','discards']:
 rr=[r for r in records(b,'Catch','Catch') if r['catch_basis']==basis]
 coverage[basis]={}
 for year in [1950,2019]:
  total=math.fsum(r[year] for r in rr if finite(r[year]));covered=math.fsum(r[year] for r in rr if finite(r[year]) and dec[r['taxon']]['ids']);coverage[basis][year]={'total_tonnes':total,'mapped_tonnes':covered,'coverage_fraction':covered/total if total else None}
unresolved=[taxa[t] for t,d in dec.items() if not d['ids']]
out={'taxa':len(taxa),'resolved':len(taxa)-len(unresolved),'unresolved':len(unresolved),'coverage':coverage,'unresolved_by_2019_catch':sorted(unresolved,key=lambda r:r['tonnes2019'],reverse=True),'weight_checks':'all resolved weights sum1; exact group ids; all181 catch taxa represented; no basal/Import/mammal mapping','caveat':'Mapped does not mean certain; coarse and stage allocations are explicit proxies. Source Java Sea model extrapolated over Indonesian Sea LME and1950-2019, not spatially representative validation.'}
(ev/'MAPPING_COVERAGE.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
