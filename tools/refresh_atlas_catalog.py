"""Refresh display geography without recreating or mutating the article archive."""
import json
from pathlib import Path
import sys

from atomic_output import write_text_atomic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'PPRAtlas'))
from atlas.catalog import build_catalog


def refresh_catalog(root=ROOT):
    """Preserve localized evidence while replacing the display catalog atomically.

    Article additions, removals, source changes, or boundary changes require the
    archive build workflow. This geography-only refresh must never silently
    relabel existing archived evidence or copy a new source into its place.
    """
    atlas_root = Path(root) / 'PPRAtlas'
    path = atlas_root / 'data/catalog.json'
    previous = json.loads(path.read_text(encoding='utf-8'))
    current = build_catalog(atlas_root)
    old_articles = {article['article_id']: article for article in previous['articles']}
    if set(old_articles) != {article['article_id'] for article in current['articles']}:
        raise ValueError('Article assignments changed; use the archive build workflow')
    for article in current['articles']:
        old = old_articles[article['article_id']]
        signature = lambda record: sorted((file['sha256'], file['role']) for file in record['material_files'])
        same_geometry = json.dumps(article.get('geometry'), sort_keys=True) == json.dumps(old.get('geometry'), sort_keys=True)
        if signature(article) != signature(old) or not same_geometry or not old.get('footprint_key'):
            raise ValueError(f"Verified archive evidence changed: {article['article_id']}")
        article['material_files'] = old['material_files']
        article['footprint_key'] = old['footprint_key']
    write_text_atomic(path, json.dumps(current, ensure_ascii=False, indent=2, allow_nan=False))
    return current


if __name__ == '__main__':
    catalog = refresh_catalog()
    print(json.dumps({'display_ecosystems':len(catalog['regions']),
                      'curated_ecosystems':len(catalog['curated_region_ids']),
                      'article_assignments':len(catalog['articles'])}))
