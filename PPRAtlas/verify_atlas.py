"""Verify all display identities and the separate curated archive and history."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse,unquote
import hashlib,json,math
from bs4 import BeautifulSoup
from atlas.core import rank_regions

root=Path(__file__).resolve().parent
db=json.loads((root/'data/catalog.json').read_text(encoding='utf-8'))
source=json.loads((root/'inputs/global_estimation.json').read_text(encoding='utf-8'))
ids={r['unit_id'] for r in source['regions']}
display_ids={u['unit_id'] for folder in ('global_output','eez_output')
             for u in json.loads((root.parent/'SeaAroundUsExtraction'/folder/'tables/units.json').read_text(encoding='utf-8'))}
assert len(db['regions'])==len(display_ids)==366
assert {r['unit_id'] for r in db['regions']}==display_ids
assert set(db['curated_region_ids'])==ids and len(ids)==167
curated=[r for r in db['regions'] if r['curated_archive_member']]
assert {r['unit_id'] for r in curated}==ids
assert Counter(r['region_type'] for r in curated)=={'LME':66,'EEZ':84,'High Seas':17}
assert Counter(r['region_type'] for r in db['regions'])=={'LME':66,'EEZ':282,'High Seas':18}
curated_ranks={r['unit_id']:r['rank_selected_ppr'] for r in source['regions']}
assert all(r['curated_ppr_rank']==curated_ranks[r['unit_id']] for r in curated)
assert all(r['curated_ppr_rank'] is None and r['article_count']==0 for r in db['regions'] if not r['curated_archive_member'])
assert {r['unit_id'] for r in db['searches']}=={i for i in ids if i.startswith(('EEZ_','LME_'))}
assert len(db['searches'])==150 and all(r['queries'] for r in db['searches'])
assert len(db['annual'])==70
history_checks={}
for year,values in db['annual'].items():
    assert set(values)==display_ids
    assert all(values[unit][:2]==[None,None] for unit in ('HS_018','LME_064'))
    ranks=rank_regions([{'unit_id':i,'ppr':v[0]} for i,v in values.items()])
    known=[r for r in ranks if r['ppr'] is not None]
    assert math.isclose(sum(r['global_ppr_share'] for r in known),1,abs_tol=1e-12)
    assert math.isclose(known[-1]['cumulative_ppr_share'],1,abs_tol=1e-12)
    if year in ('1950','1985','2019'):
        history_checks[year]={'total':math.fsum(r['ppr'] for r in known),'missing':len(ranks)-len(known),'first_five':[r['unit_id'] for r in ranks[:5]]}
assert math.isclose(history_checks['2019']['total'],db['all_total_ppr'],rel_tol=1e-12)
assert math.isclose(math.fsum(db['annual']['2019'][unit][0] for unit in ids if db['annual']['2019'][unit][0] is not None),source['total_ppr'],rel_tol=1e-12)
assert math.isclose(db['selected_total_ppr'],source['total_ppr'],rel_tol=1e-12)
verified=0
for f in db['files']:
    path=(root/f['relative_path']).resolve()
    assert path.is_relative_to(root) and path.is_file()
    assert hashlib.sha256(path.read_bytes()).hexdigest()==f['sha256']
    if f['status']=='downloaded_verified':verified+=1
for a in db['articles']:
    assert a['unit_id'] in ids
    assert a['downloaded_file_count']==len(a['material_files'])
    for f in a['material_files']:
        fp=(root/f['relative_path']).resolve()
        assert fp.parent==(root/a['article_dir']).resolve()
        assert hashlib.sha256(fp.read_bytes()).hexdigest()==f['sha256']
    assert all(f['status']=='downloaded_verified' for f in a['material_files'])
    if not a['material_files']:assert a['quality_score_100']<=25
    if a['unit_id'].startswith('EEZ_'):assert a['target_coverage_ratio'] is None
    assert a['full_model_loadable']!='Yes'
    assert a['download_attempt_count']>0, a['source_article_id']
    assert (root/a['article_dir']/'README.md').is_file()
    assert (root/a['article_dir']/'footprint.geojson').exists()==bool(a.get('geometry'))
assert len({a['article_id'] for a in db['articles']})==len(db['articles'])
assert {p.parent.resolve() for p in (root/'archive/regions').glob('*/*/metadata.json')}=={(root/a['article_dir']).resolve() for a in db['articles']}
linked_files=0
for file in [root/'archive/index.html']:
    doc=BeautifulSoup(file.read_text(encoding='utf-8'),'html.parser')
    for a in doc.select('a[href]'):
        href=a['href'];parts=urlparse(href)
        if parts.scheme or not parts.path:continue
        assert (file.parent/unquote(parts.path)).resolve().is_file(),href
        linked_files+=1
paths=[p for p in root.rglob('*') if p.is_file() and '.venv' not in p.parts and '__pycache__' not in p.parts]
report={'selection_matches_workbook':True,'all_84_eezs_searched':True,'all_66_lmes_searched':True,'article_folder_copies_hash_verified':sum(len(a['material_files']) for a in db['articles']),'all_distinct_articles_have_real_download_attempts':len({a['source_article_id'] for a in db['articles']}),'annual_sets_verified':70,'sample_year_checks':history_checks,'file_records_hash_verified':len(db['files']),'verified_file_records':verified,'verified_unique_files':len({f['sha256'] for f in db['files'] if f['status']=='downloaded_verified'}),'archive_local_links_verified':linked_files,'longest_delivery_path':max(len(str(p)) for p in paths)}
report.update(display_ecosystems=len(display_ids),curated_archive_ecosystems=len(ids),
              all_display_identities_verified=True,curated_subset_matches_workbook=True,
              no_catch_identities=['HS_018','LME_064'])
(root/'data/validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
