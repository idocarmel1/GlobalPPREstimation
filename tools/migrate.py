"""One-time migration from the frozen original checkout; never modifies that checkout."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, shutil, sys
from pathlib import Path
from collections import defaultdict
from workbooks import *

def jread(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def csvread(p):
    if not Path(p).exists(): return []
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def catch_table(source, unit, unidentified):
    p=source/'SeaAroundUsExtraction/data/catch_by_taxon_year'/f'{unit}.csv.gz'
    labels={}; data={}
    if p.exists():
        with gzip.open(p,'rt',encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                name=r['taxon']; year=int(r['year'])
                labels.setdefault(name,[r.get(k) for k in ['common_name','functional_group','commercial_group']])
                for basis in ['catch','landings','discards']:
                    arr=data.setdefault((name,basis),[0.]*70); v=r.get(basis+'_tonnes')
                    val=float(v) if v not in ('',None) else None
                    arr[year-1950]=arr[year-1950]+val if arr[year-1950] is not None and val is not None else None
    # Source years absent for the whole region stay unavailable, not zero.
    years=set()
    if p.exists():
        with gzip.open(p,'rt') as f:
            for r in csv.DictReader(f):years.add(int(r['year']))
    rows=[]
    for (taxon,basis),arr in sorted(data.items()):
        rows.append([taxon,*labels[taxon],basis,taxon in unidentified,*[arr[i] if y in years else None for i,y in enumerate(YEARS)]])
    return ['taxon','common_name','functional_group','commercial_group','catch_basis','unidentified',*YEARS],rows

def migrate(source, dest, units=None):
    network=jread(source/'PPRAtlas/data/network_ppr.json'); times=jread(source/'PPRAtlas/data/time_series.json')
    catalog=jread(source/'PPRAtlas/data/catalog.json'); selections=jread(source/'data/atlas_selection.json')['units']
    project={'Regions & status':{},'Papers':{},'Models & coverage':{},'Regional PPR':{},'Regional NPP':{},
             'Method comparisons':{},'Diagnostics & sensitivity':{},'Map geography':{},'Definitions & build':{}}
    articles=[]; geometries=[]
    for r in catalog['articles']:
        x={k:v for k,v in r.items() if k not in ['geometry','material_files']}
        x['selected']=False
        # Existing atlas assignments identify sources; individual extracted models have their own table.
        for k in ['article_dir','region_dir']:
            if x.get(k): x[k]=str(x[k]).replace('archive/regions/','regions/').replace('/'+r.get('source_article_id','__NO__'),'/papers/'+r.get('source_article_id','__NO__'))
        articles.append(x)
        if r.get('geometry'):geometries+=chunks('article:'+r['article_id'],r['geometry'])
    project['Papers']['Papers']=table_dict(articles)
    project['Map geography']['Geometry']=(['geometry_id','part','geojson'],geometries)
    for r in catalog['regions']:
        if r.get('geometry'):project['Map geography']['Geometry'][1].extend(chunks(r['unit_id'],r['geometry']))
    project['Definitions & build']['Metadata']=(['key','part','value'],[])
    for key in ['sets','npp_methods','ppr_methods','scopes','npp_policy','global_npp','units_note','model_note']:
        if key in times: project['Definitions & build']['Metadata'][1].extend(chunks(key,times[key]))
    project['Definitions & build']['Definitions']=(['field','definition'],[
        ['PPR units','tonnes wet-weight equivalent; divide by 9 once for carbon'],['NPP units','tonnes carbon per year'],
        ['ownership','Papers and Models & coverage are centrally editable; region selections and result tables are generated'],
        ['annual comparison','Fixed common ecosystem cohort; each method retains its own catch coverage'],
        ['map comparison','Common catch taxa for numerator and denominator; do not divide unmatched regional totals'],
        ['missing','Blank is unavailable, never numeric zero'],['schema_version','1']])
    models=[]; ledger=[]; assigned={}; hashes={}
    def copy(p, target, deduplicate=False):
        if not p.is_file():return
        rel=p.relative_to(source).as_posix(); h=sha(p)
        if deduplicate and h in hashes:target=hashes[h]
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():shutil.copy2(p,target)
            elif sha(target)!=h:raise ValueError(f'Migration collision: {target}')
            hashes[h]=target
        assigned[rel]=target;ledger.append([rel,target.relative_to(dest).as_posix(),p.stat().st_size,h])
    unit_list=units or sorted(times['units'])
    for idx,unit in enumerate(unit_list):
        u=times['units'][unit]; choice=selections.get(unit,{}); selected=choice.get('default_model');folder=dest/'regions'/unit
        folder.mkdir(parents=True,exist_ok=True)
        for d in ['papers','models','raw']:(folder/d).mkdir(exist_ok=True)
        srcpapers=source/'PPRAtlas/archive/regions'/unit
        if srcpapers.exists():
            for p in srcpapers.rglob('*'):
                if p.is_file() and p.name!='.DS_Store':copy(p,folder/'papers'/p.relative_to(srcpapers))
        for p in (source/'PPREstimation/real_models/global_cover_jsons').glob('*.json'):
            prefix=('HS_'+p.name.split('HS_')[0].zfill(3)) if 'HS_' in p.name else 'LME_'+p.name.split('_')[0].zfill(3)
            if prefix!=unit:continue
            copy(p,folder/'models'/p.stem/'model.json')
            models.append({'unit_id':unit,'model_id':p.stem,'model_path':f'regions/{unit}/models/{p.stem}/model.json',
                           'source_filename':p.name,'selected':p.stem==selected,'selection_rationale':choice.get('note') if p.stem==selected else None,
                           'paper_ids':';'.join(choice.get('selected_articles',[])) if p.stem==selected else None})
            sp=source/'PPREstimation/output/top10'/f'{p.stem}.xlsx'
            if sp.exists():copy(sp,folder/'models'/p.stem/'sppr_source.xlsx')
        for p in (source/'SeaAroundUsExtraction/raw_data/SAU_downloads').glob(unit+'-*'):copy(p,folder/'raw'/p.name)
        annual=source/'SeaAroundUsExtraction/data/catch_by_taxon_year'/f'{unit}.csv.gz'
        if annual.exists():copy(annual,folder/'raw'/annual.name)
        for directory in ['mapping','validation']:
            sd=source/'data'/unit/directory
            if sd.exists():
                for p in sd.rglob('*'):
                    if p.is_file():copy(p,folder/'models'/(selected or 'validation')/'source_evidence'/directory/p.relative_to(sd))
        for p in (source/'data'/unit/'models').glob('*.xlsx'):copy(p,folder/'models'/p.stem/'legacy_ppr.xlsx')
        b={s:{} for s in REGION_SHEETS}
        o={'unit_id':unit,'region_name':u['name'],'region_type':u['type'],'selected_model_id':selected,
           'selection_rationale':choice.get('note'),'model_path':f'models/{selected}/model.json' if selected else None,
           'results_model_id':selected,'results_model_sha256':sha(folder/'models'/selected/'model.json') if selected else None,
           'selected_paper_ids':';'.join(choice.get('selected_articles',[])), 'production_eligible':bool(choice),
           'catch_basis':'landings','transfer_efficiency':0.1,'taxon_detail_year':2019,
           'source_note':u.get('note'),'calculation_status':'migrated saved results; unavailable methods retained',
           'source_region_workbook':f'original_research_archive/legacy/data/{unit}/{unit}.xlsx',
           'npp_policy':'Annual observed support; unsupported years stay blank; no earliest-year proxy by default'}
        b['Overview']['Settings']=(['field','value'],list(map(list,o.items())))
        unidentified={r['name'] for r in u.get('unidentified',{}).get('taxa',[])}
        b['Catch']['Catch']=catch_table(source,unit,unidentified)
        tl=[]
        for d in ['global_output','eez_output']:
            p=source/'SeaAroundUsExtraction'/d/'tables/regions'/unit/'species.csv'
            if p.exists():tl=csvread(p);break
        b['Classic PPR']['Taxa']=(['taxon','tl','sppr','tl_source','match_method','confidence'],[
            [r['taxon'],float(r['tl']) if r.get('tl') else None,float(r['sppr']) if r.get('sppr') else None,r.get('tl_source'),r.get('match_method'),r.get('match_confidence')] for r in tl])
        b['Classic PPR']['Annual']=(ANNUAL_HEADER,flatten_method('', 'all', SIMPLE,u['simple']))
        for typ in ['commercial','functional']:
            groupfile=source/'SeaAroundUsExtraction'/('eez_output' if unit.startswith('EEZ') else 'global_output')/'tables/regions'/unit/(typ+'.csv')
            b['Classic PPR'][typ+' comparison']=table_dict(csvread(groupfile))
        nm=next((m for m in network['units'].get(unit,{}).get('models',[]) if m['id']==selected),None)
        tm=next((m for m in u.get('models',[]) if m['id']==selected),None)
        b['PPR']['Annual']=(ANNUAL_HEADER,[])
        b['PPR']['Taxon SPPR']=(['model_id','taxon','scope','method','sppr'],[])
        b['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],[])
        if nm:
            upstream=folder/'models'/selected/'sppr_source.xlsx'; w=openpyxl.load_workbook(upstream,read_only=True,data_only=True)
            b['Selected model groups']['Groups']=(list(next(w['groups_df'].values)),[list(r) for r in list(w['groups_df'].values)[1:]])
            gs=[]
            for scope in ['all','inner','PP']:
                rr=list(w['sppr_'+scope].values); hh=rr[0]
                gs.extend([[selected,r[1],scope,method,r[i]] for r in rr[1:] for i,method in enumerate(hh) if i>=2])
            b['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],gs)
            for sn in ['model_health','mc_diagnostics','run_notes']:
                rr=list(w[sn].values);b['Diagnostics'][sn]=(list(rr[0]),[list(r) for r in rr[1:]])
            w.close()
            mr=csvread(source/'data'/unit/'mapping'/f'{selected}.csv'); notes={r['taxon']:r for r in mr}
            gd=nm.get('group_data',{})
            for taxon,assign in zip(network['units'][unit]['taxa'],gd.get('mappings',[])):
                note=notes.get(taxon,{})
                for gi,weight in assign:
                    b['PPR']['Matching'][1].append([selected,taxon,gd['groups'][gi]['name'],weight,note.get('confidence'),note.get('evidence'),note.get('explanation')])
                if not assign:b['PPR']['Matching'][1].append([selected,taxon,None,None,note.get('confidence','unresolved'),note.get('evidence'),note.get('explanation')])
            for scope,ss in nm.get('scopes',{}).items():
                for taxon,vals in zip(network['units'][unit]['taxa'],ss['values']):
                    for method,v in zip(ss['methods'],vals):
                        if method!=SIMPLE:b['PPR']['Taxon SPPR'][1].append([selected,taxon,scope,method,v])
            if tm:
                for scope,ss in tm.get('scopes',{}).items():
                    for method,v in ss['methods'].items():b['PPR']['Annual'][1].extend(flatten_method(selected,scope,method,v))
        b['NPP']['NPP']=(['method','units',*YEARS],[[k,'tC/year',*v] for k,v in u.get('npp',{}).items()])
        b['NPP']['Provenance']=table_dict([{'year':int(y),**r} for y,r in u.get('npp_metadata',{}).items()])
        # Ratios are an explicit readable regional output, one row per method/scenario/NPP method.
        npp={r[0]:r[2:] for r in b['NPP']['NPP'][1]}
        ratio=[]
        for r in b['Classic PPR']['Annual'][1]+b['PPR']['Annual'][1]:
            if r[5]!='ppr':continue
            for method,den in npp.items():ratio.append([*r[:5],method,*[100*p/9/n if finite(p) and finite(n) and n>0 else None for p,n in zip(r[7:],den)]])
        b['PPR–NPP']['Ratios']=(['model_id','scope','method','catch_basis','unidentified','npp_method',*YEARS],ratio)
        b['Overview']['Settings'][1].append(['calculation_input_sha256',input_hash(b)])
        from regional import set_result_hash, taxon_detail
        taxon_detail(b)
        set_result_hash(b)
        write_book(folder/f'{unit}.xlsx',b)
        if idx%20==0: print(f'Regional workbooks: {idx+1}/{len(unit_list)}',flush=True)
    project['Models & coverage']['Models']=table_dict(models)
    write_book(dest/'Project.xlsx',project)
    if units:return
    # Keep original code runnable as a historical reference. Active regional tools use only local workbook/native inputs.
    for p in sorted(source.rglob('*')):
        if not p.is_file() or '.git' in p.parts or p.name=='.DS_Store':continue
        rel=p.relative_to(source).as_posix()
        if rel in assigned:continue
        if rel.startswith('SeaAroundUsExtraction/spatial/'):
            target=dest/'common_reference_data/geography'/p.name
        elif rel.startswith('SeaAroundUsExtraction/input/'):
            target=dest/'common_reference_data/taxonomic_references'/p.relative_to(source/'SeaAroundUsExtraction/input')
        elif rel.startswith('PPREstimation/real_models/'):
            target=dest/'common_reference_data/ecobase_library'/p.relative_to(source/'PPREstimation/real_models')
        elif rel.startswith('research/'):
            target=dest/'original_research_archive'/p.relative_to(source)
        elif rel.startswith('graphify-out/'):
            target=dest/'original_research_archive/knowledge_graph'/p.name
        else:target=dest/'original_research_archive/legacy'/p.relative_to(source)
        copy(p,target)
    # Distribution sources retain exact bytes; separate from the maintained new entry points.
    for sub in ['PPREstimation','NPPExtraction','SeaAroundUsExtraction']:
        sd=source/sub
        for p in sd.rglob('*'):
            if p.is_file() and p.suffix in ['.py','.md','.yaml','.yml','.txt','.toml','.mjs','.json'] and not any(x in p.parts for x in ['output','real_models','raw_data','data','archive','global_output','eez_output']):
                target=dest/'tools/scientific_code'/sub/p.relative_to(sd); target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    shutil.copytree(source/'skills',dest/'tools/skills/original_skill_resources',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','.DS_Store'))
    with open(dest/'original_research_archive/migration.csv','w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['original_path','retained_path','bytes','sha256']);w.writerows(ledger)
    print(f'Preserved {len(ledger)} source files with hashes',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--dest',type=Path,required=True);ap.add_argument('--units',nargs='*');a=ap.parse_args()
    migrate(a.source.resolve(),a.dest.resolve(),a.units)
