"""Physically relocate generated pages and every exposed local destination."""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from original_atlas_data import embedded


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ('href', 'src') and v:
                self.links.append(v)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--serve', action='store_true')
    args = parser.parse_args()
    relocated = BASE / 'work/final_page_relocation/relocated_repository'
    retained = BASE / 'verification/final_page_relocation'
    retained.mkdir(parents=True, exist_ok=True)
    relocated.mkdir(parents=True, exist_ok=True)
    files, links, external = set(), [], set()

    def add(href, parent, origin):
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc:
            assert parsed.scheme not in ('file',), (origin, href)
            external.add(href)
            return
        if not parsed.path:
            return
        target = (parent / unquote(parsed.path)).resolve()
        assert target.is_relative_to(ROOT), (origin, href)
        assert target.is_file(), (origin, href, str(target))
        rel = target.relative_to(ROOT).as_posix()
        files.add(rel)
        links.append({'origin': origin, 'href': href, 'resolved': rel})

    pages = ['interactive_map/index.html', 'interactive_map/trends.html', 'interactive_map/archive/index.html']
    for rel in pages:
        p = ROOT / rel
        files.add(rel)
        parsed = Links()
        parsed.feed(p.read_text(encoding='utf-8'))
        for href in parsed.links:
            add(href, p.parent, rel)
    catalog, _ = embedded(ROOT / pages[0], 'DB')
    series, _ = embedded(ROOT / pages[1], 'SERIES_DB')
    for article in catalog['articles']:
        for item in article.get('material_files', []):
            add(item['relative_path'], ROOT / 'interactive_map', article['article_id'])
    network = catalog['network']
    for unit, value in network['units'].items():
        for model in value.get('models', []):
            for key in ('workbook', 'source'):
                if model.get(key):
                    add(model[key], ROOT, f'{unit}/{model["id"]}/{key}')
    for unit, value in series['units'].items():
        if value.get('sources', {}).get('workbook'):
            add(value['sources']['workbook'], ROOT, f'{unit}/source workbook')
        for model in value.get('models', []):
            if model.get('workbook'):
                add(model['workbook'], ROOT, f'{unit}/{model["id"]}/trends workbook')
    add(catalog['source_workbook'], ROOT / 'interactive_map', 'Project workbook')
    add(network['npp_source'], ROOT, 'map annual NPP')
    add(series['npp_source'], ROOT, 'trends annual NPP')
    add('interactive_map/data/unidentified_taxa.json', ROOT, 'unidentified inventory')
    manifest = []
    for rel in sorted(files):
        src, dst = ROOT / rel, relocated / rel
        before = sha(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        assert sha(dst) == before == sha(src), rel
        manifest.append({'path': rel, 'sha256': before, 'bytes': src.stat().st_size})
    for link in links:
        assert (relocated / link['resolved']).is_file()
    receipt = {'recorded_utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS',
               'scope': 'Physical relocation of all statically rendered and dynamic local destinations exposed by map/trends/archive. External URLs classified, not re-fetched. Office package relocation is verified separately.',
               'relocated_root': str(relocated), 'files': manifest, 'links': links,
               'external_urls': sorted(external), 'count_files': len(files), 'count_links': len(links),
               'copied_bytes': sum(r['bytes'] for r in manifest),
               'source_page_hashes': {p: sha(ROOT / p) for p in pages}}
    (retained / 'verification.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('status', 'count_files', 'count_links', 'copied_bytes', 'relocated_root')}), flush=True)
    if args.serve:
        from open_map import make_server
        server = make_server(relocated, 0)
        url = f'http://127.0.0.1:{server.server_port}/interactive_map/index.html'
        (retained / 'server.json').write_text(json.dumps({'url': url, 'root': str(relocated)}, indent=2), encoding='utf-8')
        print(url, flush=True)
        try:
            server.serve_forever()
        finally:
            server.server_close()


if __name__ == '__main__':
    main()
