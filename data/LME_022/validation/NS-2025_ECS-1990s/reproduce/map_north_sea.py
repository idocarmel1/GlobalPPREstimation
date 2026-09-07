"""Explicit source membership first; scope-specific catch mapping decisions."""
from pathlib import Path
import csv,json,re,shutil,subprocess,sys
from collections import defaultdict,Counter
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/run_sppr.py').is_file() and (p/'PPRAtlas/archive').is_dir())
BASE=ROOT/'data/LME_022/validation/NS-2025_ECS-1990s'
EVAL=BASE/'evaluation';STEM='22_20251990_East_Coast_of_Scotland_(1991-1995)'
SCRIPTS=EVAL/'skills/claude/ewe-species-to-group-mapper/scripts'
sys.path.insert(0,str(SCRIPTS));import mapping_io as mio
book=BASE/'sppr'/f'{STEM}.xlsx';dest=EVAL/'PPREstimation/output/top10'/book.name
shutil.copy2(book,dest)
subprocess.run([sys.executable,'-X','utf8',str(SCRIPTS/'prepare_mapping.py'),'LME_022','--root',str(EVAL)],check=True)
mdir=EVAL/'data/LME_022/mapping'
shutil.copy2(BASE/f'{STEM}.members.csv',mdir/f'{STEM}.members.csv')
extract=BASE/'extraction/20251990_East_Coast_of_Scotland_1991-1995'
shutil.copy2(extract/'taxonomy.csv',mdir/f'{STEM}.taxonomy.csv')
members=list(csv.DictReader((mdir/f'{STEM}.members.csv').open(encoding='utf-8')))
explicit=defaultdict(set);genus=defaultdict(set)
for row in members:
    t=row['printed_name'];g=row['group_name'];explicit[t].add(g)
    if re.match(r'^[A-Z][a-z]+ [a-z]',t):genus[t.split()[0]].add(g)
groups=mio.read_groups(dest);known={r['group_name'] for r in groups}
rows=mio.read_mapping_csv(mdir/f'{STEM}.csv')
def assign(row,gs,confidence,evidence,why):
    gs=list(dict.fromkeys(gs));assert set(gs)<=known,(row['taxon'],gs)
    row.update(group=' | '.join(gs),weights='',confidence=confidence,evidence='composite_split' if len(gs)>1 else evidence,explanation=why)
def unresolved(row,why):row.update(group='Unresolved',weights='',confidence='unresolved',evidence='none',explanation=why)
family={
 'Ammodytidae':['Small pelagics'],'Triglidae':['Large Dem. fish'],'Lophiidae':['Monkfish'],
 'Pleuronectidae':['Flatfishes'],'Soleidae':['Flatfishes'],'Bothidae':['Flatfishes'],
 'Pleuronectiformes':['Flatfishes','Turbot'],'Scophthalmidae':['Flatfishes','Turbot'],
 'Clupeidae':['Herring','Small pelagics'],'Clupeiformes':['Herring','Small pelagics'],
 'Gadidae':['Cod','Haddock','Whiting','Saithe','Large Dem. fish','Small pelagics','Large Pelagics'],
 'Gadiformes':['Cod','Ling','Haddock','Whiting','Hake','Saithe','Large Dem. fish','Small pelagics','Large Pelagics'],
 'Merlucciidae':['Hake'],'Sebastidae':['Large Dem. fish'],'Scorpaenidae':['Large Dem. fish'],
 'Scorpaeniformes':['Large Dem. fish'],'Anarhichadidae':['Large Dem. fish'],
 'Carangidae':['Large Pelagics'],'Mullidae':['Large Dem. fish'],'Caproidae':['Large Dem. fish'],
 'Scombridae':['Large Pelagics'],
}
infauna={'Ensis','Solen','Phaxas','Gari','Cochlodesma','Myrtea','Thyasira','Mya','Spisula','Mercenaria','Chamelea','Ruditapes','Venerupis','Polititapes','Arctica','Donax','Callista','Venus','Glycymeris','Veneridae','Mactridae','Polychaeta'}
epifauna={'Buccinum','Buccinidae','Littorina','Mytilus','Mytilidae','Modiolus','Pecten','Pectinidae','Aequipecten','Chlamys','Mimachlamys','Ostrea','Ostreidae','Crassostrea','Magallana','Cerastoderma','Cardiidae','Acanthocardia','Haliotis','Murex','Patella','Gastropoda'}
outside={'Coryphaenoides','Macrouridae','Macrourus','Alepocephalus','Beryx','Berycidae','Trachichthyidae','Epigonus','Mora','Moridae','Aphanopus','Lepidopus','Trichiurus','Trichiuridae','Thunnus','Auxis','Euthynnus','Sarda','Katsuwonus','Xiphias','Istiophorus','Mola','Brama','Bramidae','Centrolophus','Trachipterus','Anguilla','Salmo','Salmonidae','Osmerus','Coregonus','Perca','Esox','Sander','Rutilus','Cyprinus','Cyprinidae','Tinca','Lota','Scardinius','Carassius','Leuciscus','Hypophthalmichthys','Acipenser','Acipenseridae','Salvelinus','Petromyzontidae','Chimaera','Chimaeriformes','Hydrolagus','Rhinochimaera','Chondrichthyes','Miscellaneous diadromous fishes'}
for r in rows:
    t=r['taxon'];first=t.split()[0];fg=r.get('functional_group','')
    if t in explicit:
        assign(r,sorted(explicit[t]),'high','explicit_member',f'Table S2 explicitly lists {t} in this model group; source membership overrides the SAU habitat-size class.')
    elif ' ' not in t and first in genus:
        assign(r,sorted(genus[first]),'medium','taxonomic_containment',f'Table S2 lists members of genus {first} in these group(s); genus-level catch is assigned to their documented group union.')
    elif first in outside or t in outside:
        unresolved(r,'Table S2 has no corresponding deep-ocean, tuna/billfish, chimaera, freshwater or diadromous compartment for this taxon; extending the East Coast of Scotland model to it is unsupported.')
    elif t in ['Marine fishes not identified','Marine finfishes not identified','Marine groundfishes not identified','Osteichthyes']:
        assign(r,['Flatfishes','Monkfish','Large Dem. fish'],'low','composite_split','Analyst inference: SAU medium demersal unidentified catch spans the model\'s multi-species demersal pools (Table S2). Species-specific commercial stocks are excluded under the coarse-taxon workflow. This broad, unobserved composition is a major uncertainty; fixed weights use identified catch in these pools.')
    elif t=='Marine pelagic fishes not identified':
        assign(r,['Small pelagics','Large Pelagics'],'medium','composite_split','SAU medium pelagic unidentified catch spans the two multi-species pelagic pools in Table S2; the named single-stock Herring group is excluded. Fixed weights use identified catch.')
    elif t=='Perciformes':
        assign(r,['Large Dem. fish'],'medium','habitat_size_guild','SAU medium demersal perch-like catch corresponds to the Table S2 residual pool containing wolffish, gurnards and red mullet; this is analyst inference, not a listed member.')
    elif t in family:
        gs=family[t];assign(r,gs,'medium' if len(gs)>1 or t=='Scombridae' else 'high','taxonomic_containment','Taxonomic containment of the Table S2 named members determines the candidate group(s). '+('This Scombridae assignment represents the local mackerel component; separately identified tuna catch remains unresolved.' if t=='Scombridae' else 'Fixed composition weights are used when multiple documented groups occur.'))
    elif fg=='Cephalopods':
        assign(r,['Squid & Octopus'],'high','taxonomic_containment','SAU identifies this catch as cephalopods; Table S2 pools squid, octopus and cuttlefish in Squid & Octopus.')
    elif fg in ['Shrimps','Lobsters, crabs']:
        assign(r,['Crustacea'],'high','taxonomic_containment','SAU identifies shrimp or lobster/crab catch; Table S2 Crustacea includes shrimp, lobster and crab taxa without a finer model split.')
    elif 'sharks' in fg.lower() or 'rays' in fg.lower():
        assign(r,['Sharks & rays'],'medium','taxonomic_containment','SAU identifies shark or ray catch and Table S2 has a pooled Sharks & rays group; extension beyond the listed species is explicit analyst inference.')
    elif 'flatfish' in fg.lower():
        assign(r,['Flatfishes'],'medium','taxonomic_containment','SAU identifies a flatfish taxon; the model has a broad Flatfishes pool, with separately reported turbot retained in Turbot. This taxon is not explicitly named in Table S2.')
    elif first in infauna or t in infauna:
        assign(r,['Infauna'],'medium','habitat_size_guild','Analyst inference from burrowing bivalve or polychaete identity: Table S2 Infauna explicitly comprises these organisms. Some named clam categories also occur in Epifauna, so this inferred extension requires review.')
    elif first in epifauna or t in epifauna:
        assign(r,['Epifauna'],'medium','taxonomic_containment','Table S2 Epifauna explicitly includes mussels, oysters, scallops, cockles, periwinkles and whelks; this catch label belongs to those source-defined categories.')
    elif t in ['Bivalvia','Mollusca','Miscellaneous aquatic invertebrates']:
        assign(r,['Infauna','Epifauna'],'medium','composite_split','The SAU demersal-invertebrate category spans burrowing and surface benthos represented by Table S2 Infauna and Epifauna; fixed weights derive from identified benthic catch.')
    elif fg=='Other demersal invertebrates':
        assign(r,['Epifauna'],'low','habitat_size_guild','Analyst inference: benthic epifaunal catch is represented by the Epifauna compartment name; Table S2 does not list this organism, so its detailed trophic placement remains weakly supported.')
    elif fg=='Krill':
        assign(r,['Large zooplankton'],'medium','habitat_size_guild','SAU identifies krill; the source defines Large zooplankton as zooplankton over 2 mm. Assignment is a size/habitat inference.')
    elif first in genus:
        gs=sorted(genus[first]);assign(r,gs,'medium','analogue',f'Table S2 places congeneric {first} species in these group(s). This unlisted species is an explicit congeneric extension, not source membership.')
    elif fg in ['Small pelagics (<30 cm)','Medium pelagics (30 - 89 cm)']:
        gs=['Small pelagics'] if fg.startswith('Small') else ['Large Pelagics']
        assign(r,gs,'low','habitat_size_guild','Analyst inference from SAU pelagic size/habitat class to the Table S2 pelagic pools; this species is not listed and the model lacks its own dedicated compartment.')
    elif any(x in fg.lower() for x in ['demersal','benthopelagic','reef assoc']):
        assign(r,['Large Dem. fish'],'low','habitat_size_guild','Analyst inference from SAU benthic fish habitat to the residual demersal pool containing gurnards, wolffish, sculpins and rocklings (Table S2); unlisted species and smaller fish make this a weak extension.')
    else:unresolved(r,'No source-defined compartment or adequately supported taxonomic/habitat mapping was found in the East Coast of Scotland model.')
with (mdir/f'{STEM}.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,mio.FIELDS);w.writeheader();w.writerows(rows)
dictionary=[]
for g in groups:
    n=g['group_name'];member_text='; '.join(r['printed_name'] for r in members if r['group_name']==n)
    dictionary.append(dict(group_name=n,model_tl=g.get('tl'),grouping_basis='single stock' if n in ['Turbot','Cod','Ling','Haddock','Whiting','Hake','Saithe','Herring'] else 'non-living' if n in ['Detritus','diet_import'] else 'taxonomic',explicit_members=member_text,supporting_taxa=g.get('taxon_descr') or 'algorithm-added external import pool',membership_source='Table S2' if n!='diet_import' else 'algorithm-added',source_relationship='direct source' if n!='diet_import' else 'analyst inference',source_location='Table S2, source workbook A3:C27',source_url='https://doi.org/10.3389/fmars.2025.1646031',notes='Partial North Sea footprint; only isolated computational validation.'))
with (mdir/f'{STEM}.groups.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,list(dictionary[0]));w.writeheader();w.writerows(dictionary)
notes='''# Partial-area validation: East Coast of Scotland model applied to North Sea catch

Saygu et al. (2025), doi:10.3389/fmars.2025.1646031. Model period 1991-1995; catch series is whole North Sea LME_022, 1950-2019. This is an isolated computational test, not a validated whole-LME estimate or a selected atlas model.

The grouping combines named single stocks, taxonomic pools and habitat/size pools. No spatial prefixes or life-stage split occurs. Table S2 (archived author XLSX) supplies all source membership; names and misspellings are preserved. Main PDF, XLSX Tables S1-S4 and DOCX formulas supplement were inspected. No listed supplement is missing.

The large unidentified demersal catch is assigned at LOW confidence across Flatfishes, Monkfish and Large Dem. fish, excluding single-stock commercial groups per the coarse-taxon workflow. This candidate composition is inferred and materially influences PPR. Taxon membership confirmation and arithmetic verification do not validate this assumption. Other splits follow documented group unions; weights remain constant over 1950-2019 and use identified catch.

Deep-ocean fishes, tuna/billfish, chimaeras, freshwater and diadromous catch without a source compartment remain unresolved. Extension of unlisted species uses explicit medium/low confidence. The Table S2 catch-facing distinction between burrowing clams and Epifauna's broad clam category is imperfect and remains documented in row explanations.

SPPR health: GE and With Egestion are OK; the diagnostic for the default repaired-EE TE configuration is FAIL (living spectral radius 1.11278). A finite result or successful computation is not evidence of convergence. Preserve all methods, use GE for a diagnostic-tested computational reference, and exclude methods explicitly flagged by the upstream diagnostic or a negative source-group SPPR. This configuration diagnostic does not grade every TE-named solver or the Monte Carlo accepted-draw subset. The existing loader balances rounded source inputs and supplies its own unknown-value conventions; those transformed values are not extracted author measurements. All source import cells remain unchanged.
'''
(mdir/f'{STEM}.notes.md').write_text(notes,encoding='utf-8')
(BASE/'MODEL_PROFILE.md').write_text(notes,encoding='utf-8')
taxa,_=mio.read_catch(EVAL,'LME_022');total=sum(sum(v['by_year'].values()) for v in taxa.values())
coverage=defaultdict(float)
for r in rows:coverage[r['confidence']]+=sum(taxa[r['taxon']]['by_year'].values())
(BASE/'mapping_summary.json').write_text(json.dumps({'taxa_by_confidence':dict(Counter(r['confidence'] for r in rows)),'catch_total':total,'catch_by_confidence':dict(coverage),'mapped_pct':100*(1-coverage['unresolved']/total)},indent=2),encoding='utf-8')
print('MAPPING',len(rows),dict(Counter(r['confidence'] for r in rows)),100*(1-coverage['unresolved']/total))
