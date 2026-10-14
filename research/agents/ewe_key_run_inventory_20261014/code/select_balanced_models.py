"""Register and select the two authorized static snapshots using project writers."""
from pathlib import Path
from zipfile import ZipFile
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records, overview, sha, update_book
from tools.project_core.registry.discovery import discover_regions, discover_models
from tools.project_core.registry.writes import central_lock
from tools.project_core.calculations.regional import set_setting
from tools.project_core.validation.researcher_review import table_rows

STUDY = ROOT / 'research/agents/ewe_key_run_inventory_20261014'
TARGETS = [
    ('LME_022', 'ICES-WGSAM-2015', 'ICES_WGSAM2015_North_Sea_1991', 'North Sea', 1991, 'intended_full'),
    ('LME_023', 'ICES-WGSAM-2016', 'ICES_WGSAM2016_Baltic_Proper_2004', 'Baltic Proper', 2004, 'subregional'),
]
INDEPENDENT = [('Catch', 'Catch'), ('Classic PPR', 'Taxa'), ('Classic PPR', 'Annual'), ('NPP', 'NPP'), ('NPP', 'Provenance')]

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def table_identity(path):
    from hashlib import sha256
    result = {}
    with ZipFile(path) as archive:
        for sheet, name in INDEPENDENT:
            _, headers, _, data = table_rows(archive, sheet, name)
            result[sheet + '/' + name] = sha256(json.dumps([headers, [r for _, r in data]], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return result

def register():
    project = ROOT / 'Project.xlsx'
    fingerprint = sha(project)
    book = read_book(project, sheets=['Papers', 'Models & coverage'])
    models = records(book, 'Models & coverage', 'Models')
    conflicts = [r for r in models if r['unit_id'] in {t[0] for t in TARGETS} and r.get('researcher_review_status') == 'Validated by researcher']
    if conflicts:
        raise ValueError('User requested confirmation before replacing a verified regional model: ' + str(conflicts))
    baseline = {'date': '2026-10-14', 'authorization': 'User: select and update the map for the 2 balanced models',
                'project_sha256': fingerprint, 'registered_models_before': models,
                'registered_papers_before': records(book, 'Papers', 'Papers'),
                'region_hashes_before': {u: sha(p) for u, p in discover_regions(ROOT).items()},
                'canonical_hashes_before': {}, 'targets': {}}
    for unit, path in discover_regions(ROOT).items():
        for mid, model in discover_models(path.parent).items():
            baseline['canonical_hashes_before'][model.relative_to(ROOT).as_posix()] = sha(model)
    ph, pr = book['Papers']['Papers']
    mh, mr = book['Models & coverage']['Models']
    for unit, paper_id, mid, name, year, coverage in TARGETS:
        region = ROOT / 'regions/LME' / unit
        folder = region / 'papers' / paper_id
        model = folder / 'models' / mid / 'model.json'
        metadata = json.loads((folder / 'sources/metadata.json').read_text(encoding='utf-8'))
        manifest = json.loads((folder / 'source_manifest.json').read_text(encoding='utf-8'))
        current = overview(read_book(region / (unit + '.xlsx'), sheets=['Overview']))
        baseline['targets'][unit] = {'overview_before': current, 'independent_tables_before': table_identity(region / (unit + '.xlsx')),
                                    'model_id': mid, 'model_sha256': sha(model)}
        common = 'Published Rpath port snapshot; materially differs from the accepted native EwE configuration. Static source budget checks pass. Native database unavailable; detritus-routing import restrictions and loader departures retained. No project researcher approval or Ecopath PPR coefficients/matching.'
        p = {k: metadata.get(k) for k in ph}
        p.update(article_id=metadata['article_id'], source_article_id=paper_id,
                 region_dir=region.relative_to(ROOT).as_posix(), article_dir=folder.relative_to(ROOT).as_posix(),
                 coverage_class=coverage, target_coverage_ratio=None, selected=False,
                 loadability_class='Canonical Ecopath snapshot loads; calculation readiness pending',
                 full_model_loadable='Static JSON schema load checked; full accepted Ecosim configuration unavailable',
                 quality_rationale=common, recommendation='User-authorized regional default based on static mass balance; Rpath variant limits retained',
                 geometry_method='No article polygon registered', geometry_confidence=None,
                 geometry_note=metadata['modeled_footprint'] + '; exact LME overlap not measured; no inferred article polygon',
                 language='English', download_status='downloaded_verified',
                 supplement_status='Official output ZIP and output CSV/XLSX tables retained',
                 downloaded_file_count=len(manifest['files']),
                 loadability_evidence=(folder / 'models' / mid / 'model_notes.md').relative_to(ROOT).as_posix(),
                 documentation_evidence=(folder / 'README.md').relative_to(ROOT).as_posix(),
                 provenance='Online-source research and source-faithful JSON extraction, 2026-10-14; see research/agents/ewe_key_run_inventory_20261014/JSON_CREATION_REPORT.md',
                 source_urls=';'.join(sorted({str(f.get('url')) for f in manifest['files'] if f.get('url')})),
                 notes=common)
        m = dict(unit_id=unit, model_id=mid, model_path=model.relative_to(ROOT).as_posix(),
                 source_filename=model.name, selected=False, paper_ids=metadata['article_id'],
                 model_year=year, variant=name + ' published Rpath port snapshot', availability=common,
                 publication_year=metadata['publication_year'], model_years=str(year),
                 target_coverage_ratio=None, coverage_class=coverage, doi=metadata.get('doi'),
                 coverage_note=metadata['coverage_note'], production_eligible=False,
                 canonical_source_path=model.relative_to(ROOT).as_posix(), canonical_source_sha256=sha(model))
        assert not any(r['article_id'] == p['article_id'] for r in records(book, 'Papers', 'Papers')), 'Already registered paper'
        assert not any((r['unit_id'], r['model_id']) == (unit, mid) for r in records(book, 'Models & coverage', 'Models')), 'Already registered model'
        pr.append([p.get(k) for k in ph])
        mr.append([m.get(k) for k in mh])
    write_json(STUDY / 'evidence/balanced_selection_before.json', baseline)
    with central_lock(ROOT):
        assert sha(project) == fingerprint, 'Project changed during registration preparation'
        update_book(project, book)
    print('Registered exactly two source snapshots; researcher-review fields remain blank.', flush=True)

def select(unit):
    target = next(t for t in TARGETS if t[0] == unit)
    _, paper_id, mid, name, year, _ = target
    path = ROOT / 'regions/LME' / unit / (unit + '.xlsx')
    fingerprint = sha(path)
    book = read_book(path, sheets=['Overview'])
    set_setting(book, 'selected_model_id', mid)
    set_setting(book, 'selection_rationale', f'User selected this {name} {year} published Rpath snapshot on 2026-10-14 because its static mass-balance checks pass. It materially differs from the accepted native EwE key run; source routing restrictions and loader departures remain. Researcher approval and Ecopath PPR readiness are not established.')
    assert sha(path) == fingerprint, 'Region changed during selection preparation'
    update_book(path, book)
    print('Saved authorized Overview selection for ' + unit + '; regional refresh is required.', flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('operation', choices=['register', 'select'])
    ap.add_argument('--unit', choices=['LME_022', 'LME_023'])
    args = ap.parse_args()
    if args.operation == 'register':
        register()
    else:
        select(args.unit)
