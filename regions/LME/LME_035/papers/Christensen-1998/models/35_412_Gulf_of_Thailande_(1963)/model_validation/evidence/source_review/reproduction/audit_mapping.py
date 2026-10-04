from pathlib import Path
import sys,json,math,copy,pickle,csv,re,collections
Q=Path(__file__).parent;ROOT=Q.parents[4];sys.path.insert(0,str(ROOT/'tools'));import workbooks as W;import regional as Rcalc
R=ROOT/'regions/LME_035';MID='35_412_Gulf_of_Thailande_(1963)';E=R/'validation_reports'/MID;MP=R/'models'/MID
def dump(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
with(Q/'book.pkl').open('rb')as f:b=pickle.load(f)
old=copy.deepcopy(b);native={int(g['group_seq']):g for g in json.loads((MP/'model.json').read_text(encoding='utf-8'))['group']};gg={int(g['seq']):g for g in W.records(b,'Selected model groups','Groups')};gn={s:g['group_name']for s,g in gg.items()};gi={v:k for k,v in gn.items()}
tax=json.loads((MP/f'source_evidence/mapping/{MID}.taxonomy-sources.json').read_text(encoding='utf-8'))
prior=collections.defaultdict(list)
for r in W.records(b,'PPR','Matching'):prior[r['taxon']].append(r)
resolved={r['taxon']:r for r in csv.DictReader((MP/f'source_evidence/mapping/{MID}.resolved.csv').open(encoding='utf-8-sig'))};classic={r['taxon']:r for r in W.records(b,'Classic PPR','Taxa')}
stage={r['taxon']:[]for r in W.records(b,'PPR','Allocation assumptions')}
for r in W.records(b,'PPR','Allocation assumptions'):stage[r['taxon']].append(r)
def tx(t):
 rr=tax.get(t)or{};return rr[0]if isinstance(rr,list)and rr else rr if isinstance(rr,dict)else{}
direct={3:['Trichiurus','Muraenesox','Chirocentrus','Sphyraena'],4:['Epinephelus','Lutjanus'],5:['Thunnus tonggol','Euthynnus affinis','Auxis thazard'],6:['Saurida','Lactarius','Lethrinus','Sciaenidae','Psettodes'],7:['Scomberomorus'],11:['Decapterus'],13:['Priacanthus'],14:['Plectorhinchus','Scolopsis','Upeneus','Pomadasys','Pampus','Arius'],16:['Bothidae','Cynoglossidae'],17:['Nemipterus','Pentaprion'],19:['Rastrelliger'],21:['Leiognathus']}
pairs={2:[2,8],3:[3,9],4:[4,10]}
fish=[3,4,5,6,7,9,10,11,13,14,16,17,19,20,21,23]
broads={'Marine fishes not identified':fish,'Marine groundfishes not identified':[3,4,6,9,10,13,14,16,17,21,23],'Marine pelagic fishes not identified':[3,5,7,9,11,14,19,20],'Perciformes':[3,4,5,6,7,9,10,11,13,14,17,19,21,23],'Miscellaneous aquatic invertebrates':[12,18,22,24,25,26,27],'Miscellaneous marine crustaceans':[22,24,25,27],'Malacostraca':[22,24,25,27],'Mollusca':[12,24,26,27],'Decapoda':[22,24,25,27]}
def choose(t,r):
 a=tx(t);fam=a.get('family');gen=t.split()[0];priorids=[gi[x['group']]for x in prior[t]if x.get('group')]
 if t in broads:
  why='Broad reporting scope approximated over every compatible named, residual and juvenile source pool; species/stage composition is unknown. '
  if t.startswith('Marine '):why+='SAU ISSCAAP39 is bony fish; dedicated Sharks/Juv.sharks/Rays excluded. Functional Medium demersals and separately named taxa are not exhaustive composition evidence. '
  if t=='Marine groundfishes not identified':why+='Ponyfishes/Flatfish/grouper stages and large demersal guild included; Lg.piscivores also contains actual pelagic Chirocentrus/Sphyraena, a mixed-pool mismatch. '
  if t=='Marine pelagic fishes not identified':why+='Named tuna/mackerel/scad, pelagic Chirocentrus/Sphyraena and Pampus source connections retain their actual mixed guilds. Predecessor Table2 supports Pampus in medium pelagics. Lactarius FAO evidence is bottom-associated and source trashfish composition supplies no positive pelagic member; these pools excluded with named grouper/flatfish/ponyfish and small demersals. '
  if t=='Perciformes':why+='Historical Perch-likes reporting scope spans source scombrids/carangids and multiple reef/demersal guilds; current narrow WoRMS order is not the historic mixture. Mixed Lg/Med.pisc pools also include non-perciform members. '
  if t in ['Mollusca','Decapoda','Malacostraca','Miscellaneous marine crustaceans','Miscellaneous aquatic invertebrates']:why+='Named benthic/cephalopod/crustacean and plausible unlisted benthos/plankton stages retained as an ecological approximation; full composition is not explicitly enumerated. '
  return broads[t],'M10','Very low',why
 if fam in ['Istiophoridae','Xiphiidae'] or t in ['Istiophorus','Makaira']:
  return[5],'M11','Very low','Pauly&Christensen1993 Table2/PDF19 assigns sailfish&billfish and tuna/frigate mackerels to Large pelagics in Gulf ModelC (Figure5/PDF8). Focal1998 source cites that10–50m predecessor but its Tuna lists coastal Thunnus tonggol/Euthynnus/Auxis. Tuna is a receiving large-pelagic predator analogue via explicit predecessor crosswalk, not focal billfish membership; oceanic/deeper species and narrowed taxonomy mismatch. Lg.piscivores explicitly demersal and has different named fish; source diet and geography are limits, not an extra eligibility gate.'
 for s,names in direct.items():
  if t in names or gen in names or fam in names:
   ids=pairs.get(s,[s]);mr='M2'if gen in ['Epinephelus','Plectorhinchus']else'M1'if t in names else'M3'
   return ids,mr,'High','Focal Christensen1998 p130 explicitly names '+next(n for n in names if t==n or gen==n or fam==n)+'. Verified constituent identity retains the documented source group'+(' and complete juvenile/adult union; Juv.groupers includes both grouper and snapper.'if len(ids)>1 else'.')+' Representative list does not prove containment of unrelated higher taxa.'
 if t in ['Carangidae','Chondrichthyes']:
  return([3,9,11]if t=='Carangidae'else[2,8,15]),'M10','Very low',('Scad has explicit Decapterus; large coastal carangid predators use the Lg.piscivore pair as an unlisted guild analogue. Broad jacks/pompanos mixture is not observed; mixed source guild composition remains approximate.'if t=='Carangidae'else'Cartilaginous reporting scope approximated by represented shark stages and rays; unrepresented chimaeras have no documented source group. Unknown species/stage composition remains.')
 if t=='Elasmobranchii':return[2,8,15],'M3','High','Source generic shark juvenile/adult and ray pools jointly represent the elasmobranch union. Chimaeras excluded from reported class. Species/stage mixture is unknown and graded separately.'
 if t=='Serranidae':return[4,10],'M10','Very low','SAU historical Basses,groupers,hinds scope includes source Epinephelus (current Epinephelidae), but current Serranidae is distinct and other basses are not source-listed. Grouper/snapper stage union is a historical grouper proxy with unresolved bass/feeding mixture; no modern synonymy is asserted.'
 if t in ['Lutjanidae','Cephalopholis boenak','Pristipomoides']:return[4,10],'M9','Medium','Source Epinephelus/Lutjanus juvenile+adult union supports a related grouper/snapper extension. Family or related genera are not individually source-listed; complete source union retained with inferred membership.'
 if fam in ['Carcharhinidae','Sphyrnidae','Alopiidae','Lamnidae'] or t in ['Sphyrnidae']:
  return[2,8],'M3','High','Verified shark identity fits the generic source shark union, including juvenile sharks. No species or stage cutoff is documented; stage-weight uncertainty is graded in allocation, and whole-LME habitat transfer remains a model limitation.'
 if 'rays' in r['functional_group']or t in ['Batoidea','Dasyatidae','Himantura']:return[15],'M3','High','Verified batoid/ray identity fits the dedicated Rays compartment; no competing ray stage group is present.'
 if fam in ['Loliginidae','Octopodidae','Sepiidae']or t in ['Cephalopoda','Teuthida','Octopoda','Octopus','Octopodidae','Sepia','Sepiidae','Loliginidae']:return[12],'M3','High','Verified squid/cuttlefish/octopus identity fits generic Cephalopods. Non-cephalopod Molluscs and general Benthos are less specific alternatives.'
 if r['functional_group']=='Jellyfish' or t in ['Scyphozoa','Rhizostomeae','Cephea']:return[18],'M3','High','Verified gelatinous scyphozoan identity fits the dedicated source Jellyfish compartment; general zooplankton is less specific.'
 if r['functional_group']=='Shrimps' or fam in ['Penaeidae','Sergestidae','Solenoceridae']:return[25],'M3','High','Verified penaeid/sergestid/solenocerid shrimp identity fits the dedicated generic Shrimps pool. No source shrimp stage partition or named competing shrimp pool exists.'
 if r['functional_group']=='Lobsters, crabs' or fam in ['Portunidae','Oziidae','Palinuridae','Scyllaridae']or t=='Charybdis feriatus':return[22],'M2'if t=='Charybdis feriatus'else'M3','High','Verified crab/lobster identity fits source Crab,lobster; Shrimps and general Benthos are less specific. '+('WoRMS current feriatus→feriata orthographic bridge retained; raw catch label unchanged.'if t=='Charybdis feriatus'else'')
 if t in ['Bivalvia','Crassostrea','Gastropoda','Modiolus','Ostreidae','Perna viridis','Tegillarca granosa','Trochus niloticus','Veneridae'] or fam in ['Ostreidae','Mytilidae','Modiolidae','Arcidae','Trochidae','Veneridae']:return[26],'M2'if t=='Trochus niloticus'else'M3','High','Verified non-cephalopod benthic mollusc fits dedicated Molluscs. Cephalopods is separate; general Benthos is a less specific alternative. Historical/current spelling and raw label are preserved.'
 if fam=='Leiognathidae'or t=='Leiognathidae':return[21],'M2'if gen in ['Eubleekeria','Gazza','Photopectoralis']else'M3','High','Dedicated Ponyfishes with historical Leiognathus supports the verified leiognathid identity, including modern segregated genera; modern nomenclature does not create a different ecological guild.'
 if fam=='Engraulidae'or t=='Engraulidae':return[20],'M3','High','Source small-pelagic components explicitly include anchovy; verified anchovy identity fits that common-name component. Named Chirocentrus large-piscivore pool is a different clupeiform family.'
 if t in ['Gerreidae','Haemulidae','Lethrinidae','Mullidae','Priacanthidae','Stromateidae','Paralichthyidae','Ariidae','Nemipteridae','Scombridae','Scombroidei','Sphyraenidae','Trichiuridae']:
  ids=priorids
  if t in ['Sphyraenidae','Trichiuridae']:ids=[3,9]
  return ids,'M9','Medium','Source-listed representative genera/families establish the closest related taxonomic/guild set; the whole reported family/suborder is an explicit extension, not exhaustive named membership. Other named guilds were checked and lack a more direct connection. '+('Historical Scombroidei includes source hairtails/barracudas and named scombrid pools; reporting concept differs from current order.'if t=='Scombroidei'else'')
 if t=='Synodontidae':return[6],'M5','Medium','Historical FAO Synodontidae includes source Saurida;2026 WoRMS separates Harpadontidae. Retained historical lizardfish concept and shelf demersal piscivory support Med.dem.pisc; no current-family containment is claimed.'
 if priorids and priorids[0]==3:
  low=t in ['Congridae','Elagatis bipinnulata','Latidae','Megalops cyprinoides','Scorpaenidae'];verylow=t=='Coryphaena hippurus';mc='Very low'if verylow else'Low'if low else'Medium';mr='M11'if verylow else'M6'if low else'M5'
  why='Large coastal fish-predator connection to source Trichiurus/Muraenesox/Chirocentrus/Sphyraena and complete juvenile/adult union. Source calls guild large demersal but actual Chirocentrus/Sphyraena have pelagic components; FAO historical regional sheets support coastal/reef predator ecology. Named Tuna/Scad are competing but different taxonomic/schooling examples; species and source-composition differences remain.'
  if t=='Megalops cyprinoides':why+=' Historical FAO maximum55cm contradicts the provider Large>=90cm bin; no literal source length cutoff is supplied. Size/habitat uncertainty lowers membership, with accepted stage fractions retained.'
  if t=='Congridae':why+=' Source Muraenesox is Muraenesocidae, not Congridae; whole conger/garden-eel family fit is partial.'
  if t=='Coryphaena hippurus':why+=' Oceanic/coastal surface feeding makes Tuna a plausible competing pelagic-predator analogue; neither pool explicitly lists dolphinfish. Retain the accepted large-predator pair at Very low rather than assert exclusive source membership or change a supported stage fraction.'
  if t=='Elagatis bipinnulata':why+=' Surface/coastal-oceanic habitat and related Scad pool give competing fits; retained large-predator assignment is partial at Low, not an exhaustive containment claim.'
  if t in ['Latidae','Scorpaenidae']:why+=' Whole reported family spans varying size/feeding ecology and is not source-listed; broad fit remains partial at Low.'
  return[3,9],mr,mc,why
 if priorids==[23]:return[23],'M11','Very low','Unlisted coastal herbivore/omnivore has a positive residual-catch connection to the source trash-fish pool, which is not an exclusive omnivore guild. Named demersal piscivores and benthivores are different principal guilds; residual membership/species composition and feeding are unverified.'
 if t in ['Caesio','Caesionidae','Alepes']:return priorids,'M11','Very low','Unlisted reef-associated schooling fish uses '+gn[priorids[0]]+' through source coastal schooling '+('Decapterus carangid'if t=='Alepes'else'sardine/anchovy small-pelagic')+' connection. Reef habitat, feeding and species composition differ; other large/demersal guilds offer no directly named match.'
 if t in ['Aluterus','Tetraodontidae']:return priorids,'M6','Low','Partial benthic-invertebrate/coastal feeding connection to source Med.dem.benth examples Upeneus/Pomadasys/Plectorhinchus; feeding/species variation and absent explicit membership remain. Trash fish is a less specific residual alternative.'
 if t in ['Echinodermata','Holothuriidae']:return[24],'M5','Medium','Verified benthic invertebrate identity fits the source Benthos residual; named mollusc/crab/shrimp and plankton compartments represent different taxa. Detailed source benthos composition is unavailable; membership is inferred.'
 if priorids:
  s=priorids[0];why=prior[t][0].get('explanation')or''
  return priorids,'M4'if fam in ['Scombridae','Carangidae','Nemipteridae','Gerreidae','Haemulidae','Mullidae']else'M5','Medium','Reviewed unlisted related taxon/ecological extension to '+gn[s]+'. Positive source connection: '+why.replace('Reviewed against the Ecobase group name and diet; the original paper p.130 lists important components but does not settle this taxon.','').replace('Scad is the model\'s only carangid compartment','Scad is the explicit Decapterus pool')+' Source example lists are illustrative, and competing named/residual groups do not supply a more direct documented fit; broader regional membership is assumed.'
 raise ValueError(t)
audit=[];newmaps=[];ledger=[];decisions=[];changes=[]
for r in sorted([x for x in W.records(b,'Catch','Catch')if x['catch_basis']=='landings'],key=lambda x:x['taxon']):
 t=r['taxon'];ids,mr,mc,why=choose(t,r);assert len(ids)==len(set(ids))and all(s in native for s in ids)
 raw=[float(native[s]['export'])for s in ids];bio=[float(native[s]['biomass'])for s in ids];oldids={gi[x['group']]for x in prior[t]if x.get('group')};oldbasis=resolved.get(t,{}).get('weight_basis');same=set(ids)==oldids or(t in stage and set(ids)==oldids|{8 if 2 in ids else 9 if 3 in ids else 10})
 if len(ids)==1:ws=[1.];wr='W1';wc='High';ww='One reviewed group receives100%; no allocation split.'
 elif same and oldbasis=='catch_composition':
  pw={gi[x['group']]:x['weight']for x in prior[t]if x.get('group')};ws=[pw.get(s,0.)for s in ids];wr='W5';wc='Low';ww='Exact accepted identified-catch fractions retained. Original all1950–2019 singly assigned guild donors are not restricted to this lineage; country/gear/period mismatches and unobserved residual composition make the proxy Low (see identified_catch_proxy_review.json).'
 elif all(math.isfinite(x)and x>=0 for x in raw)and math.fsum(raw)>0:
  ws=[x/math.fsum(raw)for x in raw];wr='W4';wc='Medium';ww='Complete accepted native export/catch proportions, including genuine canonical zeros, are the fixed1980 composition proxy; no observed regional/year/gear/stage caught-mass partition is claimed.'
  if same:
   pw={gi[x['group']]:x['weight']for x in prior[t]if x.get('group')}
   assert all(math.isclose(pw.get(s,0),w,abs_tol=1e-8)for s,w in zip(ids,ws)),t
   ws=[pw.get(s,0.)for s in ids]
 else:
  assert all(math.isfinite(x)and x>=0 for x in bio)and math.fsum(bio)>0;ws=[x/math.fsum(bio)for x in bio];wr='W9';wc='Medium';ww='Complete biomass fallback follows unusable/zero-total source catch under composition/catchability assumption.'
 overall=min([mc,wc],key=['Unresolved','Very low','Low','Medium','High'].index);reason=(why+' '+ww+' Fixed1980 coefficients and proxy fractions transfer across1950–2019 whole-LME landings/catch/discards; source completeness/applicability remains limited.').replace('receives100','receives 100').replace('native export/catch','native export/catch').replace('Fixed1980','Fixed 1980').replace('across1950','across 1950').replace('fixed1980','fixed 1980').replace('all1950','all 1950').replace('SAU ISSCAAP39','SAU ISSCAAP 39').replace('2026 WoRMS','2026 WoRMS')
 c=r.get(2019);co=classic.get(t,{});sp=co.get('sppr');pp=0. if c==0 else c*sp/9 if W.finite(c)and W.finite(sp)else None
 a=dict(taxon=t,tl=co.get('tl'),classic_sppr=sp,catch_tonnes=c,simple_chain_ppr_tC=pp,common_name=r['common_name'],functional_group=r['functional_group'],membership_rule=mr,membership_confidence=mc,allocation_rule=wr,allocation_confidence=wc,overall_confidence=overall,assumed=mc!='High'or len(ids)>1,group_ids=ids,group_names=[gn[s]for s in ids],weights=ws,mapping_display='; '.join(gn[s]+f' ({100*w:.6f}%)'for s,w in zip(ids,ws)),reason=reason,sources=['Christensen1998p130','EcoBase412Native','WoRMS2026','SAUv50.1','ClassicSaved']+(['Predecessor1993Table2','FAOCatalogues']if tx(t).get('family')in ['Istiophoridae','Xiphiidae']else []),taxonomic_record=tx(t),prior_mapping=prior[t])
 audit.append(a)
 for s,w in zip(ids,ws):
  row=dict(model_id=MID,taxon=t,group=gn[s],weight=w,confidence=overall.lower().replace(' ','_'),evidence=f'validation_reports/{MID}/taxon_audit.json',explanation=reason)
  newmaps.append(row)
  ledger.append(dict(unit_id='LME_035',model_id=MID,taxon=t,group=gn[s],seq=s,weight=w,rule=wr,membership_rule=mr,membership_confidence=mc,allocation_confidence=wc,confidence=overall.lower().replace(' ','_'),assumed=a['assumed'],source_catch_field='export',source_catch_raw=native[s]['export'],source_catch=raw[ids.index(s)],loaded_catch=gg[s]['catch'],catch_provenance='Explicit accepted EcoBase canonical export, not independently verified full published numeric table; canonical zero distinct from missing/default0.',source_biomass=bio[ids.index(s)],source_period='1980',years_applied='1950-2019',catch_bases_applied='landings;catch;discards',evidence=row['evidence'],limitations=reason))
 decisions.append(dict(taxon=t,included=[dict(seq=s,group=gn[s],source_catch=raw[i],source_catch_raw=native[s]['export'],source_biomass=bio[i],weight=ws[i],canonical_zero=raw[i]==0)for i,s in enumerate(ids)],excluded=[dict(seq=s,group=gn[s],reason='Outside independently reviewed set. '+why)for s in native if s not in ids],membership_rule=mr,allocation_rule=wr,catch_total=math.fsum(raw),biomass_total=math.fsum(bio),source_decision=why,full_numeric_source_fidelity_claim=False))
 changes.append(dict(taxon=t,old=prior[t],new=[x for x in newmaps if x['taxon']==t],kind='mapping_or_weight'if [(x.get('group'),x['weight'])for x in prior[t]]!=[(gn[s],w)for s,w in zip(ids,ws)]else'confidence_or_rationale',membership_rule=mr,allocation_rule=wr))
assert len(audit)==247 and all(math.isclose(math.fsum(a['weights']),1,abs_tol=1e-10)for a in audit)
ct=math.fsum(a['catch_tonnes']for a in audit);pt=math.fsum(a['simple_chain_ppr_tC']for a in audit if W.finite(a['simple_chain_ppr_tC']))
def parts(rule,conf):
 out=[]
 for rr,cc in sorted(set((a[rule],a[conf])for a in audit)):
  p=math.fsum(a['simple_chain_ppr_tC']for a in audit if a[rule]==rr and a[conf]==cc and W.finite(a['simple_chain_ppr_tC']));out.append(dict(rule=rr,confidence=cc,ppr_tC=p,ppr_percentage=p/pt*100))
 return sorted(out,key=lambda x:-x['ppr_percentage'])
cats=[]
for label in ['High','Medium','Low','Very low','Unresolved']:
 aa=[a for a in audit if a['overall_confidence']==label];c=math.fsum(a['catch_tonnes']for a in aa);p=math.fsum(a['simple_chain_ppr_tC']for a in aa if W.finite(a['simple_chain_ppr_tC']));cats.append(dict(label=label,taxa=len(aa),catch_tonnes=c,ppr_tC=p,catch_percentage=c/ct*100,ppr_percentage=p/pt*100))
summary=dict(unit_id='LME_035',model_id=MID,year=2019,basis='landings',source_scope='all',taxon_filter='all',group_filter='none',unidentified='method',source_groups=29,synthetic_groups=['diet_import30'],taxa=247,total_catch_tonnes=ct,total_simple_chain_ppr_tC=pt,missing_coefficient_taxa=[a['taxon']for a in audit if not W.finite(a['classic_sppr'])],unknown_ppr_taxa=[a['taxon']for a in audit if a['simple_chain_ppr_tC']is None],confidence_summary=cats,membership_summary=parts('membership_rule','membership_confidence'),allocation_summary=parts('allocation_rule','allocation_confidence'))
for name,value in [('taxon_audit.json',audit),('candidate_and_allocation_evidence.json',decisions),('adopted_mapping_changes.json',changes),('coverage_summary.json',summary)]:dump(name,value)
if '--adopt'in sys.argv:
 assert W.sha(R/'LME_035.xlsx')=='718e1f7b093f6a3c75bbc52277252ead0613b8223f6ba75990180a9212e93930'
 b['PPR']['Matching']=W.table_dict(newmaps);b['PPR']['Mapping review']=W.table_dict([{k:a[k]for k in ['taxon','membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence','assumed','reason']}for a in audit]);b['PPR']['Allocation assumptions']=W.table_dict(ledger)
 Rcalc.recalculate(b,R/'LME_035.xlsx');b['Classic PPR']=copy.deepcopy(old['Classic PPR']);rh,rv=b['PPR–NPP']['Ratios'];b['PPR–NPP']['Ratios']=(rh,[r for r in W.rows(old,'PPR–NPP','Ratios')if not r[0]]+[r for r in rv if r[0]])
 Rcalc.set_setting(b,'source_note','Reviewed all247 taxa: source/genus/functional matches, exact retained stage weights, Low identified-catch proxy limitations, expanded Very low aggregate candidates and predecessor-supported billfish analogues. Scientific payload1980 under inherited1963 identity; whole-LME/year transfer remains provisional. GE/TE/With Egestion WARN and six symbolic failures retained. Evidence: validation_reports/'+MID+'/taxon_audit.json.')
 Rcalc.set_setting(b,'calculation_status','provisional: reviewed mapping; direct GE/TE/With Egestion WARN; source completeness and whole-LME1980 transfer limits retained');Rcalc.set_setting(b,'production_eligible',False);Rcalc.set_result_hash(b);W.write_book(R/'LME_035.xlsx',b)
 for sheet in ['Catch','Classic PPR','NPP']:assert W.digest_tables(list(b[sheet].items()))==W.digest_tables(list(old[sheet].items())),sheet
 assert W.digest_tables(b['Selected model groups'])==W.digest_tables(old['Selected model groups']);dump('adoption_record.json',dict(workbook_sha256=W.sha(R/'LME_035.xlsx'),input_hash=W.input_hash(b),result_hash=Rcalc.result_hash(b),taxa=247,stage_taxa=len(stage),canonical_model_sha256=W.sha(MP/'model.json'),protected_cached_blocks_exact=True,fresh_canonical_validation_pending=True))
print(json.dumps(summary,indent=2))
