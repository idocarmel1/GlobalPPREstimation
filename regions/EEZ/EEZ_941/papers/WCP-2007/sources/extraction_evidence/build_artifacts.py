"""Build imports, preserve converter output, restore source-faithful canonical JSON."""
from pathlib import Path
import json, subprocess, sys, csv, shutil, hashlib
from decimal import Decimal
import openpyxl
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction')
TAX={
'Swordfish':'Large Xiphias gladius.',
'Other Billfish':'Large Istiophorus platypterus; Makaira indica; Makaira mazara; Tetrapturus audax; Tetrapturus angustirostris.',
'Blue Shark':'Large Prionace glauca.',
'Other Sharks':'Large Alopiidae; Carcharhinidae; Lamnidae; Sphyrnidae.',
'BET':'Thunnus obesus larger than maturity class 124 cm / 3.85 y (46.2 months) / 43 kg.',
'YFT':'Thunnus albacares larger than maturity class 120 cm / 2.25 y (27 months) / 33 kg.',
'SKJ':'Katsuwonus pelamis larger than 100% maturity class 43 cm / 0.75 y (9 months) / 1.6 kg.',
'Piscivorous fish':'Alepisauridae; Bramidae; Carangidae; Coryphaenidae; Gempylidae; wahoo Acanthocybium solandri; opah Lampris guttatus; small Scombridae.',
'Small Billfish':'Small billfish, same species as large groups Swordfish and Other Billfish.',
'Small Sharks':'Small sharks, same species as large groups Blue Shark and Other Sharks.',
'Small BET':'Thunnus obesus smaller than maturity class 124 cm / 3.85 y (46.2 months) / 43 kg and larger than 20 cm / 3 months / 0.18 kg.',
'Small YFT':'Thunnus albacares smaller than maturity class 120 cm / 2.25 y (27 months) / 33 kg and larger than 24 cm / 3 months / 0.33 kg.',
'Small SKJ':'Katsuwonus pelamis smaller than 100% maturity class 43 cm / 0.75 y (9 months) / 1.6 kg and larger than 24 cm / 3 months / 0.25 kg.',
'baby SKJ':'Katsuwonus pelamis from hatching to recruitment: 0-3 months, smaller than 24 cm / 0.25 kg. Table 1 definition; p15 alternatively describes less than 10 cm. Conflict retained, Table 1 used.',
'Epi forage':'Initial aggregate: Euphausids; shrimps; Stomatopoda; Decapoda; Amphipoda; Hyperiidae; Phronima; Megalopa; Palinuridae; Scyllaridae; Engraulidae; Clupeidae; Exocoetidae; small Carangidae, Bramidae, Scombridae; juveniles of reef fish Acanthuridae, Balistidae, Chaetodontidae, Diodontidae, Holocentridae, Kyphosidae, Lethrinidae, Malacanthidae, Monacanthidae, Nomeidae, Ostraciidae, Pomacanthidae, Priacanthidae, Scaridae; Argonautidae; Carinariidae; Cavoliniidae; Loliginidae; Eucleoteuthis luminosa; Hyaloteuthis pelagica; Moroteuthis lonnbergi; Onychoteuthidae; Sepiolidae; Thysanoteuthidae. Source list includes ellipses.',
'Epi crust':'Stomatopoda; Megalopa stage; Hyperiidea; Amphipoda; Palinura; Enoplometopidae; Phronima sp.; Thalassocaris sp.; Scyllaridae; Harpiosquillidae. Source list ends with ellipsis.',
'Epi fish':'Acanthuridae; Balistidae; Bramidae; Carangidae; Chaetodontidae; Diodontidae; Echeneidae; Engraulidae; Exocoetidae; Holocentridae; Kyphosidae; Lethrinidae; Malacanthidae; Molidae; Monacanthidae; Nomeidae; Ostraciidae; Pomacanthidae; Priacanthidae; Scaridae; Scombridae; Serranidae; Tetraodontidae; Zanclidae. Source list ends with ellipsis.',
'Epi small fish':'Larval and juvenile stages of the Epipelagic fish species.',
'Epi mollusc':'Argonautidae; Carinariidae; Cavoliniidae; Loliginidae; Eucleoteuthis luminosa; Hyaloteuthis pelagica; Moroteuthis lonnbergi; Onychoteuthidae; Sepiolidae; Thysanoteuthidae. Source list ends with ellipsis.',
'Epi small mollusc':'Larval and juvenile stages of the Epipelagic molluscs species.',
'M Meso forage':'Initial aggregate: Nemichthyidae; Myctophidae; Gempylidae; Phosichthyidae; Enoploteuthidae; Stenoteuthis; Pterygioteuthis; Heteroteuthinae. Source list ends with ellipsis.',
'M Meso fish+other':'Nemichthyidae; Myctophidae; Gempylidae; Phosichthyidae. Table 1 Migrant mesopelagic fish; Table 6 adds +other without an exhaustive definition of other. Source list ends with ellipsis.',
'M meso mollusc':'Enoploteuthidae; Stenoteuthis; Pterygioteuthis; Heteroteuthinae. Source list ends with ellipsis.',
'Meso forage':'Initial aggregate: juvenile Alepisauridae; Omosudidae; Paralepididae; Ophiididae; Trichiuridae; Caristiidae; Ostracoberycidae; Percophidae; Scombrolabracidae; Scorpaenidae; Argyropelecus; Triacanthidae; Macrurocyttidae; Octopoteuthidae; Ommastrephidae; Moroteuthis; Ancistrocheirus; Amphitretidae. Source list ends with ellipsis.',
'Meso fish + other':'Juvenile Alepisauridae; Omosudidae; Paralepididae; Ophiididae; Trichiuridae; Caristiidae; Ostracoberycidae; Percophidae; Scombrolabracidae; Scorpaenidae; Argyropelecus; Triacanthidae; Macrurocyttidae. Table 1 Mesopelagic fish; Table 6 adds + other without an exhaustive definition of other. Source list ends with ellipsis.',
'Meso mollusc':'Octopoteuthidae; Ommastrephidae; Moroteuthis; Ancistrocheirus; Amphitretidae. Source list ends with ellipsis.',
'HM Bathy forage':'Myctophidae; Maurolicus; Sternoptyx; Liocranchia; Caridae; Oplophorus; Sergestidae; Euphausiidae. Highly migrant bathypelagic forage; source list ends with ellipsis.',
'M Bathy forage':'Histioteuthidae; Penaeoidea; Acanthephyra. Migrant bathypelagic forage; source list ends with ellipsis.',
'Bathy forage':'Paralepididae; Scopelarchidae; Diretmidae; Chiasmodontidae; Bolitaenidae. Source list ends with ellipsis.',
'Mesozpk':'Zooplankton size class 200-2000 micrometres, mostly copepods.',
'Microzpk':'Zooplankton size class 20-200 micrometres: copepod nauplii; ciliates; sarcodinids; rotifers; small cladocerans. Source list ends with ellipsis.',
'Large phyto':'All pelagic photosynthetic organisms larger than 2-8 micrometres, mainly diatoms; autotrophic dinoflagellates; pelagophytes; prymnesiophytes.',
'Small phyto':'All pelagic photosynthetic organisms smaller than 2-8 micrometres, mainly Prochhlorococcus; Synechococcus; autotrophic eukaryotes. Source spelling retained.',
'Detritus':'All pelagic non-living material; bacterioplankton; heterotrophic pico- and nanozooplankton (<20 micrometres).'}

def run(script,args,log):
    r=subprocess.run([sys.executable,str(SKILL/'scripts'/script),*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    log.write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
    print(script,r.returncode,log.name)
    return r

raw=json.loads((HERE/'source_tables.json').read_text())
for period in ['final','initial']:
    extraction=json.loads((HERE/(period+'_extraction.json')).read_text())
    model_id=extraction['source_identity']['model_id']
    base=ROOT/'regions'/'EEZ_941'/'models'/model_id
    tables=base/'extracted_tables'; tables.mkdir(parents=True,exist_ok=True)
    run('write_outputs.py',[HERE/(period+'_extraction.json'),'--outdir',base,'--dir-name','extracted_tables'],base/'write_outputs.log')
    wb=openpyxl.Workbook(); ws=wb.active; ws.title='Taxonomy'; ws.append(['seq','group_name','taxon_descr'])
    for g in extraction['groups']: ws.append([g['n'],g['name'],TAX[g['name']]+' [Table 1, PDF p9; group names aligned to '+('Table 6' if period=='final' else 'Table 3')+'.]'])
    wb.save(tables/'Taxonomy.xlsx')
    with (tables/'taxonomy.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['seq','group_name','taxon_descr']); w.writerows(list(ws.values)[1:])
    # Blank detritus self fate is source export by sedimentation. Not self recycling.
    run('validate.py',[tables],tables/'VALIDATION.txt')
    run('massbalance_check.py',[tables],tables/'MASS_BALANCE_SOURCE.txt')
    run('database_json.py',['-d',tables,'--update-report'],tables/'DATABASE_CONVERSION.txt')
    dbs=list(tables.glob('941_*.json'))
    assert len(dbs)==1,dbs
    converted=json.loads(dbs[0].read_text())
    canonical=json.loads(json.dumps(converted))
    byseq={str(g['group_seq']):g for g in canonical['group']}
    for s in extraction['groups']:
        if str(s['n']) not in byseq:
            # Converter skips a fully blank basic-input row. Restore the documented
            # initial detritus group without inventing its absent parameters.
            assert s['name']=='Detritus'
            g={k:'-9999' for k in converted['group'][0]}
            g.update(group_name=s['name'],group_seq=str(s['n']),pp='2',taxon_descr=TAX[s['name']]+' [Table 1, PDF p9.]',pedigree_assignment_descr=None,diet_descr=None)
            byseq[str(s['n'])]=g
    canonical['group']=[byseq[str(s['n'])] for s in extraction['groups']]
    changes=[]
    for g,s in zip(canonical['group'],extraction['groups']):
        assert g['group_name']==s['name']
        # Exact source values, including output estimates, retained as decimal strings.
        for src,dst in [('biomass','biomass'),('biomass','biomass_habitat_area'),('pb','pb'),('qb','qb'),('ee','ee'),('pq','ge'),('unassim','gs'),('ba','biomass_accum'),('ba_rate','biomass_accum_rate')]:
            g[dst]=s.get(src) if s.get(src) is not None else '-9999'
        if s.get('ba_rate')=='0':
            g['biomass_accum']='0' # exact 0 * B; loader does not read the rate field
        g['habitat_area']='-9999' # whole-area densities; habitat proportion not supplied
        g['vbk']='-9999'; g['shadow_price']='-9999' # converter defaults are not source values
        if period=='final':
            for names,k in [(['BET','Small BET'],'0.3'),(['YFT','Small YFT'],'0.32'),(['SKJ','Small SKJ','baby SKJ'],'0.8')]:
                if s['name'] in names: g['vbk']=k # VBGF K, multi-stanza settings p15
        g['tl']=s.get('tl') or '-9999'
        for src,dst in [('biomass','b_hab_area_input'),('pb','pb_input'),('qb','qb_input'),('ee','ee_input')]:
            g[dst]='true' if raw['table3'][s['name']].get(src+'_'+period.title()) is not None else 'false'
        if period=='final' and s['name'] in ['Small BET','Small YFT','Small SKJ','baby SKJ']:
            g['b_hab_area_input']='false'; g['qb_input']='false' # Table 6 blue: multi-stanza outputs
        g['ge_input']='false' # Table 6 output, not independent input
        g['diet_imp']='0'
        g['detritus_import']='0' if s['name']=='Detritus' else '-9999'
        diet=extraction['diet'].get(str(s['n']),{})
        routing=extraction['detritus_fate'].get(str(s['n']),{})
        items=[]
        for prey in extraction['groups']:
            prop=diet.get(str(prey['n']))
            fate=routing.get(prey['name'])
            if prop is not None or fate is not None:
                items.append({'prey_seq':str(prey['n']),'proportion':prop or '0','detritus_fate':fate or '0'})
        g['diet_descr']={'diet':items} if items else None
        fleet=extraction['landings'].get(str(s['n']),{})
        if fleet:
            g['export']=str(sum((Decimal(v) for v in fleet.values()),Decimal(0)))
        elif raw['table5'].get(s['name'],{}).get('printed_Total')=='0':
            g['export']='0'
        else: g['export']='-9999'
    canonical['_source_provenance']={**extraction['source_identity'],'source_pdf':'../../papers/WCP-2007/download-0adcf55e.pdf','strict_source_status':'published balanced final model; rounded estimates and unknown flows retained' if period=='final' else 'explicitly unbalanced initial configuration; not admitted as balanced model', 'source_group_order':'Table 6 final row order' if period=='final' else 'Table 3 initial-active row order; source does not print group numbers','habitat_area_note':'Biomass in tons per model km2 from source. Habitat fraction unspecified; numerical loader uses biomass directly.'}
    converted_byseq={str(g['group_seq']):g for g in converted['group']}
    for g in canonical['group']:
        c=converted_byseq.get(str(g['group_seq']),{})
        for k in g:
            if c.get(k)!=g[k]: changes.append({'seq':g['group_seq'],'group':g['group_name'],'field':k,'converter':c.get(k),'canonical':g[k]})
    (base/'model.json').write_text(json.dumps(canonical,indent=2),encoding='utf-8')
    (tables/'converter_to_canonical_audit.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
    # Reconstruct canonical separately, preserving converter round trip unchanged.
    engine_path=base/(model_id+'.json')
    shutil.copyfile(base/'model.json',engine_path)
    run('database_json.py',['-j',engine_path],tables/'CANONICAL_RECONSTRUCTION.txt')
    recon=base/(model_id+'_reconstructed.xlsx')
    if recon.exists(): shutil.move(str(recon),tables/'CANONICAL_reconstructed.xlsx')
    # Engine-compatible file is an explicit exact-byte alias, not a second model.
    assert hashlib.sha256(engine_path.read_bytes()).digest()==hashlib.sha256((base/'model.json').read_bytes()).digest()
    print(model_id)
