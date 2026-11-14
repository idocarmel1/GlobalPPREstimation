"""Reproduce source-faithful extraction of official Ecosense.GOA inputs.

No Rpath balance, PPRCalculator, SPPR or regional arithmetic is performed.
Uses the maintained writer, validator, converter and reconstruction verifier.
Original recovery inputs are used if present; canonical native inputs otherwise.
"""
from pathlib import Path
from decimal import Decimal
import csv, hashlib, json, shutil, subprocess, sys, traceback
from collections import Counter

RUN = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[6]
MODEL_ID = 'Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49'
PAPER = ROOT/'regions/LME/LME_002/papers/GOA-2020'
MODEL = PAPER/'models'/MODEL_ID
SCRIPTS = ROOT/'tools/skills/paper-to-ppr/resources/extraction/scripts'
COMMIT = 'fe63f6d370d942ff1786f4d649e432fbfb85f81b'
RAW = 'https://raw.githubusercontent.com/NOAA-EDAB/Rpath/'+COMMIT+'/'
PDF = 'https://repository.library.noaa.gov/view/noaa/30747/noaa_30747_DS1.pdf'
CITATION = ('Whitehouse, G.A. and Aydin, K.Y. (2020). Assessing the sensitivity of three Alaska '
            'marine food webs to perturbations: an example of Ecosim simulations using Rpath. '
            'Ecological Modelling 429, 109074. https://doi.org/10.1016/j.ecolmodel.2020.109074')
SOURCE_PATHS = {
 'Ecosense_GOA_base.csv':'data-raw/Ecosense_GOA_base.csv',
 'Ecosense_GOA_diet.csv':'data-raw/Ecosense_GOA_diet.csv',
 'Ecosense_GOA_pedigree.csv':'data-raw/Ecosense_GOA_pedigree.csv',
 'Ecosense.GOA.rda':'data/Ecosense.GOA.rda',
 'Ecosense.GOA.Rd':'man/Ecosense.GOA.Rd',
 'Rpath_README.md':'README.md','Rpath_data.R':'R/data.R',
 'Rpath_param.R':'R/param.R','Rpath_ecopath.R':'R/ecopath.R',
 'Rpath_write_functions.R':'R/write_functions.R',
 'Rpath_unbalanced_data.R':'data-raw/Rpath_unbalanced_data.R',
}
ALIAS = {'Urchins, dollars, cucumbers':'Urchins dollars cucumbers'}
FIELDS = {'Biomass':'biomass','PB':'pb','QB':'qb','EE':'ee','ProdCons':'pq',
          'BioAcc':'ba','Unassim':'unassim','DetInput':'detritus_import'}
CANON = {'Biomass':'biomass','PB':'pb','QB':'qb','EE':'ee','ProdCons':'ge',
         'BioAcc':'biomass_accum','Unassim':'gs','DetInput':'detritus_import'}

def dump(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return [r for r in csv.reader(f) if r]
def nd(x):return x if x != '' else '-9999'
def relative(path,start):
    import os
    return Path(os.path.relpath(path,start)).as_posix()
def companion(description,data):return {'description':description,'rows':data}

# Table 1 membership transcribed from NOAA's indexed PDF text, pp.5-7.
# This is contextual evidence only; uncertain original naming is not silently resolved.
MEMBERS = [
 'Transient killer whales; Sperm and beaked whales; Resident killer whales; Porpoises',
 'Gray whale','Humpbacks; Fin whales; Sei whales; Right whales; Minke whales',
 'Northern fur seal (juv); Northern fur seal; Steller sea lion (juv); Steller sea lion; Resident seals; Sea otters',
 'Shearwaters; Fulmars','Murres; Puffins','Gulls; Kittiwakes','Auklets','Storm petrels; Albatross/Jaeger','Cormorants',
 'Sleeper shark; Salmon shark; Dogfish','Walleye pollock (juv); Walleye pollock','Pacific cod (juv); Pacific cod',
 'Bathylagidae; Myctophidae; Capelin; Sandlance; Eulachon; Other managed forage; Other pelagic smelt; Pacific herring (juv); Pacific herring',
 'Arrowtooth flounder (juv); Arrowtooth flounder; Pacific halibut (juv); Pacific halibut',
 'Yellowfin sole; Flathead sole (juv); Flathead sole; Southern rock sole; Northern rock sole; Alaska plaice; Dover sole; Rex sole; Miscellaneous flatfish',
 'Other skates; Longnosed skate; Big skate',
 'Sablefish (juv); Sablefish; Atka mackerel (juv); Atka mackerel; Greenlings; Pacific ocean perch (juv); Pacific ocean perch; Sharpchin rockfish; Northern rockfish; Dusky rockfish; Shortraker rockfish; Rougheye rockfish; Shortspine thornyhead (juv); Shortspine thornyhead; Other Sebastes; Grenadiers; Miscellaneous fish deep',
 'Eelpouts','Large sculpins','Other sculpins','Misc. fish shallow','Octopi','Squids','Salmon returning','Salmon outgoing',
 'Bairdi; King Crab; Hermit crabs; Miscellaneous crabs','Pandalidae; NP shrimp','Sea stars','Brittle stars',
 'Urchins dollars cucumbers','Snails','Miscellaneous crustaceans','Benthic amphipods','Anemones','Corals; Sea Pens',
 'Miscellaneous worms; Hydroids','Urochordata','Sponges','Bivalves','Polychaetes','Scyphozoid Jellies',
 'Fish Larvae; Chaetognaths; Euphausiids; Mysids; Pelagic amphipods; Gelatinous filter feeders; Pteropods','Copepods',
 'Pelagic microbes','Benthic microbes','Macroalgae; Large phytoplankton; Small phytoplankton; Outside production',
 'Pelagic detritus; Discards; Outside detritus','Benthic detritus; Offal',
 'Halibut longline; Crab pots; Herring fishery; Salmon fishery; Indigenous and subsistence; Flatfish trawl; Other groundfish trawl; Cod longline; Cod pots; Cod trawl; Pollock trawl; Rockfish trawl; Sablefish longline; Shrimp trawl'
]

def main():
    qa=RUN/'qa'; qa.mkdir(exist_ok=True)
    recovery=RUN/'inputs/recovery'
    native=MODEL/'inputs/native';native.mkdir(parents=True,exist_ok=True)
    provenance=[]
    for filename,remote in SOURCE_PATHS.items():
        src=recovery/filename if (recovery/filename).exists() else native/filename
        if src.resolve()!= (native/filename).resolve():shutil.copy2(src,native/filename)
        target=native/filename
        assert target.read_bytes()[:43] != b'version https://git-lfs.github.com/spec/v1'
        provenance.append({'path':'native/'+filename,'sha256':sha(target),'bytes':target.stat().st_size,
          'verification':'full_bytes','source_url':RAW+remote,'repository_path':remote,'commit':COMMIT,
          'role':'native_numeric_input' if filename.endswith('.csv') else 'native_object' if filename.endswith('.rda') else 'source_code_or_documentation',
          'acquisition_date':'2026-11-14'})
    base=rows(native/'Ecosense_GOA_base.csv');dietrows=rows(native/'Ecosense_GOA_diet.csv');ped=rows(native/'Ecosense_GOA_pedigree.csv')
    records=[dict(zip(base[0],r)) for r in base[1:]]
    biological=[r for r in records if r['Type']!='3'];fleetrows=[r for r in records if r['Type']=='3']
    assert len(biological)==49 and len(fleetrows)==1 and len(MEMBERS)==50
    names=[r['Group'] for r in biological];importnames=[ALIAS.get(n,n) for n in names]
    assert len(set(names))==len(set(importnames))==49
    assert dietrows[0][1:]==names[:47]
    assert [r[0] for r in dietrows[1:]]==names+['Import']
    fleet=fleetrows[0]['Group'];dets=[r['Group'] for r in biological if r['Type']=='2']
    groups=[]
    for i,r in enumerate(biological,1):
        g={'n':i,'name':ALIAS.get(r['Group'],r['Group']),
           'parameter_roles':{FIELDS[k]:'source_native_input' for k in FIELDS if r[k]!=''}}
        for k,v in FIELDS.items():g[v]=r[k] or None
        groups.append(g)
    type0=[i for i,r in enumerate(biological,1) if r['Type']=='0']
    companions={
      'Rpath_parameter_model_native.csv':companion('Exact native parameter table including fleet row and native NA/zero masks; B t/km^2; PB/QB year^-1; BioAcc/catch/DetInput t/km^2/year; rates/fates dimensionless. Source data-raw/Ecosense_GOA_base.csv.',base),
      'Rpath_parameter_model.csv':companion('Native table with all original fields plus exact destination-name aliases for PelDetFate and BenthDetFate. Duplicate routing columns support ModelData fleet routing; no source value changes. Units and source as native companion.',[base[0]+dets]+[r+[r[10],r[11]] for r in base[1:]]),
      'Rpath_diet_native.csv':companion('Complete native prey-by-consumer diet table, dimensionless proportions; includes Primary production column and Import row; blank remains blank. Source data-raw/Ecosense_GOA_diet.csv.',dietrows),
      'Rpath_pedigree_native.csv':companion('Complete native Rpath pedigree/CV input table with source column labels and blanks preserved. Source data-raw/Ecosense_GOA_pedigree.csv; not reclassified as original 1-8 pedigree grades.',ped),
      'Group_label_crosswalk.csv':companion('Reversible representation-only import alias, authorized in this extraction. Native/canonical labels remain exact; no scientific correction.',[['group_id','native_and_canonical_label','standard_import_label','reason']]+[[str(i),n,importnames[i-1],'comma forbidden in strict import cells' if n in ALIAS else 'unchanged'] for i,n in enumerate(names,1)]),
      'Aggregation_membership_Table1.csv':companion('2020 article Table1 pp.5-7 GOA column; contextual text transcription, PDF visual verification unavailable (HTTP403/cache miss). Not used for parameter derivation; Steller adult/juvenile naming does not resolve original west/central splits.',[['rpath_row','rpath_group','native_type','original_groups_Table1','source_url','locator','verification','limitation']]+[[str(i),r['Group'],r['Type'],MEMBERS[i-1],PDF,'Table1 pp.5-7','indexed_pdf_text_only','Original names are Table1 labels; no asserted bijection to 133 Appendix C rows; original paper text says138 source groups.'] for i,r in enumerate(records,1)]),
    }
    fieldmap=[['native_field','standard_destination','canonical_destination','units','mapping_status','source_locator']]
    for k,v in FIELDS.items():fieldmap.append([k,'Basic_input.csv' if k!='BioAcc' else 'Biomass_accumulation.csv',CANON[k],'t/km^2' if k=='Biomass' else 't/km^2/year' if k in ['BioAcc','DetInput'] else 'year^-1' if k in ['PB','QB'] else 'dimensionless','exact literal/missingness', 'Ecosense_GOA_base.csv'])
    fieldmap += [
      ['F_Fishery','Landings.csv / '+fleet,'landings_by_fleet','t/km^2/year','positional mapping in native reader, one fleet','Rpath_ecopath.R landmat'],
      ['D_Fishery','Discards.csv / '+fleet,'discards_by_fleet','t/km^2/year','positional mapping in native reader, one fleet','Rpath_ecopath.R discardmat'],
      ['PelDetFate','Detritus_fate.csv / Pelagic detritus','detritus_fate_by_pool[48]','dimensionless','exact; fleet row in companion only','Ecosense_GOA_base.csv'],
      ['BenthDetFate','Detritus_fate.csv / Benthic detritus','detritus_fate_by_pool[49]','dimensionless','exact; fleet row in companion only','Ecosense_GOA_base.csv'],
      ['Type','diet consumer membership; detritus columns','pp','category 0 consumer;1 producer;2 detritus;3 fleet','49 biological groups; fleet retained companion','Ecosense_GOA_base.csv'],
      ['diet blank','blank','-9999','dimensionless','source NA preserved; native rpath() sets NA diet to0 on separate working array','Rpath_ecopath.R lines56-57'],
      ['Primary production diet column','companion only','diet_imp=0 from Import row; no feeding links','dimensionless','nonfeeding native column entirely blank except Import0','Ecosense_GOA_diet.csv'],
      ['Habitat fraction / TL / Z / other mortality / export fate','blank','-9999','various','not supplied by native parameter inputs; no defaults applied','all native CSV inputs inspected'],
    ]
    companions['Native_field_mapping.csv']=companion('Explicit units, source-field and runtime mapping; derived loader fields do not replace source inputs.',fieldmap)
    model={'metadata':{'LME':'2 Gulf of Alaska','model_number':MODEL_ID,'model_name':'Gulf of Alaska','model_year':'1990-1994','biomass_basis':'whole_model_area','ba_basis':'whole_model_area'},
      'groups':groups,'consumers':type0,'fleets':[fleet],'detritus_groups':dets,'diet_rows':49,'landings_rows':49,'discards_rows':49,
      'landings':{str(i):{fleet:r['F_Fishery']} for i,r in enumerate(biological,1)},
      'discards':{str(i):{fleet:r['D_Fishery']} for i,r in enumerate(biological,1)},
      'detritus_fate':{str(i):{dets[0]:r['PelDetFate'],dets[1]:r['BenthDetFate']} for i,r in enumerate(biological,1)},
      'diet':{str(i):{**{str(j):dietrows[j][i] or None for j in range(1,50)},'import':dietrows[50][i]} for i in type0},
      'companions':companions,'extraction_notes':['Native unbalanced Rpath parameters; no EE/B solve.','Source diet NA/zero masks preserved; native runtime replaces NA diet cells with zero in a separate array.','Group31 import-only alias is reversed in canonical group identity.']}
    writer=RUN/'outputs/aggregated_writer_input.json';dump(writer,model)
    stage=RUN/'outputs/aggregated_stage';stage.mkdir(parents=True,exist_ok=True)
    def run(script,args,log):
        proc=subprocess.run([sys.executable,str(SCRIPTS/script),*map(str,args)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',env={**__import__('os').environ,'PYTHONIOENCODING':'utf-8'})
        (qa/log).write_text(proc.stdout+'\nSTDERR\n'+proc.stderr,encoding='utf-8')
        return proc
    p=run('write_outputs.py',[writer,'--outdir',stage.parent,'--dir-name',stage.name],'aggregated_writer.log');assert p.returncode==0,p.stderr
    validation=run('validate.py',[stage],'aggregated_validation.log')
    conversion=run('database_json.py',['-d',stage],'aggregated_conversion.log');assert conversion.returncode==0,conversion.stderr
    candidates=[p for p in stage.glob('*.json') if p.name not in ['model.json','DIET_SOURCE_SUMS.json','SOURCE_FIDELITY_CHECK.json']]
    assert len(candidates)==1,candidates
    canonical=json.loads(candidates[0].read_text(encoding='utf-8'))
    # Reversible name restoration only. Embedded standard source tables stay literal.
    for g in canonical['group']:g['group_name']=names[int(g['group_seq'])-1]
    for entry in canonical['source_fidelity']['diet_sums']:entry['consumer_name']=names[int(entry['consumer_seq'])-1]
    # PP's omitted nonfeeding diet column has an explicit Import0, retained here.
    canonical['group'][46]['diet_imp']=dietrows[50][47]
    canonical['extraction_notes'] += ['Exact native group name restored via Group_label_crosswalk.csv; embedded extraction_source_tables retain import alias.',
       'Primary production explicit native Import0 retained in diet_imp; its native all-blank prey column remains in Rpath_diet_native.csv.']
    target=MODEL/'model.json';dump(target,canonical)
    extracted=MODEL/'extracted_tables';extracted.mkdir(exist_ok=True)
    evidence=extracted/'evidence';evidence.mkdir(exist_ok=True)
    sys.path.insert(0,str(SCRIPTS));from source_fidelity import STANDARD,reconstruct_source_workbook
    for filename in STANDARD:shutil.copy2(stage/filename,extracted/filename)
    shutil.copytree(stage/'companions',extracted/'companions',dirs_exist_ok=True)
    reconstruct_source_workbook(canonical,str(evidence/'reconstructed.xlsx'))
    for filename in ['DIET_SOURCE_SUMS.json','MASS_BALANCE.md','ewe_conversion.log']:
        if (stage/filename).exists():shutil.copy2(stage/filename,evidence/filename)
    for filename in ['aggregated_writer.log','aggregated_validation.log','aggregated_conversion.log']:
        shutil.copy2(qa/filename,evidence/filename)
    # Independent native-to-canonical checks, not merely converter roundtrip.
    checks=[]
    def check(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail})
    check('group_ids_and_exact_native_names',[(g['group_seq'],g['group_name']) for g in canonical['group']]==[(str(i),n) for i,n in enumerate(names,1)])
    check('unique_one_to_one_import_alias',len(set(importnames))==49 and sum(a!=b for a,b in zip(names,importnames))==1)
    for i,(g,r) in enumerate(zip(canonical['group'],biological),1):
        for source,dest in CANON.items():check(f'group{i}.{source}',g[dest]==nd(r[source]))
        check(f'group{i}.Type',g['pp']==r['Type'])
        check(f'group{i}.landings',g['landings_by_fleet'][fleet]==r['F_Fishery'])
        check(f'group{i}.discards',g['discards_by_fleet'][fleet]==r['D_Fishery'])
        check(f'group{i}.fate',g['detritus_fate_by_pool']=={'48':r['PelDetFate'],'49':r['BenthDetFate']})
        check(f'group{i}.no_fabricated_det_export',g['detritus_export']=='-9999')
        if i in type0:
            check(f'group{i}.diet_literal_and_mask',all(x['proportion']==nd(dietrows[int(x['prey_seq'])][i]) for x in g['diet_descr']['diet']))
            check(f'group{i}.import',g['diet_imp']==dietrows[50][i])
    for fname,original in [('Rpath_parameter_model_native.csv',base),('Rpath_diet_native.csv',dietrows),('Rpath_pedigree_native.csv',ped)]:
        check(fname+'.all_cells',canonical['published_companions'][fname]['rows']==original)
    check('producer_nonfeeding_import_zero',canonical['group'][46]['diet_imp']=='0' and canonical['group'][46]['diet_descr'] is None)
    for r in provenance:check('original_bytes.'+r['path'],sha(MODEL/'inputs'/r['path'])==r['sha256'])
    verification={'schema_version':1,'native_commit':COMMIT,'all_passed':all(c['passed'] for c in checks),'checks':checks,'failed':[c for c in checks if not c['passed']],
       'canonical_json_sha256':sha(target),'source_csv_missing_cells':{p:sum(c=='' for r in rows(native/p)[1:] for c in r[1:]) for p in ['Ecosense_GOA_base.csv','Ecosense_GOA_diet.csv','Ecosense_GOA_pedigree.csv']}}
    dump(evidence/'native_canonical_verification.json',verification);assert verification['all_passed'],verification['failed']
    # ModelData schema admission only; record runtime transformations separately.
    sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
    loader={'schema_version':1,'scope':'ModelData constructor only; no PPRCalculator, rpath balance, SPPR, diagnostics or regional arithmetic','canonical_sha256':sha(target),'source_values_modified':False}
    try:
        from ModelData import ModelData
        import contextlib,io
        buffer=io.StringIO()
        with contextlib.redirect_stdout(buffer),contextlib.redirect_stderr(buffer):loaded=ModelData(str(target))
        loader.update({'admitted':True,'real_groups':49,'loaded_groups':len(loaded.groups_data),'DC_shape':list(loaded.DC.shape),'det_fate_shape':list(loaded.det_fate.shape),'discard_returns':loaded.discard_returns_metadata,'runtime_log':buffer.getvalue(),'runtime_group_columns':list(loaded.groups_data.columns)})
        loader['runtime_missing_counts']={str(k):int(v) for k,v in loaded.groups_data.isna().sum().items()}
        loader['runtime_transformations']=['Synthetic diet_import group appended by ModelData.','Source unknown -9999 becomes runtime NaN.','Loader computes supported accounting fields from native parameters; no unknown EE is solved.','Fleet discard returns use exact native amounts and routing; source catch remains unchanged.','Nonfeeding diet representation is loader-specific; source producer column remains in native companion.']
        loaded.groups_data.to_csv(evidence/'loader_parameter_view.csv',index=True)
    except Exception as error:loader.update({'admitted':False,'error':str(error),'traceback':traceback.format_exc()})
    dump(evidence/'loader_schema_check.json',loader)
    prov={'schema_version':1,'model_id':MODEL_ID,'paper_id':'GOA-2020','citation':CITATION,'model_variant':'official NOAA-EDAB/Rpath Ecosense.GOA unbalanced parameter inputs','source_commit':COMMIT,'biological_groups':49,'consumers':46,'producers':1,'detritus':2,'fleets':1,'modeled_period':'1990-1994','period_evidence':'1990s in Ecosense.GOA.Rd; exact1990-1994 inherited Aydin2007 base model, not2020 publication year','area_km2':291840,'area_evidence':'Whitehouse&Aydin2020 section2.2.3 p4','files':provenance,'native_object_decode':'RDA archived as exact original bytes; not independently decoded; numerical extraction uses the three original CSV files identified by Rpath_unbalanced_data.R','article_access':'NOAA web-indexed full text read; local PDF download403 and screenshot cache miss; no local PDF falsely asserted','runtime_semantics':'Rpath_ecopath.R converts NA diet to0 in a separate matrix; extraction preserves raw missingness; EE and DET B remain unsolved.'}
    dump(MODEL/'inputs/provenance.json',prov)
    sums=[sum((Decimal(dietrows[j][i]) for j in range(1,50) if dietrows[j][i]),Decimal(0))+Decimal(dietrows[50][i]) for i in type0]
    summary={'model_id':MODEL_ID,'paper_id':'GOA-2020','canonical_path':relative(target,ROOT),'canonical_sha256':sha(target),'source_commit':COMMIT,'source_files':provenance,'groups':49,'consumers':46,'producers':1,'detritus':2,'fleets':1,'known_diet_sum_range':[str(min(sums)),str(max(sums))],'diet_columns_with_raw_blanks':sum(any(dietrows[j][i]=='' for j in range(1,50)) for i in type0),'native_nonzero_BA':[{'group_id':i,'name':r['Group'],'value':r['BioAcc'],'units':'t/km^2/year'} for i,r in enumerate(biological,1) if r['BioAcc'] and Decimal(r['BioAcc'])!=0],'validate_returncode':validation.returncode,'conversion_returncode':conversion.returncode,'native_canonical_checks':verification['all_passed'],'schema_admitted':loader['admitted']}
    dump(qa/'aggregated_summary.json',summary)
    # Written separately below, so rerunning numeric extraction does not need network.
    dump(qa/'aggregated_source_facts.json',{'citation':CITATION,'doi':'10.1016/j.ecolmodel.2020.109074','online_publication_date':'2020-05-25','model_period':'1990-1994','publication_is_not_baseline':True,'native_commit':COMMIT,'lineage':'Official documentation attributes aggregate to Whitehouse&Aydin2020 and original to Aydin2007; paper says B/catch summed and PB/QB/DC biomass weighted.','count_discrepancy':'2020 text says138 originalGOA groups; extracted2007 publication has133 biological compartments. Counts alone do not establish equivalence.','source_diet_runtime':'Rpath replaces NA diet with0 at runtime; raw sparse table preserved here.'})
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
