"""Display every ecosystem while keeping curated article membership explicit."""
from pathlib import Path
from collections import defaultdict
import csv, json, math
from shapely.geometry import shape, mapping, box
from .core import rank_regions, select_regions

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def display_geographies(root):
    """Read identity-matched source polygons; simplify only the display copies."""
    extraction = root.parent / 'SeaAroundUsExtraction'
    identities = [row for folder in ('global_output', 'eez_output')
                  for row in read_json(extraction / folder / 'tables/units.json')]
    if len({row['unit_id'] for row in identities}) != len(identities):
        raise ValueError('Duplicate ecosystem identities')
    geometries = {}
    for filename, prefix in [('LMEs.geojson', 'LME'), ('HighSeas.geojson', 'HS'), ('EEZs.geojson', 'EEZ')]:
        for feature in read_json(extraction / 'spatial' / filename)['features']:
            props = feature['properties']
            unit_id = props.get('unit_id') or f"{prefix}_{int(props['region_id']):03d}"
            if unit_id in geometries:
                raise ValueError(f'Duplicate source polygon: {unit_id}')
            geometry = shape(feature['geometry'])
            if geometry.is_empty:
                raise ValueError(f'Empty source polygon: {unit_id}')
            geometries[unit_id] = dict(geometry=mapping(geometry.simplify(0.03, preserve_topology=True)),
                                      geometry_source=f'SeaAroundUsExtraction/spatial/{filename}',
                                      display_simplification_degrees=0.03)
    return [(row, geometries[row['unit_id']]) for row in identities]

def new_article(source, assignment, region, material):
    verified=[f for f in material if f['status']=='downloaded_verified']
    main=any(f['role']=='main' for f in verified)
    components=dict(model_loadability_score_55=20 if main else 5,documentation_score_20=10 if main else 5,
                    spatial_fit_score_15={'whole_eez':15,'whole_lme':15,'subregional':7,'basin_proxy':3}[assignment['coverage_class']],
                    recency_validation_score_10=7 if source.get('publication_year',0)>=2015 else 3)
    cap=58 if verified else 25
    rationale='Provisional screening score. A readable source is not evidence of a successfully reconstructed or load-tested Ecopath model.'
    geometry=None;method='No defensible digital study boundary located';confidence='unavailable'
    if assignment.get('geometry_bbox'):
        geometry=mapping(box(*assignment['geometry_bbox']));method='Approximate reported study bounds; not an author-supplied polygon';confidence='low'
    elif assignment['coverage_class'] in ('whole_eez','whole_lme'):
        geometry=region['geometry'];method='Selected ecosystem polygon used as intended study envelope, not a recovered author boundary';confidence='low'
    return dict(source,**components,quality_score_cap=cap,quality_score_100=min(cap,sum(components.values())),
                loadability_class='D — reconstruction not yet audited' if main else 'E — full source not verified',full_model_loadable='Not tested',
                quality_rationale=rationale+' '+source.get('loadability_evidence',''),extraction_readiness='Requires input-table and diet-matrix audit',
                geometry=geometry,geometry_method=method,geometry_confidence=confidence,target_coverage_ratio=None,
                geometry_note=assignment.get('geometry_note',''),recommendation=assignment['coverage_note'])

def build_catalog(root):
    original=read_json(root/'inputs/original_catalog.json'); selected=read_json(root/'inputs/global_estimation.json')
    research=[read_json(path) for pattern in ('eez_*.json','lme_*.json') for path in sorted((root/'research').glob(pattern))]
    corrections=defaultdict(list)
    for result in research:
        for update in result.get('existing_source_updates',[]):
            corrections[update['article_id']].append(update)
    for old in original['articles']:
        for update in corrections.get(old['article_id'],[]):
            for field in ['title','authors','publication_year','doi','landing_page','functional_groups']:
                if field in update:
                    old['legacy_'+field]=old.get(field);old[field]=update[field]
            old['correction_notes']=old.get('correction_notes','')+' '+update.get('notes',update.get('correction_note',''))
            if update.get('geometry_bbox'):
                old.update(geometry=mapping(box(*update['geometry_bbox'])),geometry_confidence='low',geometry_method='Published study bounds, approximate rectangle',coverage_class='subregional',target_coverage_ratio=None)
            if update.get('clear_legacy_geometry'):
                old.update(geometry=None,geometry_confidence='unavailable',geometry_method='Legacy approximate footprint removed pending geographic verification',coverage_class='subregional',target_coverage_ratio=None,spatial_fit_score_15=7)
        if old['article_id'] in ('PCA-2016','GUI-2004'):
            old.update(geometry=None,geometry_confidence='unavailable',geometry_method='Legacy geographic assignment requires review',target_coverage_ratio=None,coverage_class='subregional' if old['article_id']=='PCA-2016' else 'geographic_assignment_unverified')
            old['spatial_fit_score_15']=7 if old['article_id']=='PCA-2016' else 0
            old['recommendation']=old.get('correction_notes','').strip()
        if old['article_id']=='KER-2005' and old['unit_id'].startswith('HS_'):
            old.update(geometry=None,geometry_confidence='unavailable',geometry_method='Kerguelen EEZ study; no demonstrated high-seas footprint',target_coverage_ratio=None,coverage_class='basin_proxy',spatial_fit_score_15=3,
                       recommendation='This model concerns the Kerguelen EEZ. Retained here only as a regional proxy; direct high-seas coverage has not been demonstrated.')
    selected_ids={r['unit_id'] for r in selected['regions']}
    features=read_json(root/'inputs/selected_regions.geojson')['features']
    geometry_rows=[dict(f['properties'],geometry=f['geometry']) for f in features]
    select_regions(selected['regions'],geometry_rows)
    if {r['unit_id'] for r in geometry_rows}!=selected_ids:
        raise ValueError('Selected polygon set differs from Global Estimation')
    with (root/'inputs/selected_regions.csv').open(encoding='utf-8-sig') as stream:
        if {r['unit_id'] for r in csv.DictReader(stream)}!=selected_ids:
            raise ValueError('Selected-region CSV differs from Global Estimation')
    geoms={r['unit_id']:r for r in geometry_rows};oldregions={r['unit_id']:r for r in original['regions']}
    regions=[]
    for row in selected['regions']:
        r=dict(oldregions.get(row['unit_id'],{}));r.update(row)
        r['geometry']=geoms[r['unit_id']]['geometry'];r['region_type']='High Seas' if r['unit_id'].startswith('HS_') else row['region_type']
        point=shape(r['geometry']).representative_point()
        if 'marker_lat' not in r:r.update(marker_lat=point.y,marker_lon=point.x)
        r.update(ppr=row['ppr_species'],ppr_species_2019=row['ppr_species'],geometry_source='Selected Sea Around Us polygon from PPR Global Estimation release',search_status=r.get('search_status','pending_search'))
        regions.append(r)
    regions=rank_regions(regions);byid={r['unit_id']:r for r in regions}
    total=math.fsum(r['ppr'] for r in regions if r['ppr'] is not None)
    if not math.isclose(total,selected['total_ppr'],rel_tol=1e-12):raise ValueError('PPR total differs from workbook')
    for row in selected['regions']:
        if byid[row['unit_id']]['ppr_rank']!=row['rank_selected_ppr']:raise ValueError('Rank differs from workbook')
    # Validate the historic archive selection before extending the display set.
    # Its scientific totals and ranks remain available as explicit subset metadata.
    for region in regions:
        region.update(curated_archive_member=True, curated_ppr_rank=region['ppr_rank'])
    annual=defaultdict(dict)
    with (root/'inputs/annual_regions.csv').open(encoding='utf-8-sig') as stream:
        for row in csv.DictReader(stream):
            annual[row['year']][row['unit_id']]=[float(row['ppr_species']) if row['ppr_species'] else None,float(row['total_catch_tonnes']) if row['total_catch_tonnes'] else None,row['source_data_status']]
    identities = display_geographies(root)
    display_ids = {row['unit_id'] for row, _ in identities}
    if not selected_ids <= display_ids:
        raise ValueError('Curated ecosystems missing from source identity inventory')
    for year, values in annual.items():
        if set(values) != display_ids:
            raise ValueError(f'Annual ecosystem identities differ from display inventory: {year}')
    for row, geographic in identities:
        if row['unit_id'] in selected_ids:
            continue
        ppr, catch, status = annual[str(selected['year'])][row['unit_id']]
        point = shape(geographic['geometry']).representative_point()
        regions.append(dict(row, **geographic, region_name=row['name'],
                            marker_lat=point.y, marker_lon=point.x,
                            ppr=ppr, ppr_species_2019=ppr, total_catch_tonnes=catch,
                            curated_archive_member=False, curated_ppr_rank=None,
                            search_status='not_in_curated_archive',
                            search_notes='This ecosystem is outside the curated article archive; no article search is claimed.',
                            **{'data availability':status}))
    regions=rank_regions(regions);byid={r['unit_id']:r for r in regions}
    files=read_json(root/'inputs/recovered_files.json')
    attempts=[]
    for path in sorted((root/'research/downloads').glob('*.json')):
        result=read_json(path);files.extend(result['files']);attempts.extend(result['attempts'])
    review_path=root/'research/file_identity_review.json'
    reviews=read_json(review_path)['reviewed'] if review_path.exists() else []
    for result in research:reviews.extend(result.get('file_identity_reviews',[]))
    identity={(r['article_id'],r['sha256']):r for r in reviews}
    for f in files:
        review=identity.get((f['article_id'],f['sha256']))
        if review:
            f['identity_status']=review['identity_status'];f['identity_notes']=review.get('notes','')
            for key in ['material_kind','file_label']:
                if review.get(key):f[key]=review[key]
            if review.get('recommended_role'):
                f['original_role']=f['role'];f['role']=review['recommended_role']
            if review['identity_status'] in ('mismatch','uncertain'):f['status']='identity_'+review['identity_status']
    unique={}
    for f in files:
        unique[(f['article_id'],f['sha256'],f['role'])]=f
    files=list(unique.values());by_source=defaultdict(list)
    for f in files:by_source[f['article_id']].append(f)
    sources={a['article_id']:a for a in original['articles']};articles=[]
    for old in original['articles']:
        if old['unit_id'] not in selected_ids:continue
        if any(old['unit_id'] in update.get('remove_assignments',[]) for update in corrections.get(old['article_id'],[])):continue
        a=dict(old);a['source_article_id']=a['article_id'];a['article_id']=a['source_article_id']+'__'+a['unit_id'];a['provenance']='Inherited from final all-84 catalog; original bibliographic and footprint claims retained'
        articles.append(a)
    searches=[]
    for result in research:
        sources.update({a['article_id']:a for a in result['articles']})
    # Deduplicate the same new publication returned by independent region searches.
    doi_ids={};aliases={}
    for aid,source in sources.items():
        doi=(source.get('doi') or '').lower().replace('https://doi.org/','').strip()
        if doi:
            canonical=doi_ids.setdefault(doi,aid)
            if canonical!=aid:aliases[aid]=canonical
    for alias,canonical in aliases.items():
        by_source[canonical].extend(by_source[alias])
        for field in ['loadability_evidence','documentation_evidence','notes']:
            parts=[sources[canonical].get(field,''),sources[alias].get(field,'')]
            sources[canonical][field]=' '.join(dict.fromkeys(p for p in parts if p))
        sources[canonical]['source_urls']=list(dict.fromkeys(sources[canonical].get('source_urls',[])+sources[alias].get('source_urls',[])))
    for result in research:
        for search in result['regions']:
            unit=search['unit_id']
            if unit not in selected_ids:raise ValueError(f'Research outside selected set: {unit}')
            searches.append(search);byid[unit].update(search_status=search['search_status'],search_notes=search['notes'])
            for assignment in search['assignments']:
                aid=assignment.get('existing_article_id') or assignment['article_id']
                aid=aliases.get(aid,aid)
                source=sources.get(aid)
                if source is None:raise ValueError(f'Unknown source {aid}')
                if assignment.get('existing_article_id'):
                    a=dict(source)
                    a.update(target_coverage_ratio=None,recommendation=assignment['coverage_note'],geometry_note=assignment.get('geometry_note',''))
                    # An inherited LME boundary may be just a proxy for a local study.
                    # Only explicitly documented EEZ assignments receive a displayed footprint.
                    a['geometry']=None;a['geometry_confidence']='unavailable';a['geometry_method']='Study boundary not recovered for this EEZ assignment'
                    if assignment.get('geometry_bbox'):
                        a.update(geometry=mapping(box(*assignment['geometry_bbox'])),geometry_confidence='low',geometry_method='Approximate reported study bounds')
                    elif assignment['coverage_class'] in ('whole_eez','whole_lme'):
                        a.update(geometry=byid[unit]['geometry'],geometry_confidence='low',geometry_method='Selected EEZ used as intended study envelope')
                    a['spatial_fit_score_15']={'whole_eez':15,'whole_lme':15,'subregional':7,'basin_proxy':3}[assignment['coverage_class']]
                    a['quality_score_100']=min(a.get('quality_score_cap',58),sum(a.get(k,0) for k in ['model_loadability_score_55','documentation_score_20','spatial_fit_score_15','recency_validation_score_10']))
                    a['quality_rationale']='Inherited loadability and documentation assessment; spatial fit rescored for this EEZ. '+assignment['coverage_note']
                else:a=new_article(source,assignment,byid[unit],by_source[aid])
                a.update(source_article_id=aid,article_id=aid+'__'+unit,unit_id=unit,region_name=byid[unit]['region_name'],coverage_class=assignment['coverage_class'],coverage_note=assignment['coverage_note'],provenance='Expanded ecosystem literature search 2026-09-04')
                articles.append(a)
    if len({a['article_id'] for a in articles})!=len(articles):raise ValueError('Duplicate article-to-region assignment')
    for a in articles:
        aid=aliases.get(a['source_article_id'],a['source_article_id']);a['source_article_id']=aid
        material=by_source[aid];verified=list({(f['sha256'],f['role']):f for f in material if f['status']=='downloaded_verified'}.values())
        a['legacy_full_model_loadable']=a.get('full_model_loadable')
        a['full_model_loadable']='Not load-tested in this project'
        a['downloaded_file_count']=len(verified);a['material_files']=verified;a['region_rank']=byid[a['unit_id']]['ppr_rank']
        a['download_status']='downloaded_verified' if verified else 'no_verified_file'
        a['main_file_status']='downloaded_verified' if any(f['role']=='main' for f in verified) else 'no_verified_main_file'
        a['download_failure_reason']=None if verified else 'No source file verified in this archive. See source link and retrieval log; this is not proof that the material is unavailable everywhere.'
        if a.get('provenance','').startswith('Inherited') and a.get('main_file_status')=='downloaded_verified' and a.get('quality_score_cap',0)<=25:
            a.update(model_loadability_score_55=20,documentation_score_20=10,quality_score_cap=58,loadability_class='D — readable source recovered; reconstruction not audited')
            a['quality_score_100']=min(58,sum(a.get(k,0) for k in ['model_loadability_score_55','documentation_score_20','spatial_fit_score_15','recency_validation_score_10']))
            a['quality_rationale']='Newly recovered readable source; full parameter and diet completeness has not been audited. Provisional loadability 20/55, documentation 10/20; geographic and recency components retained.'
        if aid in ('NZ-2021-TBGB','MHI-2021') and any(f['role']=='model_files' for f in verified):
            a.update(model_loadability_score_55=35,documentation_score_20=15,quality_score_cap=72,loadability_class='C — parameter-bearing tables verified; model import not tested')
            a['quality_score_100']=min(72,sum(a.get(k,0) for k in ['model_loadability_score_55','documentation_score_20','spatial_fit_score_15','recency_validation_score_10']))
            a['quality_rationale']='Basic parameters and diet tables are present in the downloaded source archive. Full reconstruction, model balance and native EwE loading have not been verified. '+sources[aid].get('loadability_evidence','')
        if not verified:
            a['quality_score_100']=min(25,a.get('quality_score_100',0));a['quality_score_cap']=25
        if a['source_article_id'] in ('PCA-2016','GUI-2004','KER-2005'):
            a['quality_score_100']=min(a.get('quality_score_cap',58),sum(a.get(k,0) for k in ['model_loadability_score_55','documentation_score_20','spatial_fit_score_15','recency_validation_score_10']))
        if a.get('correction_notes'):
            a['quality_rationale']=a.get('quality_rationale','')+' Bibliographic/spatial correction: '+a['correction_notes']
        for update in corrections.get(aid,[]):
            if update.get('input_table_audit') and verified:
                a.update(model_loadability_score_55=35,documentation_score_20=18,quality_score_cap=76,loadability_class='C — parameter and diet tables inspected; model import not tested',extraction_readiness='Parameter and diet tables located; transcription and balance audit required')
                a['quality_score_100']=min(76,sum(a.get(k,0) for k in ['model_loadability_score_55','documentation_score_20','spatial_fit_score_15','recency_validation_score_10']))
                a['quality_rationale']=update['input_table_audit']+' Full model import and numerical reconstruction remain untested.'
        a['article_dir']=f"archive/regions/{a['unit_id']}/{a['source_article_id']}"
        own_attempts=[t for t in attempts if aliases.get(t['article_id'],t['article_id'])==aid]
        a['legacy_download_attempt_count']=a.get('download_attempt_count')
        a['download_attempt_count']=len(own_attempts)
        a['download_attempt_summary']=f'{len(own_attempts)} actual retrieval requests logged in this project.'
    zotero_path=root/'research/zotero_sources.json'
    zotero=read_json(zotero_path) if zotero_path.exists() else {'items':[]}
    for item in zotero['items']:
        aid=aliases.get(item['article_id'],item['article_id'])
        for a in articles:
            if a['source_article_id']!=aid:continue
            if item.get('match_status')=='mismatch':
                a['zotero_key']=None;a['zotero_lookup_note']=item.get('notes','Mismatched library item excluded')
            else:
                a.update(zotero_key=item['zotero_key'],zotero_doi=item.get('doi'),zotero_url=item.get('url'),zotero_lookup_note=item.get('notes'))
    canonical_files={}
    for f in files:
        f=dict(f);f['original_article_id']=f['article_id'];f['article_id']=aliases.get(f['article_id'],f['article_id'])
        canonical_files[(f['article_id'],f['sha256'],f['role'])]=f
    files=list(canonical_files.values())
    for r in regions:
        related=[a for a in articles if a['unit_id']==r['unit_id']]
        r.update(article_count=len(related),best_quality_score=max([a['quality_score_100'] for a in related],default=0))
    return dict(regions=regions,articles=articles,files=files,searches=searches,download_attempts=attempts,source_aliases=aliases,source_corrections=dict(corrections),annual=annual,year=selected['year'],source_workbook='PPR_global_summary.xlsx / Global Estimation (curated subset); annual_regions.csv (all identities)',generated_on='2026-09-10',selected_total_ppr=total,curated_region_ids=sorted(selected_ids),all_total_ppr=math.fsum(r['ppr'] for r in regions if r['ppr'] is not None))
