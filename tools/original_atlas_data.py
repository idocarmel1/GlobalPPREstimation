"""Adapt the current workbooks to the original atlas data interfaces.

Compressed reference payloads supply immutable source context and alternative-model evidence.
Project.xlsx owns published annual totals and metadata. Current regional workbooks
own selected-model details; changed inputs never inherit old detail calculations.
"""
import copy,csv,gzip,json,math,html
from pathlib import Path
from collections import defaultdict
from workbooks import *
from regional import result_hash,inputs
from researcher_review import approved_review

def embedded(path,variable):
    text=Path(path).read_text(encoding='utf-8');start=text.index('const '+variable+'=')+len('const '+variable+'=')
    value,end=json.JSONDecoder().raw_decode(text[start:]);return value,text[:start]+'__PPR_DATA__'+text[start+end:]

def source_context(root):
    context=Path(root)/'common_reference_data/atlas_source_context'
    with gzip.open(context/'catalog.json.gz','rt',encoding='utf-8') as source:catalog=json.load(source)
    with gzip.open(context/'time_series.json.gz','rt',encoding='utf-8') as source:series=json.load(source)
    return catalog,series

def reconcile_paper_files(root,papers):
    """Refresh local availability without treating presence as model validation.

    Only original files directly in a paper folder are discovered; extracted
    tables, metadata and working files are not downloadable source evidence.
    Existing identity/retrieval assessments are retained on known files.
    """
    root=Path(root).resolve()
    model_extensions={'.json','.ewe','.ewemdb','.eweaccdb','.mdb','.accdb'}
    extensions={'.pdf','.doc','.docx','.xls','.xlsx','.zip','.csv','.tif','.tiff','.png','.jpg','.jpeg'}|model_extensions
    administrative={'metadata.json','retrieval.json','source-facts.json','accession_retrieval.json','supplement_retrieval_log.json'}
    # A paper folder may retain a different publication for source context.
    # Reviewed roles are bound to exact bytes; filename/PDF presence alone cannot
    # establish that a related publication is the missing focal article.
    source_paths=SourcePaths(root)
    role_path=root/'common_reference_data/paper_file_roles.json'
    reviewed_roles={}
    if role_path.is_file():
        role_data=json.loads(role_path.read_text(encoding='utf-8'))
        if role_data.get('schema_version')!=1:raise ValueError('Unknown reviewed paper-file role schema')
        for item in role_data['files']:
            resolved=source_paths.resolve(item['path'])
            if resolved is None:continue
            target=(root/resolved).resolve()
            if not target.is_relative_to(root) or target in reviewed_roles:raise ValueError('Invalid or duplicate reviewed source-file path')
            if item['role'] not in {'main','supplement','model','source','context'}:raise ValueError('Unknown reviewed source-file role')
            if not item.get('sha256') or not item.get('evidence'):raise ValueError('Reviewed source-file role lacks identity/evidence')
            reviewed_roles[target]=item
    fingerprints={}
    def fingerprint(path):
        if path not in fingerprints:fingerprints[path]=(sha(path),path.stat().st_size)
        return fingerprints[path]
    source_folders=defaultdict(list)
    for directory in sorted((root/'regions').glob('*/papers/*')):
        if directory.is_dir():source_folders[directory.name].append(directory)
    for paper in papers:
        source_id=paper.get('source_article_id') or paper['article_id'].split('__')[0]
        folder=root/'regions'/paper['unit_id']/'papers'/source_id
        candidate_folders=[folder]
        if paper.get('article_dir'):
            declared=source_paths.resolve(paper['article_dir'])
            if declared is not None:
                declared=(root/declared).resolve()
                if not declared.is_relative_to(root):raise ValueError('Declared article folder is outside the repository')
                candidate_folders.insert(0,declared)
        found={}
        for record in paper.get('material_files',[]):
            path=(root/'interactive_map'/record['relative_path']).resolve()
            if path.is_relative_to(root) and path.name not in administrative and path.is_file() and path.stat().st_size:
                current=dict(record);current_hash,current_size=fingerprint(path)
                changed=bool(record.get('sha256') and record['sha256']!=current_hash)
                unproven=record.get('status')=='downloaded_verified' and not record.get('sha256')
                if changed or unproven:
                    previous={k:record.get(k) for k in ['sha256','size_bytes','status','identity_status','validation']}
                    if record.get('prior_file_assessment'):previous['earlier_assessment']=record['prior_file_assessment']
                    current.update(prior_file_assessment=previous,status='local_file_present',identity_status='not_reassessed',
                                   validation='Current local bytes differ from, or cannot be tied to, the prior assessment; scientific identity not reassessed.')
                current.update(sha256=current_hash,size_bytes=current_size)
                current.setdefault('status','local_file_present')
                found[path]=current
        # A single publication can support multiple regional entries. Reuse its
        # exact source ID when that region has no original files of its own.
        folders=[directory for directory in dict.fromkeys(candidate_folders) if directory.is_dir()
                 and any(p.is_file() and p.name not in administrative and p.suffix.lower() in extensions and p.stat().st_size for p in directory.iterdir())]
        if not folders:folders=source_folders.get(source_id,[])
        for directory in folders:
            for path in sorted(directory.iterdir()):
                if not path.is_file() or path.name in administrative or path.suffix.lower() not in extensions or not path.stat().st_size:continue
                path=path.resolve()
                if path in found:continue
                supplement=any(s in path.stem.lower() for s in ['mmc','supplement','supporting','appendix'])
                role='model' if path.suffix.lower() in model_extensions else 'supplement' if supplement else 'main' if path.suffix.lower()=='.pdf' else 'source'
                current_hash,current_size=fingerprint(path)
                found[path]={'filename':path.name,'role':role,'file_label':('Model source' if role=='model' else 'Supplement' if supplement else 'Paper' if role=='main' else 'Source file')+' '+path.suffix[1:].upper(),
                             'status':'local_file_present','validation':'Local non-empty file; scientific identity and model loadability not reassessed.',
                             'sha256':current_hash,'size_bytes':current_size}
        material=[]
        for path,record in found.items():
            review=reviewed_roles.get(path)
            if review:
                if record['sha256']==review['sha256']:
                    record.update(role=review['role'],file_label=review['file_label'],
                                  role_evidence=review['evidence'])
                else:
                    record.update(role='source',file_label='Source file '+path.suffix[1:].upper(),
                                  identity_status='not_reassessed',status='local_file_present',
                                  validation='Source bytes changed since the reviewed file-role assessment; focal article identity is not established.')
                    record.pop('role_evidence',None)
            record.update({'relative_path':'../'+path.relative_to(root).as_posix(),'article_id':paper['article_id'],'unit_id':paper['unit_id']})
            material.append(record)
        paper['material_files']=material
        paper['downloaded_file_count']=len(material)
        paper['download_status']='local_files_available' if material else 'no_verified_file'
        paper['main_file_status']='local_file_present' if any(f.get('role')=='main' for f in material) else 'not_found'
        paper['supplement_status']='local_file_present' if any(f.get('role')=='supplement' for f in material) else 'not_found'
        paper['model_file_status']='local_file_present' if any(f.get('role')=='model' for f in material) else 'not_found'
        if material:
            if not paper.get('download_failure_reason') or paper['download_failure_reason'].startswith('No source file verified in this archive.'):
                paper['download_failure_reason']=''
            # The numeric quality score is a historical scientific assessment,
            # not something that can be recomputed from file existence alone.
            stale='E — no verified downloadable file'
            if stale in (paper.get('loadability_class') or ''):
                paper['loadability_class']='Local sources available; model loadability not reassessed'
            if stale in (paper.get('quality_rationale') or ''):
                paper['quality_rationale']='Historical score (not reassessed after local file discovery). '+paper.get('quality_rationale','').replace(stale+'. ','').replace(stale,'')

class SourcePaths:
    """Resolve historical references without rewriting scientific source workbooks."""
    def __init__(self,root):
        self.root=Path(root);self.paths={}
        for file,old,new in [
            ('original_research_archive/migration.csv','original_path','retained_path'),
            ('common_reference_data/provenance/archive_relocation.csv','old_path','new_path')]:
            path=self.root/file
            if path.exists():
                with path.open(encoding='utf-8-sig',newline='') as source:
                    self.paths.update({r[old]:r[new] or None for r in csv.DictReader(source)})

    def resolve(self,value):
        normalized=value.replace('\\','/')
        candidates=[normalized,normalized.removeprefix('../'),'PPRAtlas/'+normalized]
        match=next((p for p in candidates if p in self.paths),None)
        if match is None:
            if normalized.startswith('archive/regions/'):
                parts=('regions/'+normalized[len('archive/regions/'):]).split('/')
                return '/'.join(parts[:2]+['papers']+parts[2:])
            return value
        seen=set()
        while match in self.paths:
            target=self.paths[match]
            if target is None:return None
            if target==match:return target
            if match in seen:raise ValueError(f'cyclic source relocation: {value}')
            seen.add(match);match=target
        return match

    def rewrite(self,value,key=None):
        if isinstance(value,dict):return {k:self.rewrite(v,k) for k,v in value.items()}
        if isinstance(value,list):
            rewritten=[self.rewrite(v,key) for v in value]
            # Removed interface artifacts retain their audit record, but are not links.
            return [v for v in rewritten if not isinstance(v,dict) or 'relative_path' not in v or v['relative_path'] is not None]
        if not isinstance(value,str):return value
        path=self.resolve(value)
        if path is not None and path!=value and key=='relative_path':return '../'+path.removeprefix('../')
        return path

def branch(record,treatment,basis):
    target=record if treatment=='method' else record.setdefault('unidentified_'+treatment,{})
    return target if basis=='landings' else target.setdefault('catch_bases',{}).setdefault(basis,{})

def fill_annual(data,template=None):
    result=copy.deepcopy(template or {})
    # Every supported branch is replaced by the current workbook values.
    for treatment in ['method','zero','simple']:
        for basis in ['landings','catch','discards']:
            target=branch(result,treatment,basis)
            for metric in ['ppr','catch','covered_catch']:target[metric]=[None]*70
            target['status']='unavailable'
            target.pop('sensitivity',None)
    for r in data:
        target=branch(result,r['unidentified'],r['catch_basis']);metric=r['metric'];values=[r.get(y) for y in YEARS]
        if metric in ['min_tC','max_tC']:
            if any(finite(v) for v in values):
                original=branch(template or {},r['unidentified'],r['catch_basis']).get('sensitivity',[])
                bands=target.setdefault('sensitivity',[copy.deepcopy(original[i]) if i<len(original) and original[i] else {} for i in range(70)])
                for i,v in enumerate(values):bands[i].update({metric:v,'status':'assessed' if finite(v) else 'not_assessed'})
        else:
            target[metric]=values
            if metric=='ppr':target['status']=r.get('status') or 'unavailable'
    return result

def detail_from_book(book,unit,model_id):
    taxa,catch,unidentified,simple=inputs(book)
    taxainfo={r['taxon']:r for r in records(book,'Catch','Catch')};tl={r['taxon']:r for r in records(book,'Classic PPR','Taxa')}
    affected={'classifier_version':'regional-workbook','rule_description':'Explicit unidentified classification retained in regional Catch.',
              'taxa':[{'name':t,'common_name':taxainfo[t].get('common_name'),'reason':'Regional Catch unidentified flag','reference_tl':tl.get(t,{}).get('tl'),'simple_sppr':simple.get(t)} for t in taxa if unidentified.get(t)],'catch_bases':{}}
    for basis in ['landings','catch','discards']:
        sums={}
        for field,selected in [('catch',[t for t in taxa if unidentified.get(t)]),('missing_simple_catch',[t for t in taxa if unidentified.get(t) and not finite(simple.get(t))])]:
            sums[field]=[math.fsum(catch[t,basis][i] for t in selected) if all(finite(catch.get((t,basis),[None]*70)[i]) for t in selected) else None for i in range(70)]
        if basis=='landings':affected.update(sums)
        else:affected['catch_bases'][basis]=sums
    inp={'years':YEARS,'taxa':taxa,'simple_sppr':[simple.get(t) for t in taxa],'unidentified':affected,'catch_basis_policy':'explicit regional workbook catch bases',
         **{basis:[catch.get((t,basis),[None]*70) for t in taxa] for basis in ['landings','catch','discards']}}
    inp['full_precision_catch']=inp['catch']
    groups=records(book,'Selected model groups','Groups');coeff=records(book,'Selected model groups','Group SPPR')
    methods=list(dict.fromkeys(r['method'] for r in coeff));group_names=[r['group_name'] for r in groups]
    indices={g:i for i,g in enumerate(group_names)};assign=defaultdict(list)
    for r in records(book,'PPR','Matching'):
        if r.get('group') in indices:assign[r['taxon']].append([indices[r['group']],r['weight']])
    values={(r['group'],r['scope'],r['method']):r['sppr'] for r in coeff}
    gd={'groups':[{'id':r['group_name'],'name':r['group_name'],'tl':r.get('tl'),'te':r['ge']*r['ee'] if finite(r.get('ge')) and finite(r.get('ee')) else None} for r in groups],
        'methods':methods,'scopes':{scope:[[values.get((g,scope,m)) for m in methods] for g in group_names] for scope in ['all','inner','PP']},
        'mappings':[assign[t] for t in taxa],'te_definition':'Stored source-group GE × EE; no EE repair or solver recalculation.',
        'provenance':{'workbook':f'regions/{unit}/{unit}.xlsx','groups_sheet':'Selected model groups','mapping_sheet':'PPR'}}
    statuses={(r['scope'],r['method']):r['status'] for r in records(book,'PPR','Annual') if r['metric']=='ppr' and r['catch_basis']=='landings' and r['unidentified']=='method'}
    tc={(r['taxon'],r['scope'],r['method']):r['sppr'] for r in records(book,'PPR','Taxon SPPR')}
    scopes={}
    for scope in ['all','inner','PP']:
        mm=methods+([SIMPLE] if scope=='all' else [])
        scopes[scope]={'methods':mm,'status':{m:('ok' if m==SIMPLE else statuses.get((scope,m),'unavailable')) for m in mm},
                       'values':[[simple.get(t) if m==SIMPLE else tc.get((t,scope,m)) for m in mm] for t in taxa]}
    health={}
    for r in records(book,'Diagnostics','model_health'):
        option=r.get('TE_option') or r.get('config_TE_option')
        if not option:continue
        health[option]={'b':r.get('divergence_b'),'rho_living':r.get('divergence_rho_living'),'status':r.get('status'),
            'b_converges':r.get('divergence_b_converges'),'living_converges':r.get('divergence_living_converges'),'balanced':r.get('model_input_is_model_balanced'),
            'config':{k[7:]:v for k,v in r.items() if k.startswith('config_')}}
    mc={r['method']:{k:r.get(k) for k in ['n_samples','n_accepted']} for r in records(book,'Diagnostics','mc_diagnostics')}
    # The atlas flag enables mapping/group controls; coefficient availability is
    # checked separately by each method. It is not scientific model approval.
    model={'id':model_id,'label':model_id.replace('_',' '),'verified':bool(any(assign.values())),'scopes':scopes,'group_data':gd,'health':health,'mc_diagnostics':mc}
    return inp,model

def review_flags(book):
    flags=[]
    for r in records(book,'Diagnostics','model_health'):
        option=r.get('TE_option') or r.get('config_TE_option') or 'SPPR';grade=r.get('status')
        if grade and grade!='OK':flags.append(f'{option}: {grade}')
        for field,label in [('model_input_is_model_balanced','strict input balance false'),('balance_is_balanced','strict SPPR balance false')]:
            if r.get(field) is False:flags.append(f'{option}: {label}')
    for r in records(book,'PPR','Annual'):
        status=str(r.get('status') or '')
        if r.get('metric')=='ppr' and status.startswith('provisional:'):flags.append(f"{r['method']}: {status}")
    o=overview(book)
    if not records(book,'Diagnostics','model_health'):flags.append('Diagnostic report not available in regional workbook; see retained model evidence')
    if o.get('production_eligible') is False:flags.append('Whole-region scientific validation pending')
    return list(dict.fromkeys(flags))

def datasets(workbook):
    root=workbook.parent
    catalog,series=source_context(root);network=catalog.pop('network')
    for collection in ['regions','articles']:
        for r in catalog[collection]:
            for k in ['title','authors','region_name','recommendation','coverage_note','quality_rationale','geometry_note','geometry_method','search_notes','loadability_class','download_failure_reason']:
                if isinstance(r.get(k),str):r[k]=html.unescape(r[k])
            for f in r.get('material_files',[]):
                for k in ['filename','file_label']:
                    if isinstance(f.get(k),str):f[k]=html.unescape(f[k])
    project=read_book(workbook);region_rows=records(project,'Regions & status','Regions')
    model_metadata={(r['unit_id'],r['model_id']):r for r in records(project,'Models & coverage','Models')}
    geometry=unchunks(rows(project,'Map geography','Geometry'));meta=unchunks(rows(project,'Definitions & build','Metadata'))
    for key,value in meta.items():
        if key in series:series[key]=value
    annual=defaultdict(list)
    for r in records(project,'Regional PPR','Annual'):annual[r['unit_id']].append(r)
    npp=defaultdict(dict);npp_meta=defaultdict(dict)
    for r in records(project,'Regional NPP','NPP'):npp[r['unit_id']][r['method']]=[r.get(y) for y in YEARS]
    for r in records(project,'Regional NPP','Provenance'):npp_meta[r['unit_id']][str(r['year'])]=json.loads(r['details'])
    oldregions={r['unit_id']:r for r in catalog['regions']};newregions=[];series_units={};network_units={};simple_units={}
    catalog['annual']={str(y):{} for y in YEARS}
    for region in region_rows:
        unit=region['unit_id'];path=root/region['workbook'];selected=region.get('selected_model_id')
        if not path.is_file() or sha(path)!=region['sha256']:raise ValueError(f'{unit}: regional workbook changed; update Project.xlsx before generating HTML')
        u=copy.deepcopy(series['units'].get(unit,{'models':[]}));nu=copy.deepcopy(network['units'].get(unit,{'models':[]}))
        u.update({'name':region['name'],'type':region['type'],'note':region.get('selection_rationale') or '', 'default_model':selected,'npp':npp[unit],'npp_metadata':npp_meta[unit]})
        source={'workbook':region['workbook']};u['sources']=source;nu['sources']=source;nu['note']=u['note']
        classic=[r for r in annual[unit] if not r['model_id'] and r['method']==SIMPLE]
        u['simple']=fill_annual(classic,u.get('simple'))
        sm=next((m for m in u['models'] if m['id']==selected),None);nm=next((m for m in nu['models'] if m['id']==selected),None)
        changed=not str(region.get('status','')).startswith('migrated saved results')
        if selected or changed or unit not in series['units']:
            book=read_book(path);o=validate_region(book,path)
            if o.get('calculation_result_sha256')!=result_hash(book):raise ValueError(f'{unit}: generated regional results are stale')
            if changed or selected and (sm is None or nm is None):
                detail,newmodel=detail_from_book(book,unit,selected)
                nu.update(detail);u['group_inputs']=detail;u['unidentified']=detail['unidentified']
                if selected:
                    nm=newmodel;sm={k:copy.deepcopy(v) for k,v in newmodel.items() if k!='scopes'};sm['taxon_scopes']=copy.deepcopy(newmodel['scopes']);sm['scopes']={}
                    nu['models']=[m for m in nu['models'] if m['id']!=selected]+[nm];u['models']=[m for m in u['models'] if m['id']!=selected]+[sm]
            print(f'Checked HTML detail inputs: {unit}',flush=True)
        if selected:
            selected_rows=[r for r in annual[unit] if r['model_id']==selected]
            if sm is None:sm={'id':selected,'label':selected,'verified':False,'scopes':{}};u['models'].append(sm)
            prior=sm.get('scopes',{});sm['scopes']={}
            for scope,method in dict.fromkeys((r['scope'],r['method']) for r in selected_rows):
                record=fill_annual([r for r in selected_rows if r['scope']==scope and r['method']==method],prior.get(scope,{}).get('methods',{}).get(method))
                sm['scopes'].setdefault(scope,{'methods':{}})['methods'][method]=record
            for model in [sm,nm]:
                if model is not None:
                    sourcefile=f'regions/{unit}/models/{selected}/sppr_source.xlsx'
                    if not (root/sourcefile).exists():sourcefile=f'regions/{unit}/models/{selected}/model.json'
                    model.update({'workbook':region['workbook'],'workbook_sha256':region['sha256'],'source':sourcefile})
                    model['review_flags']=review_flags(book)
                    model['review_note']=overview(book).get('source_note') or overview(book).get('calculation_status') or ''
                    review=approved_review(root,model_metadata.get((unit,selected)),book)
                    if review:
                        model['researcher_review']=copy.deepcopy(review)
                        model['display_ppr_excluded_group_ids']=review['excluded_group_ids'][:]
            if nm is not None:
                if changed:nm.pop('discard_sensitivity',None);nm['discard_sensitivity_unavailable']={}
                for scope,s in sm['scopes'].items():
                    for method,record in s['methods'].items():
                        for treatment in ['method','zero','simple']:
                            band=branch(record,treatment,'landings').get('sensitivity')
                            if band:nm.setdefault('discard_sensitivity',{}).setdefault(scope,{}).setdefault(method,{})[treatment]=band
        nu['default_model']=next((i for i,m in enumerate(nu['models']) if m['id']==selected),None)
        nu['selected_articles']=[r['article_id'] for r in records(project,'Papers','Papers') if r['unit_id']==unit and r.get('selected')]
        if not nu['selected_articles']:nu['selected_articles']=[r['article_id'] for r in records(project,'Papers','Papers') if r['unit_id']==unit]
        if nu['models']:network_units[unit]=nu
        su=copy.deepcopy(network.get('simple_units',{}).get(unit,{}));su.update({k:u[k] for k in ['name','type','simple','sources']});su['years']=YEARS
        if u.get('unidentified') is not None:su['unidentified']=u['unidentified']
        simple_units[unit]=su;series_units[unit]=u
        r=copy.deepcopy(oldregions.get(unit,{'unit_id':unit,'search_status':'not reviewed','search_notes':'','ppr_rank':None,'marker_lat':0,'marker_lon':0}))
        r.update({'region_name':region['name'],'region_type':region['type'],'geometry':geometry.get(unit,r.get('geometry'))})
        newregions.append(r)
        for i,y in enumerate(YEARS):catalog['annual'][str(y)][unit]=[u['simple']['ppr'][i],u['simple']['catch'][i],u['simple']['status']]
    network.update({'units':network_units,'simple_units':simple_units,'npp':dict(npp),'npp_metadata':dict(npp_meta),'npp_years':YEARS,'npp_methods':series['npp_methods']})
    series['units']=series_units;series['years']=YEARS
    oldpapers={r['article_id']:r for r in catalog['articles']};papers=[]
    for row in records(project,'Papers','Papers'):
        paper={**oldpapers.get(row['article_id'],{}),**row};paper['geometry']=geometry.get('article:'+row['article_id']);paper.setdefault('material_files',[])
        for field in ['title','authors','recommendation','coverage_class','coverage_note','quality_rationale','geometry_note','geometry_method','search_notes','loadability_class','download_failure_reason']:
            if paper.get(field) is None:paper[field]=''
        papers.append(paper)
    catalog.update({'regions':newregions,'articles':papers,'network':network,'source_workbook':'../'+workbook.name})
    paths=SourcePaths(root)
    catalog=paths.rewrite(catalog)
    reconcile_paper_files(root,catalog['articles'])
    catalog['files']=[dict(f) for paper in catalog['articles'] for f in paper['material_files']]
    return catalog,paths.rewrite(series),project
