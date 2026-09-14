"""Adapt the current workbooks to the original atlas data interfaces.

Archived exports supply immutable source context and alternative-model evidence.
Project.xlsx owns published annual totals and metadata. Current regional workbooks
own selected-model details; changed inputs never inherit old detail calculations.
"""
import copy,csv,json,math,html
from pathlib import Path
from collections import defaultdict
from workbooks import *
from regional import result_hash,inputs

def embedded(path,variable):
    text=Path(path).read_text();start=text.index('const '+variable+'=')+len('const '+variable+'=')
    value,end=json.JSONDecoder().raw_decode(text[start:]);return value,text[:start]+'__PPR_DATA__'+text[start+end:]

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
        health[r['TE_option']]={'b':r.get('divergence_b'),'rho_living':r.get('divergence_rho_living'),'status':r.get('status'),
            'b_converges':r.get('divergence_b_converges'),'living_converges':r.get('divergence_living_converges'),'balanced':r.get('model_input_is_model_balanced'),
            'config':{k[7:]:v for k,v in r.items() if k.startswith('config_')}}
    mc={r['method']:{k:r.get(k) for k in ['n_samples','n_accepted']} for r in records(book,'Diagnostics','mc_diagnostics')}
    model={'id':model_id,'label':model_id.replace('_',' '),'verified':bool(any(assign.values()) and tc),'scopes':scopes,'group_data':gd,'health':health,'mc_diagnostics':mc}
    return inp,model

def datasets(workbook):
    root=workbook.parent;old=root/'original_research_archive/legacy/PPRAtlas'
    catalog,_=embedded(old/'index.html','DB');network=catalog.pop('network')
    for collection in ['regions','articles']:
        for r in catalog[collection]:
            for k in ['title','authors','region_name','recommendation','coverage_note','quality_rationale','geometry_note','geometry_method','search_notes','loadability_class','download_failure_reason']:
                if isinstance(r.get(k),str):r[k]=html.unescape(r[k])
            for f in r.get('material_files',[]):
                for k in ['filename','file_label']:
                    if isinstance(f.get(k),str):f[k]=html.unescape(f[k])
    series,_=embedded(old/'trends.html','SERIES_DB')
    project=read_book(workbook);region_rows=records(project,'Regions & status','Regions')
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
    # Paths embedded in the old data are resolved through the preservation ledger.
    with (root/'original_research_archive/migration.csv').open() as f:ledger={r['original_path']:r['retained_path'] for r in csv.DictReader(f)}
    def rewrite(value,key=None):
        if isinstance(value,dict):return {k:rewrite(v,k) for k,v in value.items()}
        if isinstance(value,list):return [rewrite(v,key) for v in value]
        if not isinstance(value,str):return value
        path=ledger.get(value) or ledger.get('PPRAtlas/'+value)
        if not path and value.startswith('archive/regions/'):path='regions/'+value[len('archive/regions/'):];parts=path.split('/');path='/'.join(parts[:2]+['papers']+parts[2:])
        if path:return '../'+path if key=='relative_path' else path
        return value
    return rewrite(catalog),rewrite(series),project
