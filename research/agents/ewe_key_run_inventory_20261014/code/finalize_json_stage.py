"""Record canonical snapshot creation without registration or publication."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[4]
STUDY = ROOT / 'research/agents/ewe_key_run_inventory_20261014'
PACKAGES = [
    ('LME_022', 'ICES-WGSAM-2015', 'ICES_WGSAM2015_North_Sea_1991', 'published North Sea Rpath port snapshot; materially different from accepted native EwE configuration'),
    ('LME_023', 'ICES-WGSAM-2016', 'ICES_WGSAM2016_Baltic_Proper_2004', 'published Baltic Proper Rpath port snapshot; materially different from accepted native EwE configuration'),
    ('LME_024', 'ICES-WGSAM-2019-Irish-Sea', 'ICES_WGSAM2019_Irish_Sea_1973', 'Irish Sea published Table 0.1 baseline extraction; accepted final native equivalence unresolved'),
]

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    spec = importlib.util.spec_from_file_location('evidence_checker', ROOT / 'tools/skills/paper-to-ppr/scripts/check_evidence.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    inventory = {'date': '2026-10-14', 'stage': 'canonical source snapshots created; registry, selections and map still on hold', 'packages': []}
    for unit, paper, model_id, identity in PACKAGES:
        folder = ROOT / 'regions/LME' / unit / 'papers' / paper
        model = folder / 'models' / model_id
        manifest_path = folder / 'source_manifest.json'
        manifest = read(manifest_path)
        for item in manifest['files']:
            assert digest(folder / item['path']) == item['sha256'], item['path']
        check = checker.check(model / 'extracted_tables/evidence/evidence_index.json')
        assert check['complete'], check
        fidelity = read(model / 'extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json')
        assert fidelity['numeric_value_and_missing_mask_match'] and not fidelity['errors']
        snapshot = read(model / 'model.json')
        record = {
            'unit_id': unit, 'model_id': model_id,
            'path': (model / 'model.json').relative_to(ROOT).as_posix(),
            'sha256': digest(model / 'model.json'), 'groups': len(snapshot['group']),
            'source_identity': identity, 'canonical_model_available': True,
            'native_ewe_database_available': False, 'accepted_native_equivalence': 'not established',
            'standard_import_tables': fidelity['standard_tables'],
            'companion_tables': fidelity['companion_tables'],
            'roundtrip_cells_checked': fidelity['cells_checked'],
            'numeric_value_and_missing_mask_match': True,
            'exact_value_and_missing_mask_match': fidelity['exact_value_and_missing_mask_match'],
            'max_numeric_difference': fidelity['max_numeric_difference'],
            'evidence_inventory': check, 'original_source_hashes_unchanged': True,
            'central_registration_applied': False, 'selection_applied': False,
            'map_updated': False, 'researcher_approval': 'not conferred',
        }
        inventory['packages'].append(record)
        metadata_path = folder / 'sources/metadata.json'
        metadata = read(metadata_path)
        metadata.update({
            'extraction_readiness': 'canonical source snapshot and eight standard import tables created; diagnostics retained; downstream readiness not approved',
            'model_file_status': 'canonical model.json available; accepted native EwE database not obtained',
            'canonical_model_path': f'models/{model_id}/model.json',
            'canonical_source_identity': identity,
            'accepted_native_equivalence': 'not established',
            'central_registration_status': 'not applied; map and selection updates remain on hold at user request',
        })
        write(metadata_path, metadata)
        manifest['publication'] = metadata
        manifest['stage'] = 'sources prepared and canonical source snapshot created; no registry, selection or map update'
        manifest['canonical_snapshot'] = {k: record[k] for k in ('path', 'sha256', 'source_identity', 'accepted_native_equivalence')}
        write(manifest_path, manifest)
        readme_path = folder / 'README.md'
        text = readme_path.read_text(encoding='utf-8')
        text = text.replace('Source preparation only: Project.xlsx, regional workbook selections, scientific inputs and generated map pages remain unchanged.', 'Canonical source extraction is complete. Project.xlsx, regional workbook selections, previously existing scientific inputs and generated map pages remain unchanged.')
        if unit == 'LME_024':
            text = text.replace(' A Rpath port is not the accepted native EwE software configuration.', '')
            text = text.replace('No official model-input or model-output CSV bundle was located for the Irish Sea; none was invented from unrelated data.', 'No original model CSV bundle was located. Eight standard import tables have now been extracted from the published report; they are derived tables, not a recovered native database.')
        if '## Canonical source snapshot' not in text:
            text += f'\n## Canonical source snapshot\n\n[model.json](models/{model_id}/model.json) now contains {len(snapshot["group"])} groups, with eight standard import tables and {fidelity["companion_tables"]} source companions under `extracted_tables/`. Its identity is **{identity}**. Missing values and source diagnostics remain explicit. This is an Ecopath data snapshot; it does not reproduce a complete accepted Ecosim scenario or confer researcher approval.\n\nSee [model notes](models/{model_id}/model_notes.md) and the [JSON creation report](../../../../../research/agents/ewe_key_run_inventory_20261014/JSON_CREATION_REPORT.md) for source differences, validation limits and the hold on publication.\n'
        readme_path.write_text(text, encoding='utf-8')
    write(STUDY / 'evidence/canonical_snapshot_inventory.json', inventory)
    print(json.dumps({'models': len(inventory['packages']), 'source_hashes_unchanged': True, 'inventory_checks_passed': True, 'roundtrip_numeric_and_missing_masks_preserved': True}))

if __name__ == '__main__':
    main()
