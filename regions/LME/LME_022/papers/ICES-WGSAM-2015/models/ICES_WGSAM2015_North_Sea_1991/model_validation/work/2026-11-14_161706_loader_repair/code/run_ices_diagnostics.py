"""Bounded authorized direct diagnostics; no canonical/workbook/publication writes."""
from pathlib import Path
import sys, json, hashlib, gzip, math, platform, warnings, os, subprocess
from datetime import datetime, timezone

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').is_file())
ENGINE_ROOT = Path(os.environ.get('LME022_ENGINE_ROOT', str(ROOT))).resolve()
sys.path.insert(0, str(ENGINE_ROOT))
from tools.scientific_helpers.sppr import method_coverage as mc

MODEL = ROOT / 'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991/model.json'
OUT = MODEL.parent / 'results/diagnostics/2026-11-14_loader_repair'
FLAGS = {
    'constructor': {'underdetermined': False, 'zero_catch': False,
        'zero_biomass_accum': False, 'default_gs': False,
        'normalize_DC': False, 'DC_tol': .001,
        'balance_BA_after_DC_normalization': False,
        'use_ee_floor': True, 'ee_floor': .1, 'ee_threshold': .1},
    'diagnostics': {'det_collapse_mode': 'never', 'det_open_mode': 'none',
        'det_theta': 1, 'det_external_sppr': 0},
    'method_timeout_seconds': 180,
}
KEYS = ['new_GE', 'new_TE_EEfix', 'new_WithEgestion']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return p
def plain(v):
    try:
        value = float(v)
        return value if math.isfinite(value) and value != -9999 else None
    except (TypeError, ValueError): return None

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    before = sha(MODEL)
    source = json.loads(MODEL.read_text(encoding='utf-8'))
    _, ModelData, _, _ = mc._engine()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        loaded = ModelData(str(MODEL))
    fields = ['biomass', 'pb', 'qb', 'ee', 'gs', 'biomass_accum', 'tl', 'detritus_import']
    scalar = []
    routing = []
    unknown_biology = []
    raw_sums = []
    for group in source['group']:
        seq = int(group['group_seq'])
        kind = loaded.groups_data.loc[seq, 'trophic_info']
        for field in fields:
            actual = plain(loaded.groups_data.loc[seq, field]) if field in loaded.groups_data else None
            original = plain(group.get(field))
            scalar.append({'group_id': seq, 'group_name': group['group_name'], 'field': field,
                'source_literal': group.get(field), 'source_value': original,
                'loaded_value': actual, 'changed': original != actual})
            if field in ['biomass', 'pb', 'qb', 'ee'] and original is None:
                unknown_biology.append({'group_id': seq, 'group_name': group['group_name'], 'type': kind, 'field': field})
        for pool, literal in group.get('detritus_fate_by_pool', {}).items():
            actual = plain(loaded.det_fate.loc[seq, int(pool)])
            original = plain(literal)
            routing.append({'group_id': seq, 'group_name': group['group_name'], 'pool_id': int(pool),
                'source_fraction': original, 'loaded_fraction': actual, 'changed': original != actual})
        diets = (group.get('diet_descr') or {}).get('diet') or []
        raw = sum(float(cell['proportion']) for cell in diets) + float(group.get('diet_imp', 0))
        raw_sums.append({'group_id': seq, 'type': kind, 'canonical_sum': raw,
            'loader_sum': float(loaded.DC.loc[seq].sum())})
    loader_audit = {'canonical_model_sha256': before,
        'model_id': MODEL.parent.name, 'engine_hashes': mc.engine_identity(),
        'constructor_requested': FLAGS['constructor'], 'modeldata_only_at_this_stage': True,
        'source_group_count': 69, 'loaded_group_count': len(loaded.groups_data),
        'loaded_metadata': {'model_name': str(loaded.model_name), 'model_year': str(loaded.model_year),
            'lme': int(loaded.lme)},
        'group_columns': list(loaded.groups_data.columns), 'scalar_ledger': scalar,
        'diet_import_structural_zeros': [int(x) for x in getattr(loaded, 'diet_import_structural_zeros', [])],
        'discard_returns': mc.encode_lossless(getattr(loaded, 'discard_returns', None)),
        'discard_returns_metadata': mc.encode_lossless(getattr(loaded, 'discard_returns_metadata', {})),
        'unknown_source_biology': unknown_biology, 'detritus_routing_ledger': routing,
        'diet_sums': raw_sums, 'warnings': [str(w.message) for w in caught],
        'interpretation': [
            'Global source-preserving loader/accounting correction; normal maintained loader with no model-local adaptation.',
            'Standalone source routing, including explicit zeros, is read by the repaired shared loader; field-by-field reconciliation is retained.',
            'Source parameters and missingness remain canonical; only documented nonfeeding structural diet conventions apply in runtime.',
            'Known detritus BA is retained before the EE floor. The floor retains its established effective detritus-stock closure, which is not observed accumulation or a recovered native export. Operational detritus EE=1 remains a calculation convention.',
            'No LIM, invented catch/BA/GS default, runtime diet normalization, or normalization-induced BA correction is requested.',
            'EE floor ON at .1 is an explicit current runtime assumption; it is not source correction or approval.']}
    save('source_loader_audit.json', loader_audit)
    print('Loader audited; running only GE, TE, With Egestion.', flush=True)
    answer = mc.compute_methods(MODEL, FLAGS, KEYS, OUT, progress=lambda s: print(s, flush=True))
    save('run_manifest.json', {'schema_version': 1, 'timestamp': datetime.now(timezone.utc).isoformat(),
        'scope': 'Three direct diagnostic options only; no canonical or workbook changes, no publication.',
        'code_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ENGINE_ROOT,text=True).strip(),
        'engine_root_role': 'Isolated committed global repair branch',
        'authorization': 'User explicitly requested global loader/accounting repair, all three ICES reruns and revised review files, 2026-11-14.',
        'canonical_unchanged': sha(MODEL) == before, 'answer': answer})
    summary = {'model_id': MODEL.parent.name, 'canonical_model_sha256': before,
        'canonical_unchanged': sha(MODEL) == before, 'flags': FLAGS,
        'methods': [], 'files': [], 'source_loader_changes': {
            'scalar': [x for x in scalar if x['changed']],
            'routing': [x for x in routing if x['changed']]}}
    for key in KEYS:
        p = OUT / f'{key}.json.gz'
        doc = json.loads(gzip.decompress(p.read_bytes()))
        diag = doc.get('diagnostics') or {}
        matrix = doc.get('source_matrix')
        negative = []
        checks = {}
        if matrix:
            names = {str(g['id']): g['name'] for g in doc['groups']}
            idx, cols, data = matrix['index'], matrix['columns'], matrix['data']
            for i, row in enumerate(data):
                for j, value in enumerate(row):
                    if isinstance(value, (int, float)) and value < 0:
                        negative.append({'source_id': cols[j], 'source_name': names.get(str(cols[j])),
                            'group_id': idx[i], 'group_name': names.get(str(idx[i])), 'value': value,
                            'comparison_tolerance': 0})
            checks = {'shape': matrix['shape'], 'unique_axes': len(set(idx)) == len(idx) and len(set(cols)) == len(cols),
                'mask_counts': {k: sum(sum(row) for row in mask) for k, mask in matrix['masks'].items()},
                'negative_source_count': len({x['source_id'] for x in negative}),
                'diagnostic_negative_count': diag.get('divergence', {}).get('n_negative_sources')}
        summary['methods'].append({'method': key, 'execution_status': doc['status'],
            'reason': doc.get('reason'), 'diagnostic': diag, 'exception': doc.get('exception'),
            'constructor_outcome': doc.get('constructor_outcome') if doc['status'] == 'NOT_RUN' else None,
            'negative_entries': negative, 'matrix_checks': checks,
            'runtime_before_sha256': doc.get('runtime_before_sha256'),
            'runtime_after_sha256': doc.get('runtime_after_sha256'),
            'reconciliation': doc.get('reconciliation'), 'annual_status': doc.get('annual_status')})
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name not in ['summary.json', 'evidence_index.json', 'completeness.json']:
            summary['files'].append({'path': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size})
    save('summary.json', summary)
    index = {'schema_version': 1, 'run_id': '2026-11-14_161706_loader_repair',
        'region_id': 'LME_022', 'unit_id': 'LME_022', 'model_id': MODEL.parent.name,
        'variant_id': 'published_Rpath_port_repaired_global_loader_ee_floor_0.1',
        'source_identity': {'canonical_model_sha256': before},
        'computational_input_identity': {'canonical_model_sha256': before,
            'constructor': answer['constructor'], 'engine_hashes': answer['engine_hashes']},
        'methods': KEYS,
        'required_roles': ['canonical_model', 'source_loader_audit', 'constructor', 'direct_GE', 'direct_TE', 'direct_WithEgestion', 'summary', 'run_manifest'],
        'artifacts': [{'role': 'canonical_model', 'path': '../../../model.json', 'sha256': before, 'availability': 'present'}],
        'reconciliation': {'canonical_unchanged': sha(MODEL) == before}}
    rolemap = {'source_loader_audit.json': 'source_loader_audit', 'constructor.json.gz': 'constructor',
        'new_GE.json.gz': 'direct_GE', 'new_TE_EEfix.json.gz': 'direct_TE',
        'new_WithEgestion.json.gz': 'direct_WithEgestion', 'summary.json': 'summary', 'run_manifest.json': 'run_manifest'}
    for name, role in rolemap.items():
        p = OUT / name
        index['artifacts'].append({'role': role, 'path': name, 'sha256': sha(p), 'availability': 'present'})
    save('evidence_index.json', index)
    print(json.dumps([{'method': x['method'], 'execution': x['execution_status'],
        'status': x['diagnostic'].get('status'), 'reason': x['reason']} for x in summary['methods']]), flush=True)

if __name__ == '__main__': main()
