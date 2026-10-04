"""Keyed review of every catch label; selection remains unchanged."""
from pathlib import Path
import json,csv,math,collections
R=Path(__file__).resolve().parent.parent
ROOT=next(p for p in R.parents if (p/'Project.xlsx').exists())
MODEL='32_1_Arabian_Sea_off_Karnataka_(2000)'
oldpath=ROOT/'regions/LME_032/models'/MODEL/'source_evidence/mapping'/f'{MODEL}.csv'
old=list(csv.DictReader(oldpath.open(encoding='utf-8-sig')))
snap=json.loads((R/'baseline/snapshot.json').read_text(encoding='utf-8'))
taxonomy=json.loads((R/'mapping/taxonomy_lookup.json').read_text(encoding='utf-8'))
members=list(csv.DictReader(next(oldpath.parent.glob('*.members.csv')).open(encoding='utf-8-sig')))
basic=list(csv.DictReader((R/'source/published_balanced_basic.csv').open(encoding='utf-8-sig')))
landings=list(csv.DictReader((R/'source/published_landings.csv').open(encoding='utf-8-sig')))
groupname={int(x['group_id']):x['name'] for x in basic};groupid={v:k for k,v in groupname.items()}
catchproxy={int(x['group_id']):float(x['TOTAL']) for x in landings}
biomassproxy={int(x['group_id']):float(x['biomass']) for x in basic}
catch={x['taxon']:x for x in snap['catch'] if x['catch_basis']=='landings'}
wholecatch={x['taxon']:x for x in snap['catch'] if x['catch_basis']=='catch'}
classic={x['taxon']:x for x in snap['classic']}
stored=collections.defaultdict(list)
for x in snap['matching']:
 if x.get('group'):stored[x['taxon']].append((groupid[x['group']],x['weight']))
def accepted(s):return taxonomy.get(s,{}).get('valid_name',s)
explicit={};generic_genus={}
for x in members:
 s=x['accepted_name'] or x['printed_name']; gid=groupid.get(x['group_name'])
 if gid is None:continue
 if ' sp.' in s:generic_genus[s.split()[0]]=gid
 elif len(s.split())==2 and not s.split()[0].endswith('.'):
  printed=x['printed_name']
  # Expanded initials are spelling expansions; full historical binomials remain visible.
  if printed.split()[0].endswith('.') or len(printed.split()[0])<=2 or printed.startswith('S.comm'):printed=s
  explicit[accepted(s)]=(gid,printed,x['source_page'])
# Source spelling correction verified by the source's Caranx kalla member and WoRMS.
explicit['Alepes djedaba']=(11,'Caranx kalla','printed p.12 / PDF p.22; WoRMS accepted-name relation')
generic_genus.update({'Terapon':10,'Upeneus':10,'Lutjanus':8,'Panulirus':15,'Plotosus':17})
source='Mohamed et al. 2008, Bulletin 51 pp.11–20'
rules={
 'M1':'Explicit source member or member of a source-listed genus',
 'M2':'Accepted-name synonym of an explicit source member',
 'M3':'Complete fit to an explicitly defined generic compartment',
 'M4':'Taxonomic extension from named source representatives',
 'M5':'Supported habitat and feeding-guild extension',
 'M6':'Partial or conflicting habitat and feeding-guild fit',
 'M7':'Broad label interpreted through its recorded fishery classification',
 'M10':'Explicit coarse-category approximation to compatible compartments',
 'M11':'Closest available ecological analogue with a material mismatch',
 'W1':'One supported compartment receives the entire taxon',
 'W4':'Source-model landings proportions assumed for the catch category',
 'W9':'Source-model biomass proportions when eligible model catches are all zero',
 'W5':'Identified regional catch composition assumed for the coarse taxon'}
rank={'High':0,'Medium':1,'Low':2,'Very low':3,'Unresolved':4}
allocations=[];decisions=[];retained_weight_checks=[]
def proxy(t,gids,why):
 values=[catchproxy[g] for g in gids];basis='catch';wr='W4';total=math.fsum(values); rejected=None
 if total<=0:
  rejected={'field':'published landings','values':values,'sum':total,'reason':'No positive catch among independently eligible groups'}
  values=[biomassproxy[g] for g in gids];total=math.fsum(values);basis='biomass';wr='W9'
 assert all(math.isfinite(v) and v>=0 for v in values) and total>0
 pairs=[(g,v/total) for g,v in zip(gids,values)]
 for g,v,w in zip(gids,values,[p[1] for p in pairs]):
  allocations.append({'taxon':t,'group_id':g,'group':groupname[g],'raw_value':v,'field':basis,'unit':'t km−2 yr−1' if basis=='catch' else 't km−2','denominator':total,'weight':w,'confidence':'Medium','source':'Bulletin 51 printed p.13' if basis=='catch' else 'Bulletin 51 printed p.21','eligibility':why,'rejected_catch_attempt':rejected,'assumption':'Whole-compartment composition is a proxy for this taxon; fixed across Arabian Sea catch years and fishery bases. Zero eligible candidates retained.'})
 return pairs,wr,'Medium',f'Allocation uses published model {basis} proportions, assumed constant across regions, years and catch bases; whole-group quantities are a composition proxy.'
coarse={
 'Marine fishes not identified':([4,5,7,8,9,10,11,12,13,14,17],'Unidentified marine fish is approximated as the model’s harvested bony-fish compartments; separate shark/ray categories and non-fish pools are excluded. Its demersal tag alone does not define its composition.'),
 'Perciformes':([4,5,7,8,9,10,11,12,13,14,17],'Legacy perch-like fish reporting is broader than four demersal pools; approximate the model’s harvested bony-fish guilds. Present-day order circumscription is not substituted for the legacy catch label.'),
 'Marine groundfishes not identified':([8,9,10,17],'Groundfish reporting is approximated by the model’s benthic fish pools; diet/size composition is unknown.'),
 'Marine pelagic fishes not identified':([4,5,7,11,12,13,14],'Pelagic residual may include large benthopelagic ribbonfish/carangids; approximate all harvested water-column fish pools.'),
 'Mollusca':([6,18],'Common-name metadata explicitly includes clams, seasnails, squids and octopuses; include Cephalopods and Heterotrophic Benthos. Adult fishery catch is assumed; larval zooplankton is excluded.'),
 'Miscellaneous aquatic invertebrates':([6,15,16,18,19],'Unidentified demersal invertebrates may span molluscs, crustaceans, epifauna and infauna. These adult pools are an explicit coarse approximation; fish-bearing pools and pelagic larvae are excluded.'),
 'Malacostraca':([15,16,17,18,21],'Common metadata includes lobsters, crabs, shrimps and krill. Include harvested decapods, squilla, epifaunal crustaceans and large zooplankton; exclude micro-zooplankton eggs/larvae under an adult-catch assumption.'),
 'Chondrichthyes':([2,3],'Sharks/rays fit two pools, but common metadata also includes chimaeras, absent from the source. Approximate the two elasmobranch pools rather than claim complete containment.'),
 'Anguilliformes':([8,9],'Adult eels and morays are approximated by demersal carnivore pools; eel larvae in Micro Nekton do not represent adult fishery catch. Size, diet and depth mixture remain uncertain.'),
 'Gobiidae':([10,11,17],'Coarse gobies have unknown species/feeding composition; approximate small benthic carnivory, omnivory and water-column feeding with three source pools. Reef and specialised feeding remain unmatched.'),
 'Labridae':([9,10,11],'Wrasses vary in size and include benthic invertebrate feeders and planktivores (FishBase family account). Approximate medium/small benthic feeders plus the small water-column pool; specialised cleaning and reef habitats remain unmatched.'),
 'Scombroidei':([4,5],'Provider common name is tunas, bonitos and billfishes. Source Tunas plus Large Pelagics approximate those taxa; billfishes are ecological extensions, not source members.')}
herb={'Siganidae','Siganus','Siganus canaliculatus','Siganus sutor','Scaridae','Scarus persicus','Bolbometopon muricatum','Scarus ghobban','Acanthuridae','Acanthurus dussumieri','Crenidens crenidens'}
reef={'Pomacanthus maculosus','Pomacanthidae','Ephippidae','Platax','Platax orbicularis','Chaetodontidae','Pomacentridae'}
bill={'Istiophorus platypterus','Istiophoridae','Istiompax indica','Xiphias gladius','Xiphiidae','Kajikia audax','Istiophorus','Makaira','Tetrapturus angustirostris'}
deep={'Bramidae','Brama brama','Berycidae','Beryx','Gempylidae','Ruvettus pretiosus','Lepidocybium flavobrunneum','Lampris guttatus','Gadiformes'}
generic_compartments={'Sharks','Skates & Rays','Shrimps','Crabs & Lobster','Heterotrophic Benthos'}
for oldrow in old:
 t=oldrow['taxon']; previous=stored.get(t,[]); pairs=list(previous); membership='M4';mc='Medium';wr='W1';wc='High';weight_reason='Single-group allocation adds no internal composition assumption.';references=[source,'Regional catch metadata','WoRMS accepted-name and lineage records, retrieved 30 September 2026'];reason=''
 valid=accepted(t); genus=t.split()[0]
 if t in coarse:
  gids,reason=coarse[t];pairs,wr,wc,weight_reason=proxy(t,gids,reason);membership='M10';mc='Very low'
 elif t in {'Decapoda','Miscellaneous marine crustaceans'}:
  gids=[15,16,18];reason='Catch metadata names crabs, lobsters and shrimps. Include both harvested decapod pools and the source’s epifaunal benthic-crab pool; eggs/larvae are excluded under the adult fishery-catch interpretation.';pairs,wr,wc,weight_reason=proxy(t,gids,reason);membership='M7';mc='Medium'
 elif t in herb:
  pairs=[(17,1.)];membership='M11';mc='Very low';reason='Closest available bottom-feeding approximation is Benthic Omnivores. The model has no herbivorous reef-fish pool; specialised algal/seagrass/coral feeding differs materially from its sole/squilla diet.';references+=['FishBase/FAO rabbitfish and surgeonfish biology; reef-herbivore approximation']
 elif t in reef:
  pairs=[(17,1.)];membership='M11';mc='Very low';reason='Closest available reef/bottom-feeding approximation is Benthic Omnivores. Specialised coral/sponge feeding or mixed reef plankton/algal feeding is absent from the source; no direct membership is claimed.';references+=['Arabian Gulf Pomacanthus feeding study; reef analogue assumption']
 elif t in bill:
  pairs=[(4,1.)];membership='M5';mc='Medium';reason='Large mobile pelagic fish/squid predator fits an ecological extension of the seerfish/barracuda guild. Billfishes are not named source members; offshore/depth and migratory differences remain a transfer assumption.';references+=['FishBase sailfish and swordfish biology, FAO Nakamura 1985']
 elif t in deep:
  pairs=[(7,1.)];membership='M11';mc='Very low';reason='Closest available water-column predator approximation is Large Benthopelagics (ribbonfish/carangids). Deep/oceanic feeding and habitat, or coarse gadiform composition, are poorly represented by a shelf model exploited to 200 m.';references+=['FAO Beryx deep-water account; FishBase escolar; CSIRO/NOAA opah biology']
 elif t=='Ablennes hians':
  pairs=[(4,1.)];membership='M5';mc='Medium';reason='Neritic/oceanic surface piscivore is a supported ecological extension of Large Pelagics. FAO/FishBase and the Arabian Sea needlefish diet study support the habitat/diet match; not an explicit source member.';references+=['FishBase Ablennes hians; Arabian Sea diet study']
 elif t in {'Monacanthidae','Aluterus monoceros'}:
  pairs=[(9,1.)];membership='M5';mc='Medium' if t=='Aluterus monoceros' else 'Low';membership='M5' if mc=='Medium' else 'M6';reason='Filefish is compared with the source’s balistid medium benthic pool. Aluterus western Bay of Bengal landed-fish evidence supports bottom omnivory with strong fish feeding; whole Monacanthidae remains heterogeneous and partly conflicting.';references+=['Ghosh et al. 2021, Aluterus monoceros feeding, CMFRI repository']
 elif valid in explicit and explicit[valid][0] in [g for g,w in previous]:
  g,printed,locator=explicit[valid];pairs=[(g,1.)];membership='M1' if t==printed else 'M2';mc='High';reason=f'Source explicitly lists {printed} in {groupname[g]} ({locator}).'+(f' WoRMS links the catch label to accepted name {valid}.' if t!=printed else '')
 elif genus in generic_genus and generic_genus[genus] in [g for g,w in previous]:
  g=generic_genus[genus];membership='M1';mc='High';reason=f'Source explicitly lists the genus {genus} sp. in {groupname[g]}; the catch label lies within that genus. No numerical source-size cutoff is stated.'
 elif len(previous)>1:
  membership='M7';mc='Medium';reason='The named lineage spans the source compartments; use identified regional members as a composition proxy, rather than assign the whole label to one guild.'
  # Reconstruct the retained, lineage-restricted whole-period catch allocation.
  target={'Clupeiformes':('order','Clupeiformes'),'Carangidae':('family','Carangidae'),'Engraulidae':('family','Engraulidae'),'Scombridae':('family','Scombridae'),'Siluriformes':('order','Siluriformes'),'Pleuronectiformes':('order','Pleuronectiformes'),'Elasmobranchii':('elasmobranch',True)}.get(t)
  totals={g:0. for g,w in previous};support=[]
  for name,ps in stored.items():
   if name==t or len(ps)!=1 or ps[0][0] not in totals:continue
   tx=taxonomy.get(name,{})
   included=(target and tx.get(target[0])==target[1]) if target and target[0]!='elasmobranch' else (target and groupname[ps[0][0]] in ['Sharks','Skates & Rays'])
   if included:
    v=math.fsum(wholecatch[name][str(y)] for y in range(1950,2020));totals[ps[0][0]]+=v;support.append({'taxon':name,'group_id':ps[0][0],'total_catch_1950_2019_t':v})
  total=math.fsum(totals.values());calculated=[(g,totals[g]/total) for g,w in previous] if total>0 else []
  maxdiff=max([abs(w-dict(calculated).get(g,0)) for g,w in previous],default=0)
  retained_weight_checks.append({'taxon':t,'recorded':previous,'reconstructed':calculated,'max_difference':maxdiff,'support':support})
  if calculated:
   if maxdiff>=1e-9:pairs=calculated
   wr='W5';wc='Medium';weight_reason=('Retained' if maxdiff<1e-9 else 'Reconstructed')+' weights use identified, singly assigned total catch within this lineage in Arabian Sea 1950–2019. Its observed mix is assumed for the coarse label and held fixed across years/bases.'
   for g,w in pairs:allocations.append({'taxon':t,'group_id':g,'group':groupname[g],'raw_value':totals[g],'field':'identified lineage total catch 1950–2019','unit':'t','denominator':total,'weight':w,'confidence':wc,'source':'Regional Catch and exact WoRMS lineages','eligibility':reason,'assumption':weight_reason})
  else:
   pairs,wr,wc,weight_reason=proxy(t,[g for g,w in previous],reason+' Historical allocation cannot be independently reproduced with current taxonomy; use the approved source-model proxy instead.')
 elif previous:
  g=previous[0][0];e=oldrow['evidence']
  if oldrow['group'] in generic_compartments and oldrow['confidence']=='high':
   membership='M3';mc='High';reason=f'The source explicitly defines the generic {groupname[g]} compartment, and taxonomy/catch interpretation supports this label within it. Fishery-caught adults are intended; epifaunal unlanded crabs and planktonic larvae remain separate source pools.'
  elif t in {'Myctophidae','Balistidae'}:
   membership='M3';mc='High';reason=f'The source explicitly lists the generic {"Myctophids" if t=="Myctophidae" else "Balistids"} in {groupname[g]}. The catch family matches that source-defined generic membership; fishery-caught fish are intended, not the separately modelled larvae.'
  elif t in {'Scyphozoa','Rhizostomeae','Catostylus perezi','Cephea'}:
   membership='M3';mc='High';reason='The source explicitly places jellyfish in Micro Nekton. The taxon is a jellyfish; the misleading group name does not override source membership.'
  elif t=='Cnidaria':
   membership='M7';mc='Medium';reason='Regional functional metadata labels this phylum-level record Jellyfish, supporting Micro Nekton as a fishery interpretation. Cnidaria also includes non-jellyfish benthos, so full taxonomic containment is not claimed.'
  elif t in {'Octopus','Octopodidae','Octopoda','Cephalopoda'}:
   membership='M4';mc='Medium';reason='Source Cephalopods lists squid and cuttlefish; extend that single compartment to octopods or the broader class under a disclosed cephalopod analogue. Benthic octopod diet/behaviour is not separately modelled.'
  elif t=='Scomber':
   membership='M11';mc='Very low';reason='Closest available mackerel analogue is the dedicated Rastrelliger kanagurta pool. Scomber is not listed and can differ materially in feeding and habitat.'
  elif e=='analogue' or e=='habitat_size_guild':
   membership='M5' if oldrow['confidence']=='medium' else 'M6';mc='Medium' if membership=='M5' else 'Low';reason=oldrow['explanation']+' This is a guild extension, not explicit taxonomic membership; provider size bins are not the source model’s operative thresholds.'
  else:
   membership='M4';mc='Medium'
   relatives=[x['accepted_name'] or x['printed_name'] for x in members if groupid.get(x['group_name'])==g and (x['accepted_name'] or x['printed_name']).split()[0]==genus]
   if not relatives:relatives=[x['accepted_name'] or x['printed_name'] for x in members if groupid.get(x['group_name'])==g][:3]
   lineage=taxonomy.get(t,{}).get('family') or t
   reason=f'Taxonomy/catch ecology links {t} ({lineage}) to source representatives '+', '.join(relatives)+f' in {groupname[g]}. Extend those representatives to this label; the source does not establish complete containment or the provider’s numerical size bins.'
 else:raise ValueError('Unreviewed catch label '+t)
 assert pairs and len(set(g for g,w in pairs))==len(pairs) and math.isclose(math.fsum(w for g,w in pairs),1,abs_tol=1e-9,rel_tol=0)
 conf=max([mc,wc],key=lambda c:rank[c]);c=catch[t]['2019'];cl=classic.get(t,{})
 coeff=cl.get('sppr');ppr=0. if c==0 else (c*coeff/9 if coeff is not None else None)
 decisions.append({'taxon':t,'common_name':oldrow['common_name'],'catch_t':c,'tl':cl.get('tl'),'classic_sppr':coeff,'simple_ppr_tC':ppr,'missing_coefficient':coeff is None,'missing_annual_ppr':ppr is None,'groups':[{'group_id':g,'group':groupname[g],'weight':w} for g,w in pairs],'membership_rule':membership,'membership_confidence':mc,'allocation_rule':wr,'allocation_confidence':wc,'overall_confidence':conf,'previous_confidence':oldrow['confidence'],'previous_groups':[{'group_id':g,'weight':w} for g,w in previous],'membership_reason':reason,'allocation_reason':weight_reason,'reason':reason+' '+weight_reason,'references':references,'taxonomy_url':taxonomy.get(t,{}).get('url'),'accepted_name':valid,'year':2019,'basis':'landings'})
assert set(catch)==set(x['taxon'] for x in decisions) and len(decisions)==430
decisions.sort(key=lambda x:(x['simple_ppr_tC'] is None,-(x['simple_ppr_tC'] or 0),x['taxon']))
totcatch=math.fsum(x['catch_t'] for x in decisions);totppr=math.fsum(x['simple_ppr_tC'] for x in decisions if x['simple_ppr_tC'] is not None)
coverage=[]
for conf in rank:
 xs=[x for x in decisions if x['overall_confidence']==conf];cv=math.fsum(x['catch_t'] for x in xs);pv=math.fsum(x['simple_ppr_tC'] for x in xs if x['simple_ppr_tC'] is not None)
 coverage.append({'confidence':conf,'taxa':len(xs),'catch_t':cv,'catch_pct':100*cv/totcatch,'ppr_tC':pv,'ppr_pct':100*pv/totppr})
def rule_totals(component):
 out=[]
 for rule,conf in sorted(set((x[component+'_rule'],x[component+'_confidence']) for x in decisions)):
  xs=[x for x in decisions if x[component+'_rule']==rule and x[component+'_confidence']==conf];p=math.fsum(x['simple_ppr_tC'] for x in xs if x['simple_ppr_tC'] is not None);out.append({'rule':rule,'description':rules[rule],'confidence':conf,'ppr_pct':100*p/totppr,'taxa':len(xs)})
 out.sort(key=lambda x:-x['ppr_pct']);assert abs(math.fsum(x['ppr_pct'] for x in out)-100)<1e-8
 return out
summary={'year':2019,'basis':'landings','taxa':430,'source_groups':24,'runtime_groups':25,'catch_t':totcatch,'ppr_tC':totppr,'missing_coefficients':sum(x['missing_coefficient'] for x in decisions),'unknown_annual_ppr':sum(x['missing_annual_ppr'] for x in decisions),'coverage':coverage,'membership_rules':rule_totals('membership'),'allocation_rules':rule_totals('allocation'),'changed_confidence':sum(x['overall_confidence'].lower()!=x['previous_confidence'] for x in decisions),'changed_assignment':sum(x['previous_groups']!=[{'group_id':g['group_id'],'weight':g['weight']} for g in x['groups']] for x in decisions)}
for name,value in [('adopted_taxon_audit.json',decisions),('allocation_evidence.json',allocations),('retained_weight_reconstruction.json',retained_weight_checks),('coverage_summary.json',summary)]:
 (R/'mapping'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
