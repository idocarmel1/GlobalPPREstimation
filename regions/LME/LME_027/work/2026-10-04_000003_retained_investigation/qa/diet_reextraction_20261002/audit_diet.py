"""Read-only native diet comparison; writes only dated regional audit evidence."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json
import shutil
import zipfile
import xml.etree.ElementTree as ET
import openpyxl

REGION = Path(__file__).resolve().parents[1]
ROOT = REGION.parents[1]
OUT = Path(__file__).resolve().parent
MID = '27_118_Northwest_Africa_(1987)'
MODEL = REGION / 'models' / MID / 'model.json'
SOURCE = REGION / 'papers/CAN-2009' / f'{MID}.json'
RUN = MODEL.parent / 'integration_20260928'
DOCX = REGION / f'Model_validation_{MID}.docx'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

inputs = [MODEL, SOURCE, REGION / 'LME_027.xlsx', DOCX, MODEL.parent / 'sppr_source.xlsx']
before = {rel(p): sha(p) for p in inputs}
native = json.loads(SOURCE.read_text(encoding='utf-8'))
canonical = json.loads(MODEL.read_text(encoding='utf-8'))
assert canonical == native, 'Canonical differs from retained source; stop and investigate.'
wb = openpyxl.load_workbook(REGION / 'LME_027.xlsx', read_only=True, data_only=False)
settings = {r[0]: r[1] for r in wb['Overview'].iter_rows(values_only=True) if len(r) >= 2 and r[0]}
wb.close()
assert settings['selected_model_id'] == MID
assert settings['model_path'] == f'models/{MID}/model.json'
ledger = json.loads((RUN / 'transformation_ledger.json').read_text(encoding='utf-8'))
runtime_changes = {(str(x['seq']), x['field']): x for x in ledger if x['field'].startswith('diet:')}
groups = {str(g['group_seq']): g for g in native['group']}
cells, sums = [], []
for gi, g in enumerate(canonical['group']):
    seq = str(g['group_seq'])
    diet = g.get('diet_descr', {}).get('diet', [])
    singleton_diet = isinstance(diet, dict)
    if singleton_diet:
        diet = [diet]
    total = Decimal(str(g['diet_imp']))
    for di, d in enumerate(diet):
        prey = str(d['prey_seq'])
        value = d['proportion']
        total += Decimal(str(value))
        transformation = runtime_changes.get((seq, 'diet:' + prey))
        cells.append({'consumer_seq': seq, 'consumer_name': g['group_name'],
            'prey_seq': prey, 'prey_name': groups[prey]['group_name'],
            'source_literal': value, 'canonical_literal': value,
            'source': rel(SOURCE), 'source_sha256': before[rel(SOURCE)],
            'source_cell': f'/group/{gi}/diet_descr/diet' + ('' if singleton_diet else f'/{di}') + '/proportion',
            'evidence_status': 'verified_native_export_literal; printed_final_table_unverified',
            'accepted_correction': None,
            'historical_runtime_transformation': transformation})
    imp_transform = runtime_changes.get((seq, 'diet:28'))
    cells.append({'consumer_seq': seq, 'consumer_name': g['group_name'],
        'prey_seq': 'Import', 'source_literal': g['diet_imp'],
        'canonical_literal': g['diet_imp'], 'source': rel(SOURCE),
        'source_sha256': before[rel(SOURCE)], 'source_cell': f'/group/{gi}/diet_imp',
        'evidence_status': 'verified_native_export_literal; printed_final_table_unverified',
        'accepted_correction': None, 'historical_runtime_transformation': imp_transform})
    sums.append({'consumer_seq': seq, 'consumer_name': g['group_name'],
        'real_prey_sum': str(total - Decimal(str(g['diet_imp']))),
        'import_literal': g['diet_imp'], 'source_total': str(total),
        'canonical_total': str(total), 'one_minus_total': str(Decimal(1) - total),
        'consumer_with_diet': any(Decimal(str(d['proportion'])) != 0 for d in diet) or Decimal(str(g['diet_imp'])) != 0,
        'researcher_rounding_review_status': 'pending; no approval inferred',
        'runtime_normalization_allowed': True})
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(DOCX) as z:
    doc = ET.fromstring(z.read('word/document.xml'))
paragraphs = [''.join(t.text or '' for t in p.findall('.//w:t', ns)) for p in doc.findall('.//w:p', ns)]
review_excerpt = [p for p in paragraphs if any(k in p.lower() for k in ('diet', 'normaliz', 'researcher', 'calculation choices'))]
archive = OUT / 'original_inputs' / before[rel(MODEL)]
archive.mkdir(parents=True, exist_ok=True)
for p, name in [(MODEL, 'canonical_model.json'), (SOURCE, 'retained_ecobase_source.json')]:
    dest = archive / name
    if dest.exists():
        assert sha(dest) == before[rel(p)], 'Existing archive has conflicting bytes.'
    else:
        shutil.copyfile(p, dest)
    assert sha(dest) == before[rel(p)]
after = {rel(p): sha(p) for p in inputs}
assert before == after, 'Concurrent protected input change; audit must be rerun.'
execution = json.loads((RUN / 'execution_evidence.json').read_text(encoding='utf-8'))
assert execution['input_sha256'] == before[rel(MODEL)]
save('native_cell_ledger.json', {'model_id': MID, 'cells': cells,
    'implicit_cells': 'Absent prey entries are source omissions, not newly inferred printed zeros.',
    'accepted_corrections': 'No documented cell-specific accepted diet correction found; canonical exactly equals retained source.'})
save('consumer_sums.json', sums)
save('provenance.json', {'date': '2026-10-02', 'unit_id': 'LME_027', 'selected_model_id': MID,
    'outcome': 'verified_unnormalized_unchanged', 'canonical_old_sha256': before[rel(MODEL)],
    'canonical_new_sha256': after[rel(MODEL)], 'canonical_equals_retained_source': True,
    'classification_evidence': 'Exact semantic equality of all source/native diet and import literals; nonunit consumer sums retained; 40 historical runtime-only changes documented separately.',
    'extracted_import_tables': 'None for this existing EcoBase model; sppr_source.xlsx is downstream calculated evidence, not an extracted diet/import table.',
    'researcher_review_status': 'pending; no approval inferred from current request, tolerance, or historical accepted runtime conventions',
    'runtime_policy': 'Runtime normalization is always allowed under latest explicit user steering; researcher rounding/error review remains evidence/trust status.',
    'canonical_transformations_this_audit': [], 'protected_input_hashes_before': before,
    'protected_input_hashes_after': after, 'original_model_archive': rel(archive),
    'historical_runtime_transformations': rel(RUN / 'transformation_ledger.json'),
    'historical_runtime_changed_diet_cells': len(runtime_changes),
    'historical_diagnostics': {'execution_evidence': rel(RUN / 'execution_evidence.json'),
        'actual_input_sha256': execution['input_sha256'], 'matches_current_canonical': True,
        'stale_due_to_this_audit': False, 'freshness_hashes_rewritten': False,
        'scientific_validity': 'Existing WARN/strict-balance findings preserved; native equality does not validate final-paper fidelity or runtime corrections.'},
    'researcher_docx_review': {'path': rel(DOCX), 'sha256': before[rel(DOCX)],
        'matching_paragraphs_read_only': review_excerpt, 'cell_correction_found': False},
    'unresolved': ['Exact printed diet/import cells for the final Morissette et al. 2009 FCRR 17(2) report have not been verified. Native EcoBase accession 118 source literals are verified, not silently relabeled printed-paper values.',
        'Nonunit source sums have no explicit researcher rounding-only review.'],
    'runs_performed': 'Read-only JSON literal/Decimal sum comparison, Overview selection read, DOCX XML read, SHA256 preservation checks. No SPPR or scientific recalculation.'})
save('source_recovery.json', {'date': '2026-10-02', 'scope': 'Bounded discovery during initial audit; stopped after latest user narrowed scope to normalization classification.',
    'queries': ['"Morissette" "Melgo" "2009" "17(2)" pdf', '"Food web model and data" "Northwest African" diet matrix', '"Modelling the trophic role of marine mammals" "2009" pdf UBC'],
    'outcomes': [{'url': 'https://epub.sub.uni-hamburg.de/epub/volltexte/2011/11876/pdf/17_2.pdf', 'status': 'Indexed primary source identity found; web open failed, no table geometry recovered.'},
        {'url': 'https://oceans.ubc.ca/research/publications/research-reports/', 'status': 'Official publisher index confirms FCRR 17(2), authors and 120 pages; links https://hdl.handle.net/2429/40932.'},
        {'url': 'https://hdl.handle.net/2429/40932', 'status': 'Web fetch redirected to https://open.library.ubc.ca/handle/2429/40932 and failed; no PDF/table bytes recovered.'}],
    'prior_precise_recovery_log': rel(REGION / 'validation_reports' / MID / 'source_retrieval_review.json')})
print(json.dumps({'outcome': 'verified_unnormalized_unchanged', 'canonical_sha256': before[rel(MODEL)],
    'diet_and_import_cells_compared': len(cells), 'runtime_only_changed_cells': len(runtime_changes),
    'protected_inputs_unchanged': before == after, 'evidence': rel(OUT)}))
