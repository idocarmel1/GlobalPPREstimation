"""Register acquired context and package unadopted scientific proposals."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import platform

RUN = Path(__file__).resolve().parents[1]
MODEL = Path(__file__).resolve().parents[4]
REPO = next(p for p in MODEL.parents if (p/'Project.xlsx').exists())
PAPER = MODEL.parents[1]
OUT = RUN/'outputs'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

downloads = read(OUT/'source_downloads.json')
old = PAPER/'sources/context/Quinones2017_doctoral_thesis.pdf'
new = PAPER/'sources/context/Quinones2018_doctoral_thesis.pdf'
if old.exists():
    assert old.resolve().is_relative_to(REPO.resolve())
    assert new.resolve().is_relative_to(REPO.resolve())
    assert not new.exists(), 'Do not overwrite a context source.'
    old.rename(new)
    ledger = REPO/'common_reference_data/provenance/source_paths.csv'
    with ledger.open('r',encoding='utf-8-sig',newline='') as f:
        fields = csv.DictReader(f).fieldnames
    record = dict(original_path=old.relative_to(REPO).as_posix(),
        retained_path=new.relative_to(REPO).as_posix(),sha256=sha(new),retained_sha256=sha(new),
        action='context_filename_correction',
        reason='Newly downloaded thesis title page states Mar del Plata 2018; initial download filename incorrectly used 2017. Source bytes unchanged.',
        unit_id='LME_013',model_id=MODEL.name,extraction_run_id=RUN.name)
    with ledger.open('a',encoding='utf-8',newline='') as f:
        csv.DictWriter(f,fieldnames=fields).writerow(record)

for rec in downloads:
    if rec.get('filename') == 'Quinones2017_doctoral_thesis.pdf':
        rec['filename'] = new.name
        rec['path'] = 'context/'+new.name
        rec['filename_correction'] = '2018 verified on PDF title page; downloaded bytes unchanged.'
    if rec['status'] == 'verified_pdf':
        assert sha(PAPER/'sources'/rec['path']) == rec['sha256']
write(OUT/'source_downloads.json', downloads)

context = [
    dict(filename=new.name, file_label='Context: Javier Antonio Quiñones Dávila doctoral thesis (2018)',
         evidence='Title page identifies 2018. PDF166-175/printed157-166 discuss Chiaverano et al. (2018) scenarios; PDF167/printed158 repeats the 29 t/km2/year harvest assumption. No independent detailed baseline diet percentages or sardine 1.4 correction found in the inspected focal chapter.',
         supports='Related author account and scenario context; does not establish the proposed baseline values.'),
    dict(filename='Ceh2015_supplement_srep12037.pdf',file_label='Context: Ceh et al. (2015), Scientific Reports 5:12037, supplementary information',
         evidence='PDF2-3, Supplementary Table S4: gastric food-item counts per medusa in Mejillones, Northern Chile, 2010-2013. Visually inspected complete table and continuation. Numbers are item counts, not biomass diet fractions.',
         supports='Observed anchovy eggs, zooplankton and gelatinous prey; cannot independently establish 68/17/15 biomass diet fractions for the 1995-1998 model.')]
manifest = read(PAPER/'source_manifest.json')
roles_path = REPO/'common_reference_data/provenance/paper_file_roles.json'
roles = read(roles_path)
for ctx in context:
    rec = next(d for d in downloads if d.get('filename') == ctx['filename'])
    paper_path = 'sources/'+rec['path']
    repo_path = (PAPER/'sources'/rec['path']).relative_to(REPO).as_posix()
    entry = dict(path=paper_path,sha256=rec['sha256'],bytes=rec['bytes'],verification='full_bytes',
                 role='context',role_evidence=ctx['evidence'],source_url=rec['url'],
                 final_url=rec['final_url'],retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                 file_label=ctx['file_label'],supports=ctx['supports'])
    if not any(f['path']==paper_path for f in manifest['files']):
        manifest['files'].append(entry)
    if not any(f['path']==repo_path for f in roles['files']):
        roles['files'].append(dict(path=repo_path,sha256=rec['sha256'],role='context',
                                  file_label=ctx['file_label'],evidence=ctx['evidence']))
write(PAPER/'source_manifest.json',manifest)
write(roles_path,roles)

audit = read(OUT/'correction_scenarios.json')
assert audit['protected_inputs_unchanged']
for p,h in audit['protected_input_hashes'].items():
    assert sha(REPO/p)==h, 'Consumed scientific input changed.'
scenarios = {r['scenario']:r for r in audit['scenarios'] if not r['runtime_BA_compensation']}
fixed = scenarios['matrix_diet_article_landings_fixed_discards_reestimate_EE']
scaled = scenarios['matrix_diet_article_landings_scaled_discards_reestimate_EE']
assert fixed['balanced'] and scaled['balanced']
assert fixed['living_max_abs_BA']==scaled['living_max_abs_BA']==0
proposal = dict(
    status='UNADOPTED_PROPOSALS', model_id=MODEL.name,
    decision_rule='User requests article prose preference over conflicting supplement values. Keep biological B/PB/QB inputs; recalculate model-estimated EE when landings change.',
    jellyfish_diet=dict(consumer_seq=7,consumer_name='Chrysaora plocamia',
        proposed_fractions={'Diatoms':0,'Mesozooplankton':.68,'Macrozooplankton':.17,
                            'Gelatinous zooplankton':0,'Anchovy eggs':.15},
        source_evidence=['Table H-agg. production matrix F14/I14/J14/K14 supplies zero/68%/17%/zero direct links after physiological partitioning; Table E identifies singleton donor groups.',
                         '15% anchovy eggs retained from resolved diet Table B H39.',
                         'Native source egg EE independently recovered: 0.8843322109525973 vs Table A H41 0.8843322396278381.'],
        interpretation='Derived reconstruction of a coherent author-supported diet version; not newly measured fractions or proof of final author intention.'),
    primary_source_preserving_proposal=dict(sardine_seq=9,
        landings=fixed['sardine_landings'],discards=fixed['sardine_discards'],
        runtime_export=fixed['sardine_total_removals'],EE=fixed['sardine_EE'],
        derived_M0=fixed['sardine_M0'],
        reason='Article PDF3/printed30 explicitly specifies landings 1.4. Preserve reported discards absent an explicit replacement. Table A H14 EE is bold/model-estimated and recalculated from losses/production.'),
    rate_consistent_alternative=dict(sardine_seq=9,
        landings=scaled['sardine_landings'],discards=scaled['sardine_discards'],
        runtime_export=scaled['sardine_total_removals'],EE=scaled['sardine_EE'],
        derived_M0=scaled['sardine_M0'],discard_to_landings_ratio=.0309,
        assumption='Preserve supplement discard/landings ratio after reducing landings, consistent with rate-based Methods; no explicit author-revised sardine discard quantity recovered.'),
    EE_equation='EE = (normalized-diet predation + landings + discards)/production, with retained BA=0 and net migration=0.',
    original_failures=scenarios['original']['failing_group_seqs'],
    landings_only_failures=scenarios['article_landings_only_fixed_discards']['failing_group_seqs'],
    verification=dict(living_balance_passes=True,runtime_BA_compensation=False,
        living_BA_all_zero=True,all_16_runs_saved=True,
        native_steady_state_pool_outputs=fixed['native_pool_budget_with_reestimated_EE_zero_BA']),
    limitations=[
        'Article Table 1 PDF4/printed31 forage-fish landings 28.13 and Scenario III total harvest approximately 29 corroborate the older high-sardine-landings branch; article itself is internally inconsistent.',
        'Corrected diet alone passes living balance with original supplement landings. This is an alternative coherent source branch, not selected here because of user source priority.',
        'Native pool routing and fleet discard ancestry are not reproduced by the current calculator. Native pool EE re-estimates reported separately using Table C routing and discard returns; not validated native EwE execution.',
        'Runtime diet normalization retained for other small diet-sum discrepancies; no proposed adoption of those normalized values.',
        'Passed mass balance is not SPPR readiness or researcher approval. No SPPR or Monte Carlo rerun; no accepted model/report/notebook/workbook edits.'
    ])
write(OUT/'proposed_corrections.json',proposal)

inventory = []
for p in sorted(RUN.rglob('*')):
    if p.is_file() and p.name != 'evidence_index.json':
        inventory.append(dict(path=p.relative_to(MODEL).as_posix(),sha256=sha(p),bytes=p.stat().st_size))
write(OUT/'evidence_index.json',dict(schema_version=1,scope='Source-backed correction proposals only',
    generated_at_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),
    consumed_scientific_inputs=audit['protected_input_hashes'],
    scientific_code_hashes={p.relative_to(REPO).as_posix():sha(p) for p in
                           [REPO/'tools/scientific_code/PPREstimation/ModelData.py',
                            REPO/'tools/scientific_code/PPREstimation/PPRCalculator.py']},
    context_sources=downloads,artifacts=inventory))
print('Registered two context PDFs and saved proposals; protected scientific inputs unchanged.')
