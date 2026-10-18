"""Capture task preservation checks and temporary transaction rollback bytes."""
import hashlib, json, shutil, subprocess, tempfile, zipfile
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').is_file())
RUN = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from tools.project_core.validation.researcher_review import table_rows

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

with zipfile.ZipFile(ROOT / 'Project.xlsx') as archive:
    rows = [r for _, r in table_rows(archive, 'Models & coverage', 'Models')[3]]
positive = [r for r in rows if r.get('researcher_review_status') == 'Validated by researcher']
paths = set()
for r in positive:
    model = (ROOT / r['model_path']).parent
    paths.update(p for p in model.rglob('*') if p.is_file() and RUN not in p.parents)
    paths.add(ROOT / 'regions' / r['unit_id'].split('_')[0] / r['unit_id'] / (r['unit_id'] + '.xlsx'))
historical = [
    'research/human/sppr_trophic_level_20261016',
    'research/human/ppr_taxonomic_resolution_20261016',
    'research/human/ppr_taxonomic_resolution_GE_20261016',
    'regions/LME/LME_028/work/2026-10-16_202757_trophic_aggregation',
    'regions/LME/LME_027/papers/CAN-2009/models/27_118_Northwest_Africa_(1987)/model_validation/work',
]
for name in historical:
    paths.update(p for p in (ROOT / name).rglob('*') if p.is_file())
paths.update(p for p in (ROOT / 'regions').glob('*/*/*.xlsx'))
for name in ['Project.xlsx', 'research/README.md', 'common_reference_data/provenance/source_paths.csv',
             'tools/knowledge_graph/REFRESH_SCOPE.md', 'interactive_map/index.html',
             'interactive_map/trends.html', 'interactive_map/sources.html']:
    paths.add(ROOT / name)
paths.update(p for p in (ROOT / 'interactive_map/data').rglob('*') if p.is_file())
print(f'Hashing {len(paths)} preservation inputs', flush=True)
protected = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(paths)}
temporary = RUN / 'inputs' / 'temporary_rollback'
temporary.mkdir(parents=True, exist_ok=False)
target = ROOT / 'regions/LME/LME_028/papers/GUI-2004/models/28_646_Guinea_(1998)'
rollback = [ROOT/'Project.xlsx', target/'model_validation/validation.docx', target/'model_notes.md',
            ROOT/'interactive_map/index.html', ROOT/'interactive_map/trends.html', ROOT/'research/README.md',
            ROOT/'tools/knowledge_graph/REFRESH_SCOPE.md']
for p in rollback:
    dest = temporary / p.name
    shutil.copyfile(p, dest)
qa = RUN / 'qa'
qa.mkdir(parents=True, exist_ok=True)
data = {'target': ['LME_028', '28_646_Guinea_(1998)'], 'review_date': '2026-10-18',
        'authorization': 'User explicitly authorized signing as Ido Carmel and requested no historical file updates or historical review archive.',
        'temporary_rollback': str(temporary), 'protected_sha256': protected,
        'initial_model_metadata': rows, 'positive_pairs_before': [[r['unit_id'],r['model_id']] for r in positive],
        'historical_packages': historical,
        'git_status_before': subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        'git_diff_before_sha256': hashlib.sha256(subprocess.check_output(['git','diff'],cwd=ROOT)).hexdigest()}
(qa/'baseline.json').write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
(RUN/'progress.md').write_text('# LME028 regional validation withdrawal\n\nUser approved the plan on 18 October 2026 and explicitly authorized Ido Carmel signature. Historical files are left unchanged; rollback bytes are temporary.\n\n- Baseline captured; document and research preparation may proceed.\n- Central registration/publication owned solely by root.\n', encoding='utf-8')
print(json.dumps({'protected_files':len(protected),'positive_pairs':len(positive),'temporary_rollback':str(temporary)},indent=2))
