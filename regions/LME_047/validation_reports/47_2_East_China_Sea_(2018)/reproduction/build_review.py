from pathlib import Path
import sys,json,math,hashlib,csv,gzip,zipfile,io,re,collections,copy
import numpy as np
from docx import Document
ROOT=Path.cwd();Q=Path(__file__).parent;R=ROOT/'regions/LME_047';MID='47_2_East_China_Sea_(2018)';O=R/'validation_reports'/MID;O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,overview,sha
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
b=json.loads((Q/'current_book.json').read_text(encoding='utf-8'));old=collections.defaultdict(list)
for r in records(b,'PPR','Matching'):old[r['taxon']].append(r)
catch={r['taxon']:r for r in records(b,'Catch','Catch') if r['catch_basis']=='landings'}
totalcatch={r['taxon']:r for r in records(b,'Catch','Catch') if r['catch_basis']=='catch'}
classic={r['taxon']:r for r in records(b,'Classic PPR','Taxa')}
groups={r['group_name']:r for r in records(b,'Selected model groups','Groups')}
byseq={int(r['seq']):r for r in groups.values()};names={i:r['group_name'] for i,r in byseq.items()}
model=json.loads((R/'models'/MID/'model.json').read_text(encoding='utf-8'));can={int(r['group_seq']):r for r in model['group']}
paper=R/'papers/ECS-2022';supp=next(paper.glob('*.docx'));dd=Document(supp)
source_rows=[[c.text for c in r.cells]for r in dd.tables[3].rows]
save('supplement_membership_crosswalk.json',{'source':supp.relative_to(R).as_posix(),'source_sha256':sha(supp),'table':'S1','applicable':'TableS1 caption explicitly identifies M2018; main paper retains the same named groups across versions. Numerical order 16/17 in S1 differs from main Table1; join by names, never row position.','rows':source_rows,'scope':'Composition representatives are evidence of membership, not an exhaustive modern family definition.'})
# Independent Table1 transcription, M2018 B,PB,QB,EE; no edits to scientific inputs.
params={1:[43.2,82.75,None,.411],2:[12.82,40,160,.274],3:[1.841,6.7,24.2,.462],4:[.343,3,7,.957],5:[1.53,6.56,26.9,.955],6:[6.427,1.2,3.7,.232],7:[1.359,2,9,.795],8:[.0534,4.5,12,.996],9:[.288,5.1,19.2,.998],10:[.894,3,10,.946],11:[4.701,4.762,22.3,.979],12:[.278,2.156,8.497,.965],13:[.275,1.643,6.16,.324],14:[3.369,2.9,5.6,.338],15:[1.497,2.12,6.19,.953],16:[2.103,1.048,11.4,.667],17:[1.294,1.287,12.23,.695],18:[.349,1.451,9.921,.952],19:[.439,3.279,7.992,.826]}
text=(Q/'ECS-2022.txt').read_text(encoding='utf-8');part=text[text.index('20. Large yellow croakers'):];lines=part.splitlines()
for seq in [20,21,22,23,24]:
 ix=next(i for i,x in enumerate(lines) if x.startswith(str(seq)+'. ')); vals=lines[ix+1:ix+11]
 params[seq]=[None if vals[i].strip() in ['–','—','-'] else float(vals[i]) for i in [3,5,7,9]]
cells=[]
for seq,values in params.items():
 for fld,v in zip(['biomass','pb','qb','ee'],values):
  raw=can[seq].get(fld);cv=None if raw in [None,'-9999'] else float(raw)
  cells.append({'seq':seq,'group':names[seq],'field':fld,'published':v,'canonical':cv,'matches':v==cv,'interpretation':'Input missing' if v is None else 'Published numeric input'})
save('source_parameter_cell_review.json',{'source':'Xu2022 Table1 PDF5','cells':cells,'mismatches':[x for x in cells if not x['matches']],'action':'Preserve accepted inputs, record any differences.'})
dietrows=[]
for seq,g in can.items():
 ds=(g.get('diet_descr')or{}).get('diet',[]);ds=ds if isinstance(ds,list) else [ds];dietrows.append({'seq':seq,'group':names[seq],'raw_sum':sum(float(x['proportion']) for x in ds),'items':ds})
save('raw_diet_review.json',{'source':'S3, M2018; prey and predator names used to resolve supplementary16/17 numbering','canonical_rows':dietrows,'accepted_runtime':'normalize_DC=True, DC_tol=0.001; preserved','note':'Zeros in loaded catch are defaults for absent fields, not source catch observations.'})
dietcells=[]
for row in list(dd.tables[5].rows)[1:]:
 cc=[c.text.strip()for c in row.cells]
 if not cc[0].isdigit():continue
 prey=int(cc[0])
 for pred,value in zip(range(2,24),cc[2:]):
  if not value:continue
  value=float(value);d=(can[pred].get('diet_descr')or{}).get('diet',[]);d=d if isinstance(d,list)else[d];cv=next((float(x['proportion'])for x in d if int(x['prey_seq'])==prey),0.)
  dietcells.append({'prey':prey,'predator':pred,'published':value,'canonical':cv,'matches':value==cv})
save('source_diet_cell_review.json',{'source':'TableS3 M2018; native matrix axes use main Table1 IDs','cells':dietcells,'mismatches':[x for x in dietcells if not x['matches']],'parameter_action':'None. Preserve accepted diet and normalization even if differences exist.'})
# Reconstruct actual historical all-years total-catch guild donors and every raw stratum.
original_csv=R/'models'/MID/'source_evidence/mapping'/f'{MID}.csv'
orig=list(csv.DictReader(original_csv.open(encoding='utf-8-sig')))
solo=collections.defaultdict(list);totals={t:sum(round(float(r[y] or 0),3)for y in range(1950,2020))for t,r in totalcatch.items()}
for r in orig:
 ns=[v.strip() for v in r['group'].split('|')]
 if len(ns)==1 and ns[0].lower()!='unresolved':solo[ns[0]].append(r['taxon'])
if not (O/'identified_catch_proxy_review.json').exists():
 raw=R/'raw/LME_047-catch.zip';strata={};donortaxa={t for vv in solo.values()for t in vv};rawsums=collections.defaultdict(float)
 with zipfile.ZipFile(raw)as z:
  member=next(n for n in z.namelist()if n.endswith('.csv'))
  with z.open(member)as fh:
   for rr in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8-sig')):
    t=rr['scientific_name'];a=float(rr['tonnes']);rawsums[t]+=a
    if t not in strata:strata[t]={k:collections.defaultdict(float)for k in ['fishing_entity','gear_type','fishing_sector','reporting_status','catch_type','end_use_type','year']}
    for k,v in strata[t].items():v[rr[k]]+=a
 proxy=[]
 for t,rr in old.items():
  if len(rr)<2:continue
  ns=[r['group']for r in rr];sums=[sum(totals[x]for x in solo[n])for n in ns];den=sum(sums);weights=[v/den for v in sums]if den else None
  proxy.append({'taxon':t,'eligible_old_groups':ns,'saved_weights':[r['weight']for r in rr],'reconstructed_weights':weights,'maximum_absolute_difference':max(abs(r['weight']-ww)for r,ww in zip(rr,weights))if weights else None,'donor_labels_by_group':{n:solo[n]for n in ns},'rounded_all_years_total_catch_by_group':dict(zip(ns,sums)),'target_raw_strata':strata.get(t),'pooled_donor_raw_strata':{k:dict(sum((collections.Counter(strata[x][k])for n in ns for x in solo[n] if x in strata),collections.Counter()))for k in ['fishing_entity','gear_type','fishing_sector','reporting_status','catch_type','end_use_type','year']}})
 save('identified_catch_proxy_review.json',{'builder':'workflow_development_2026_09/tools/build_model_workbook.py lines154–218; mapping_io.read_catch consumes catch_tonnes, not landings','selector':'Every singly assigned taxon in each source guild, all1950–2019 years, rounded annual total catch to0.001t before summing. No within-target-lineage filter. Composite and unresolved labels excluded.','raw_zip_sha256':sha(raw),'raw_member':member,'original_mapping_sha256':sha(original_csv),'donor_all_years_raw_total_by_label':{t:rawsums[t]for t in donortaxa},'rounded_totals_by_label':{t:totals[t]for t in donortaxa},'records':proxy,'decision':'Retain historical query/strata as evidence. Current approved fallback uses complete source M2018 biomass because selected-model catch fields are missing; no claim that guild donors measure target composition.'})
# Explicit review overrides. Eligibility is derived before numerical biomass weighting.
sets={'Marine fishes not identified':list(range(11,22)),'Marine finfishes not identified':list(range(11,22)),'Marine pelagic fishes not identified':[11,13,14,16,17,18,19],'Mollusca':[4,10],'Miscellaneous marine crustaceans':[5,8,9],'Miscellaneous aquatic invertebrates':list(range(3,11)),'Carangidae':[13,17,19],'Clupeiformes':[11,13,16,19],'Pleuronectiformes':[12,13,18],'Scorpaeniformes':[11,12,13,16,18],'Gadiformes':[11,13,17,18],'Perciformes':[11,12,13,14,16,17,18,19,20,21],'Trichiuridae':[13,14],'Engraulidae':[11,16],'Hexagrammidae':[12,16],'Synodontidae':[13,15],'Scombroidei':[13,14,16,18],'Mola mola':[11],'Scaridae':[19]}
sets['Pennahia argentata']=[13,18]
reasons={
'Marine fishes not identified':'Provider key100039 is a bony Osteichthyes/ISSCAAP39 reporting pool. All eleven bony-fish source groups11–21 have actual eligible members, including named croakers, hairtail and Bombay duck. The mixed Benthivores guild also contains rays; its bony members establish eligibility but the group coefficient retains cartilage pooling. Dedicated Sharks22, Mammals23 and basal/invertebrate groups are excluded. Medium-demersal metadata and separately reported species do not establish exhaustive exclusions. Unknown residual composition makes membership Very low.',
'Marine finfishes not identified':'Provider key100139 is the bony finfish residual/ISSCAAP39, not a cartilage pool. Same independently reviewed eleven fish groups11–21 as marine-fish residual; source12 has bony/ray pooling. Named species reported separately do not prove absence from residual catch. Basal/invertebrate, Sharks22 and Mammals23 excluded. Composition across species and guilds remains unknown.',
'Marine pelagic fishes not identified':'Provider key100339 is a bony pelagic residual. Planktivores11 has Benthosema/anchovies; Piscivores13 has Auxis/Coryphaena and Sphyraena; Hairtails14 represents benthopelagic Trichiurus;16 Scomber/Setipinna,17 Decapterus/Trachurus 18Rexea prometheoides is documented meso-/benthopelagic and19 Ilisha/Caranx establish meaningful pelagic candidates. Broad mixed-guild coefficients retain demersal members. Dedicated demersal croakers20/21, Bombay duck15 and benthic12 are excluded on actual feeding/habitat definition, not size-bin metadata. Dedicated Sharks22 excluded. Unknown mixture and benthopelagic boundary remain Very low.',
'Mollusca':'Exact provider common name includes clams, sea snails, squids and octopuses. S1 Mollusks4 explicitly contains Bivalves and Cephalopods10 contains squid/cuttlefish/octopod members. Both retained; separate cephalopod reporting does not prove their absence. Gastropods lack an explicit source compartment and the bivalve coefficient is their weak benthic molluscan analogue. Unknown taxon proportions make this broad mixture Very low.',
'Miscellaneous marine crustaceans':'The Crustacea reporting label can include source Benthic Crustaceans5 (Gammaridea/Cumacea), Crabs8 and Shrimps9. Small size/low landings and separately named taxa are not exhaustive exclusions. Zooplankton2 has actual Amphipoda and pelagic larvae and is not taxonomically ineligible. Excluding this plankton-community coefficient is an explicit landed benthos/nekton approximation; no source evidence proves its absence from the reporting label. The three bottom/nekton crustacean groups form a Very low broad-composition approximation.',
'Miscellaneous aquatic invertebrates':'Broad Invertebrata residual can include Polychaetes3, Bivalves4, Benthic Crustaceans5, Ophiuroidea6, Cnidaria7, Crabs8, Shrimps9 and Cephalopods10. Actual members support these organism classes; provider tags and separate taxon reporting do not prove absence. Phytoplankton1 is not an animal invertebrate. Zooplankton2 includes actual Copepods/Amphipoda/larvae and is not taxonomically ineligible; its exclusion is an explicit landed benthos/nekton ecological approximation. No source evidence proves absence from the residual, and3–10 is not claimed to be an exhaustive taxonomic union. Unknown mixture is Very low.',
'Carangidae':'Source17 includes Decapterus, Trachurus and Parastromateus;19 includes Caranx. Identified regional Seriola/Megalaspis records support extension to piscivorous13 as well. Complete inferred set13/17/19 replaces omission of the predatory member type; representative species are not an exhaustive family definition.',
'Clupeiformes':'Source anchovies/Sardinella11, Setipinna16 and Ilisha19 establish multiple guilds. Regional catch Chirocentrus dorab is a piscivorous clupeiform, supporting13. The historical order is applied to the provider reporting label; no assumption of an exclusively planktivorous family mixture.',
'Pleuronectiformes':'Source12 contains benthic-flatfish analogue members and18 explicitly Cynoglossus joyneri. Regional piscivorous Paralichthys and Psettodes labels support13. Three feeding types retained under an inferred order-wide set; source composition is incomplete.',
'Scorpaeniformes':'Historical provider order: source11 Erisphex,12 Chelidonichthys/Lepidotrigla and supported18 Sebastes-type predators; regional Platycephalus supports13 and Pleurogrammus16. Modern order rearrangements do not justify deleting historical catch members. Five inferred guilds retained; mixed boundaries remain uncertain.',
'Gadiformes':'Source11 explicitly Bregmaceros and13 Coelorinchus. Regional Gadidae labels include benthic cod18 and more pelagic pollock17 analogues. Both are northern-water weak fits; full historical reporting-order candidate set retains this mismatch rather than silently excluding these records.',
'Perciformes':'Provider historical broad order contains source Acropoma/Apogon/Secutor11, benthic12, piscivorous13, Trichiurus14, Scomber16, carangids/pomfrets17, predators18, omnivores19 and Larimichthys20/21. Harpadon15 is aulopiform and dedicated Sharks22/Mammals23 are excluded. Mixed source pools contain non-perciforms, so the coefficients are pooled approximations; modern taxonomic restructuring and a demersal tag do not define this historical reporting mixture.',
'Trichiuridae':'Trichiurus lepturus has dedicated Hairtails14, while S1 Lepturacanthus savala and Tentoriceps cristatus occur in Piscivores13. Their separate named catch records do not prove absence from unidentified family catch. Both actual source members retained.',
'Engraulidae':'S1 Thryssa/Stolephorus11 and Setipinna tenuifilis16 are engraulid members. Family catch cannot be restricted to11 merely because the named Engraulis label is reported separately.',
'Hexagrammidae':'Regional Hexagrammos benthic-invertebrate feeding supports12 and Pleurogrammus plankton/benthos feeding supports16. Separate species labels do not eliminate either from the broader family record. Inferred regional set, not author-enumerated family membership.',
'Synodontidae':'Source Saurida tumbil13 and dedicated Harpadon nehereus15 establish two actual synodontid types. Dedicated Bombay duck takes precedence for identified Harpadon despite its duplicate13 entry; family catch retains both groups.',
'Scombroidei':'Historical reporting suborder covers Scomber16, Scomberomorus/Auxis13 Trichiuridae including dedicated Trichiurus14 and gempylid Rexea18. FAO2001 places Gempylidae within historical Scombroidei and describes Rexea as meso-/benthopelagic. Pelagic predators, hairtail and this deeper predator included; billfish extensions remain source-model limitations.',
'Mola mola':'Closest represented analogue is Planktivores11: source Benthosema, anchovies and Sardinella link positively to zooplankton-feeding fish. Primary Nakamura et al.2015 confirms sunfish foraging on siphonophores; its large oceanic body/deep excursions and gelatinous specialization are poorly represented. Mixed Planktivores/piscivores17 is an alternative but emphasizes fish predators; Other invertebrates7 is its prey, not a fish compartment. Very low ecological analogue, not an author member.',
'Scaridae':'Closest represented analogue is Omnivores19: source coastal generalist Acanthopagrus and mixed benthic/plant-animal feeding offer a weak practical connection. FAO2002 Western Central Atlantic Scaridae family diagnosis documents reef grazing on algal/bacterial mats, seagrass and some coral/invertebrates. Reef scraping and obligate grazing differ strongly from the shelf guild. Benthivores12 emphasizes animal benthos; Planktivores11 is pelagic. Very low analogue; no author parrotfish membership is claimed.',
'Psenopsis anomala':'S1 explicitly includes Psenopsis anomala in both Planktivores/Benthivores16 and Planktivores/piscivores17. Membership in the author union is High. The historical equal50/50 assumption is recorded separately; current allocation uses complete M2018 source biomass underW9, not observed stage/species catch proportions.',
'Decapoda':'Source Crabs8 and Shrimps9 contain actual decapod species. BenthicCrustaceans5 is Gammaridea/Cumacea rather than decapods. The residual Decapoda composition is unknown: separate Dendrobranchiata/Brachyura reporting does not prove reptant dominance or any lower bound on crab share. Reviewed8/9 is an inferred crustacean mixture, with published2018whole-guild catch proportions as an assumption.',
'Clupeidae':'S1Sardinella aurita supports the clupeid plankton-feeding representative inference toPlanktivores11. Regional herring/sardine labels give compatible ecology. Ilisha belongs to modernPristigasteridae and sourceOmnivores19; historical family concepts remain a reporting-scope limitation. Its separately reported catch does not prove exclusion from a broader historical family record. One-guild inference remainsMedium, not exhaustive author membership.',
'Pennahia argentata':'S1 explicitly lists Pennahia argentata in Piscivores13 and Pennahia argentatus in Benthivores/piscivores18. WoRMS recognizes Pennahia argentata; the masculine epithet in S1 does not establish a distinct second species. Both named memberships are retained as an ambiguous author union, unlike dedicated Harpadon15 which the main methods explicitly separate. Biomass weighting is an assumption, not a measured species fraction.'}
very={'Gadus macrocephalus','Gadus chalcogrammus','Gadidae','Oncorhynchus','Salmonidae','Planiliza haematocheilus','Mugil cephalus','Mugilidae','Chanos chanos','Kyphosidae','Gastropoda','Haliotidae','Haliotis','Turbo cornutus','Rapana','Rhincodon typus','Mola mola','Scaridae'}
lowsharks={'Prionace glauca','Carcharhinus falciformis','Carcharhinus longimanus','Alopias','Isurus','Isurus oxyrinchus','Sphyrna','Squalidae'}
generic={'Pectinidae','Bivalvia','Ruditapes philippinarum','Magallana gigas','Anadara','Mytilus coruscus','Mactridae','Mytilidae','Meretrix lusoria','Tegillarca granosa','Veneridae','Meretrix','Ostreidae','Cardiidae','Mizuhopecten yessoensis','Pinctada','Scyphozoa','Rhopilema esculentum','Nemopilema nomurai','Rhopilema hispidum'}
audit=[];alloc=[];changes=[]
s4=[[c.text.strip()for c in r.cells]for r in dd.tables[6].rows];end=next(r for r in s4 if r[0]=='2018');sourcecatch={int(s4[1][j]):float(end[j])for j in range(1,len(end)-1)if s4[2][j]=='6'}
save('source_2018_catch_proxy.json',{'source':'SupplementTableS4, tables[6], final2018row; Poolcode row1/Type row2','caption':'Time series data of M1997; absolute biomass1, fishing mortality4 and absolute catch6; t/km²','absolute_catch_2018_t_km2':sourcecatch,'genuine_zero_verified':False,'censored_zero_group20':'0.00 is published at two decimals; not proof of an exact zero. Any candidate set containing20 cannot use it as a genuine observed zero.','applicability':'Same article, named guilds, year2018 and CFSY catch lineage overlap selected static2018/2019 survey. Retained as source-catch composition proxy only, not native M2018 catch export. S4 group20biomass0.01 differs from Table1staticB0.0339; others broadly match at displayed precision. Native static catch values and exact baseline identity remain unavailable.'})
for t,rr in old.items():
 original=rr[0];ev=original['evidence'];oldnames=[r['group']for r in rr];ns=[names[i]for i in sets[t]]if t in sets else oldnames
 if any(n is None for n in ns):raise ValueError(t)
 reasoning=reasons.get(t,original['explanation'])
 if len(ns)>1 and t not in reasons:reasoning=' '.join(x for x in re.split(r'(?<=[.!?])\s+',reasoning)if not any(k in x.lower()for k in ['catch composition','catch-composition','weights','apportioned']))
 if t in very:mr='M11';mc='Very low'
 elif t in lowsharks:mr='M6';mc='Low';reasoning+=' Source Scoliodon laticaudus is a small coastal sharpnose shark; the reported oceanic, deep-water or different-size shark type only partly fits this pool. The mixed ray-bearing Benthivores12 is less suitable than the actual shark compartment22; no claim of exhaustive shark membership.'
 elif t in ['Scyllaridae','Panulirus','Panulirus longipes','Ibacus ciliatus']:mr='M12';mc='Medium';reasoning+=' Li&Zhang2012 retained publisher supplement A1.8 explicitly places lobsters in the older ECS Crabs group with Portunus/Charybdis, also focal Crabs8 representatives. Compatible coastal large reptant decapod grouping supports transfer1970s/2000s→2018. This older-source assumption is not focal author membership and imports neither weights nor coefficients; benthic Crustaceans5 is small Gammaridea/Cumacea and Shrimps9 is natant shrimp.'
 elif t in ['Marine fishes not identified','Marine finfishes not identified','Marine pelagic fishes not identified','Mollusca','Miscellaneous marine crustaceans','Miscellaneous aquatic invertebrates','Perciformes','Chondrichthyes']:mr='M10';mc='Very low'
 elif len(ns)>1:
  mr='M1'if t in ['Psenopsis anomala','Pennahia argentata']else ('M6'if t=='Gadiformes'else 'M9');mc='High'if t in ['Psenopsis anomala','Pennahia argentata']else ('Low'if t=='Gadiformes'else 'Medium')
 elif t in generic:mr='M3';mc='High'
 elif ev in ['explicit_member','synonym']:mr='M2'if ev=='synonym'else 'M1';mc='High'
 elif ev=='taxonomic_containment':mr='M4';mc='Medium';reasoning+=' S1 names representatives rather than all members of this genus/family/class. Extension to this exact reporting label is an explicit taxonomic/ecological assumption; the old High containment inference is not retained.'
 elif original['confidence']=='low':mr='M6';mc='Low'
 else:mr='M5';mc='Medium'
 if t=='Chondrichthyes':reasoning+=' Unlike Elasmobranchii (sharks/rays/skates), Chondrichthyes also includes chimaeras, absent from S1. Sharks22 and ray-bearing12 are a weak approximation; mixed12 includes bony fish. No claim that chimaeras are elasmobranchs.'
 if t in very and t not in ['Mola mola','Scaridae']:
  reasoning+=' Closest positive link is '+ ('the benthic shelled-mollusc compartment4, explicitly Bivalves; gastropod grazing/predation is missing. Cephalopods10 represents active nekton predators and is less suitable.'if t in {'Gastropoda','Haliotidae','Haliotis','Turbo cornutus','Rapana'} else 'the source group feeding/habitat representatives named above, but the reported grazing, northern-water or filter-feeding type is poorly represented. Competing plankton/benthos/predator guilds do not supply its missing operative habitat or feeding type.')+' This is a Very low analogue, not explicit source membership.'
 if len(ns)>1:
  ids=[int(groups[n]['seq'])for n in ns];cvals=[sourcecatch.get(i)for i in ids];usable=all(v is not None and v>0 for v in cvals)
  bvals=[float(groups[n]['biomass'])for n in ns];vals=cvals if usable else bvals;den=sum(vals);ww=[v/den for v in vals];ar='W4'if usable else 'W9';ac='Medium'
  common='The canonical export0 placeholders become catch in ModelData; no source establishes them as observed zeros. Static M2018 catch export remains unavailable. Whole-guild composition is not observed taxon caught-mass composition; proportions fixed across1950–2019, fleets, landings/discards and reporting mixtures.'
  allocation=('Complete positive 2018 absolute-catch Type6 values from source S4 (t/km²), same article/guild/CFSY lineage and overlapping year, are used as a Medium source-catch composition proxy. S4 calibrates M1997 Ecosim; this is not an exact native M2018 catch vector, and2018calibration/static biomass differs for group20. No candidate zero is used. 'if usable else 'Source S4 2018 Type6 catch is incomplete for this candidate set or contains an unverified rounded zero. Complete M2018 Table1 biomass (t/km²) is the approved fallback under the composition/catchability and common-area assumption. ')+common
  alloc.append({'taxon':t,'candidate_ids':ids,'candidate_names':ns,'source_S4_catch_values_t_km2':cvals,'canonical_export_zero_values':[0]*len(ns),'source_catch_complete_positive':usable,'fallback_trigger':None if usable else 'Missing S4 candidate catch or rounded/censored zero; unverified canonical export0 does not fill missing observations','biomass_values_t_km2':bvals,'numerical_values_used':vals,'total_value':den,'weights':ww,'rule':ar,'confidence':ac,'assumptions':allocation})
 else:ww=[1.0];ar='W1';ac='High';allocation='One reviewed source group,100%; no numerical split. Membership uncertainty is retained.'
 rank={'High':0,'Medium':1,'Low':2,'Very low':3,'Unresolved':4};overall=max([mc,ac],key=lambda x:rank[x])
 p=classic.get(t,{});cv=float(catch[t][2019]or 0);coef=p.get('sppr');pp=0.0 if cv==0 else (cv*float(coef)/9 if coef is not None else None)
 display='; '.join(n+f' ({v:.8%})'for n,v in zip(ns,ww))
 full=f'Membership: {mr} {mc}. {reasoning} Allocation: {ar} {ac}. {allocation} Overall confidence is the weaker component.'
 rec={'taxon':t,'tl':p.get('tl'),'catch_tonnes':cv,'simple_chain_ppr_tC':pp,'classic_sppr':coef,'mapped_groups':ns,'weights':ww,'mapping_display':display,'membership_rule':mr,'membership_confidence':mc,'allocation_rule':ar,'allocation_confidence':ac,'overall_confidence':overall,'reason':full,'sources':['Xu2022_S1','Xu2022_Table1','allocation','audit']+(['sunfish']if t=='Mola mola'else ['scarid']if t=='Scaridae'else ['synonyms']if ev=='synonym'else ['provider']if t in sets else []),'previous_rows':rr}
 audit.append(rec)
 newrows=[{'model_id':MID,'taxon':t,'group':n,'weight':v,'confidence':overall.lower().replace(' ','_'),'evidence':mr+';'+ar,'explanation':full}for n,v in zip(ns,ww)]
 changes.append({'key':{'model_id':MID,'taxon':t},'expected_old':rr,'new':newrows,'kind':'membership/allocation change'if ns!=oldnames or any(abs(v-r['weight'])>1e-12 for v,r in zip(ww,rr))else 'confidence/evidence review'})
audit.sort(key=lambda r:(-(r['simple_chain_ppr_tC']if r['simple_chain_ppr_tC']is not None else -math.inf),r['taxon']))
save('taxon_audit.json',audit);save('allocation_evidence.json',{'source_model':MID,'catch_missingness_verified':True,'source_biomass':params,'records':alloc});save('mapping_changes.json',changes)
totc=sum(r['catch_tonnes']for r in audit);totp=sum(r['simple_chain_ppr_tC']or 0 for r in audit)
def summarize(field,conf=None):
 out=[]
 for k in sorted({r[field]for r in audit}):
  aa=[r for r in audit if r[field]==k];out.append({'rule':k,'confidence':aa[0][conf]if conf else k,'label':k,'taxa':len(aa),'catch_percentage':100*sum(x['catch_tonnes']for x in aa)/totc,'ppr_percentage':100*sum(x['simple_chain_ppr_tC']or 0 for x in aa)/totp})
 return out
cs=summarize('overall_confidence');order=['High','Medium','Low','Very low','Unresolved'];cs=sorted(cs,key=lambda x:order.index(x['label']))
for k in order:
 if k not in [x['label']for x in cs]:cs.append({'label':k,'taxa':0,'catch_percentage':0,'ppr_percentage':0})
save('coverage_summary.json',{'taxa':len(audit),'reference_year':2019,'basis':'landings','total_landings_t':totc,'total_simple_chain_ppr_tC':totp,'positive_catch_missing_classic':[r['taxon']for r in audit if r['catch_tonnes']>0 and r['classic_sppr']is None],'zero_catch_missing_classic':[r['taxon']for r in audit if r['catch_tonnes']==0 and r['classic_sppr']is None],'confidence_summary':cs,'membership_summary':summarize('membership_rule','membership_confidence'),'allocation_summary':summarize('allocation_rule','allocation_confidence'),'classic_independent_identity':'Saved classic taxon coefficient ×2019landings÷9. Exactly one carbon conversion; not model TL orGE.'})
print('REVIEW',len(audit),totc,totp,'splits',len(alloc),'Table1mismatch',len([x for x in cells if not x['matches']]))

