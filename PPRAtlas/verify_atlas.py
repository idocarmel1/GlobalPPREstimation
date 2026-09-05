"""Verify the delivered selection, history, evidence links, files and archive paths."""
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
assert len(db['regions'])==len(ids)==167
assert {r['unit_id'] for r in db['regions']}==ids
assert Counter(r['region_type'] for r in db['regions'])=={'LME':66,'EEZ':84,'High Seas':17}
assert {r['unit_id'] for r in db['searches']}=={i for i in ids if i.startswith(('EEZ_','LME_'))}
assert len(db['searches'])==150 and all(r['queries'] for r in db['searches'])
assert len(db['annual'])==70
history_checks={}
for year,values in db['annual'].items():
    assert set(values)==ids
    ranks=rank_regions([{'unit_id':i,'ppr':v[0]} for i,v in values.items()])
    known=[r for r in ranks if r['ppr'] is not None]
    assert math.isclose(sum(r['global_ppr_share'] for r in known),1,abs_tol=1e-12)
    assert math.isclose(known[-1]['cumulative_ppr_share'],1,abs_tol=1e-12)
    if year in ('1950','1985','2019'):
        history_checks[year]={'total':math.fsum(r['ppr'] for r in known),'missing':len(ranks)-len(known),'first_five':[r['unit_id'] for r in ranks[:5]]}
assert math.isclose(history_checks['2019']['total'],source['total_ppr'],rel_tol=1e-12)
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
(root/'data/validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
