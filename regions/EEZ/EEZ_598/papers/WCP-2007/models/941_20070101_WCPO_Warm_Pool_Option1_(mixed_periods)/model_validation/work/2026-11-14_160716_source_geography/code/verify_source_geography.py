"""Read-only scientific evidence verification; create report evidence only."""
import sys, json, hashlib, os, shutil, zipfile
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from pypdf import PdfReader
from lxml import etree

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path.cwd()
MID = '941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
MODEL = ROOT / 'regions/EEZ/EEZ_598/papers/WCP-2007/models' / MID
REPORT = MODEL / 'model_validation'
OUT = REPORT / 'evidence/source_review'
GEO = REPORT / 'evidence/geography'
DONOR = ROOT / 'regions/EEZ/EEZ_941/papers/WCP-2007/models' / MID
FLOOR = DONOR / 'model_validation/evidence/ee_floor_on'
HS = ROOT / 'regions/HS/HS_071/papers/WCP-2007/models' / MID

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rel(p, base=OUT):
    assert p.exists(), p
    return Path(os.path.relpath(p, base)).as_posix()

def identity(p, expected=None):
    value = sha(p)
    if expected is not None:
        assert value == expected, p
    return {'path_relative_to_this_file': rel(p), 'sha256': value,
            'expected_sha256': expected, 'matches_expected': value == expected if expected else None}

timestamp = datetime.now(timezone.utc).isoformat()
expected_model = '328330dc06ed3e96462995f1a04c1bdaa9747468af8bb4d9e4f57196b9cc1b03'
models = [identity(p/'model.json', expected_model) for p in [MODEL, DONOR, HS]]
pdf = MODEL.parents[1] / 'sources/download-0adcf55e.pdf'
pdf_expected = '0adcf55ef7760865786bc2774b1fb147a6461a6fe0b128a943c8fce27c23f52f'
pdf_id = identity(pdf, pdf_expected)
assert pdf.read_bytes().startswith(b'%PDF-'), 'Full source PDF bytes required'
source = PdfReader(pdf)
text7 = source.pages[6].extract_text()
assert all(token in text7 for token in ['110-180', '15', '26.964', '31 functional groups'])

prior_geo = read(OUT/'geographic_estimate.json')
boundary = ROOT/'common_reference_data/geography/boundaries/EEZs.geojson'
land = ROOT/'common_reference_data/geography/basemaps/ne_50m_land.geojson'
geometry_checks = [identity(boundary, prior_geo['input_hashes']['common_reference_data\\geography\\EEZs.geojson']),
                   identity(land, prior_geo['input_hashes']['common_reference_data\\geography\\basemaps\\ne_50m_land.geojson'])]
GEO.mkdir(parents=True, exist_ok=True)
asset_pairs = [(OUT/'study_domain.png', GEO/'region_study_domain.png'),
               (OUT/'article_figure1_crop.png', GEO/'article_figure1_crop.png')]
assets = []
for src, dest in asset_pairs:
    if dest.exists():
        assert sha(src) == sha(dest), f'Will not overwrite divergent evidence: {dest}'
    else:
        shutil.copyfile(src, dest)
    assets.append({'path_relative_to_this_file': rel(dest), 'sha256': sha(dest),
                   'retained_source_relative_to_this_file': rel(src), 'byte_identical_to_retained_source': True,
                   'visually_inspected': True})

donor_review = DONOR/'model_validation/evidence/source_review/source_geography_review_20261114.json'
prior_source = read(donor_review)
source_findings = prior_source['source_findings']
# Resolve evidence relative to the original donor record, then rebase it for this record.
for key in ['accepted_departures']:
    f = source_findings[key].get('evidence_relative_path')
    if f:
        source_findings[key]['evidence_relative_path'] = rel((donor_review.parent/f).resolve())

summary = read(FLOOR/'summary.json')
provenance = read(FLOOR/'run_provenance.json')
axes = read(FLOOR/'group_axes.json')
name_by_id = {int(x['id']): x['name'] for x in axes}
assert len(name_by_id) == 32
canonical = read(MODEL/'model.json')
assert all(name_by_id[int(g['group_seq'])] == g['group_name'] for g in canonical['group'])
assert summary['canonical_model_sha256'] == provenance['canonical_model_sha256'] == expected_model
assert provenance['resolved_constructor']['use_ee_floor'] is True
assert provenance['resolved_constructor']['ee_floor'] == 0.1
historic = read(OUT/'diagnostics_verification.json')
for old in historic:
    assert old['model_sha256'] == expected_model
    for key, value in old['settings'].items():
        assert provenance['resolved_constructor'][key] == value, key
    assert old['engine_hashes'] == provenance['flags']['engine_source_hashes']
for name, expected in provenance['flags']['engine_source_hashes'].items():
    assert sha(DONOR/provenance['flags']['engine_sources'][name]) == expected
assert sha(DONOR/provenance['flags']['calculation_engine_source']) == provenance['flags']['calculation_engine_sha256']

report_file = DONOR/'model_validation/validation.docx'
with zipfile.ZipFile(report_file) as z:
    xml = etree.fromstring(z.read('word/document.xml'))
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
report_rows = {}
for row in xml.xpath('.//w:tr', namespaces=ns):
    cells = [' '.join(c.xpath('.//w:t/text()', namespaces=ns)) for c in row.xpath('./w:tc', namespaces=ns)]
    if cells and cells[0] in ['GE diagnostics', 'TE diagnostics']:
        report_rows[cells[0][:2]] = cells[1]

methods = {}
source_refs = [FLOOR/'summary.json', FLOOR/'run_provenance.json', FLOOR/'group_axes.json',
               FLOOR/'ee_floor_ledger.json', FLOOR/'runtime_initialized.json.gz', FLOOR/'source_state.json.gz',
               report_file, OUT/'diagnostics_verification.json']
for method, stem in [('GE','new_GE'), ('TE','new_TE_EEfix')]:
    file = FLOOR/(stem+'_SPPR_matrix.json')
    matrix = read(file)
    arr = np.asarray(matrix['data'], dtype=float)
    assert arr.shape == tuple(matrix['shape']) == (32,4)
    assert len(set(matrix['index'])) == 32 and len(set(matrix['columns'])) == 4
    assert matrix['index'] == [x['id'] for x in axes]
    assert matrix['columns'] == [32,31,30,29]
    assert np.isfinite(arr).all()
    assert not any(np.asarray(mask).any() for mask in matrix['masks'].values())
    negatives = [{'group_id':matrix['index'][i], 'group_name':name_by_id[matrix['index'][i]],
                  'source_id':matrix['columns'][j], 'source_name':name_by_id[matrix['columns'][j]],
                  'value':float(arr[i,j])} for i,j in zip(*np.where(arr < 0))]
    diag = summary['methods'][method]['diagnostics']
    assert negatives == summary['methods'][method]['negative_source_group_pairings'] == []
    assert int((arr < 0).any(axis=0).sum()) == diag['divergence']['n_negative_sources'] == 0
    for scope, columns in [('all', [0,1,2,3]), ('inner',[1,2,3]), ('PP',[2,3])]:
        expected = np.array([summary['methods'][method]['scopes'][scope][name_by_id[i]] for i in matrix['index']])
        assert np.allclose(arr[:,columns].sum(axis=1), expected, rtol=1e-12, atol=1e-12)
    div = diag['divergence']
    detritus = dict(div['sppr_det']['items'])[31]
    assert f"{div['rho_living']:.6f}" in report_rows[method]
    assert f'{detritus:.6f}' in report_rows[method]
    if method == 'GE':
        assert f"{div['b']:.6f}" in report_rows[method]
    assert 'WARN' in report_rows[method] and 'No negative SPPR entries' in report_rows[method]
    methods[method] = {'execution_status':summary['methods'][method]['execution_status'],
        'diagnostic_status':diag['status'], 'matrix_shape':list(arr.shape), 'all_entries_finite':True,
        'all_missing_masks_false':True, 'row_ids':matrix['index'],
        'source_columns':[axes[matrix['index'].index(i)] for i in matrix['columns']],
        'negative_source_group_pairings':negatives, 'negative_tolerance':0,
        'rho_living':div['rho_living'], 'b':div['b'], 'detritus_sppr':detritus,
        'model_input':diag['model_input'], 'sppr_balance':diag['balance'], 'warnings':diag['warnings'],
        'donor_report_text':report_rows[method], 'donor_report_values_match_rounded_saved_values':True,
        'all_inner_PP_scope_sums_reconciled':True}
    source_refs.extend([file, FLOOR/(stem+'_full_return.json.gz')])

shared = {'review_date':'2026-11-14', 'checked_at_utc':timestamp, 'target_region':'EEZ_598',
    'source_run_region':'EEZ_941', 'model_id':MID, 'canonical_sha256':expected_model,
    'operation':'Independent read-only complete saved-matrix check and exact model/configuration evidence reuse; no solver or regional calculation.',
    'reuse_supported_for_named_model_level_GE_TE_diagnostics':True,
    'model_identity_checks':models, 'canonical_group_ids_names_match_donor_axes':True,
    'historical_target_constructor_settings_match_donor_base':True,
    'historical_base_engine_hashes_match_current_saved_bytes':True,
    'calculation_engine_hash_matches_saved_bytes':True,
    'configuration':provenance['resolved_constructor'], 'calculation_engine_upgrade':provenance['flags']['calculation_engine_upgrade'],
    'scope_compatibility':provenance['scoped_compatibility'], 'methods':methods, 'ee_floor':summary['floor'],
    'historical_GE':{'b':historic[0]['direct']['divergence']['b'], 'detritus_sppr':historic[0]['direct']['divergence']['sppr_det'],
                     'interpretation':'Prior report evidence, not floor-enabled numbers; no historical result relabeled.'},
    'sources':[identity(p) for p in source_refs],
    'limitations':['Direct GE/TE reuse is not full inventory certification or an EEZ_598 annual-result migration.',
                   'GE and TE retain WARN and strict balance false. Complete nonnegative matrices are not scientific approval.',
                   'Original researcher reviews and the floor-enabled diagnostic identity remain separate.',
                   'EE floor is a hypothetical nonfishery export assumption; no canonical parameter correction is made.']}
retained_certificate = HS/'model_validation/evidence/source_review/shared_diagnostics_verification_20261114.json'
certificate = read(retained_certificate)
retained_hashes = {(retained_certificate.parent/x['path']).resolve():x['sha256'] for x in certificate['sources']}
checked_retained = [identity(p, retained_hashes[p.resolve()]) for p in source_refs if p.resolve() in retained_hashes]
assert len(checked_retained) >= 10
shared['retained_donor_certificate'] = identity(retained_certificate)
shared['retained_donor_evidence_hash_checks'] = checked_retained
shared['retained_donor_evidence_bytes_unchanged'] = True
(OUT/'shared_diagnostics_verification_20261114.json').write_text(json.dumps(shared, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

review = {'review_date':'2026-11-14', 'checked_at_utc':timestamp, 'region_id':'EEZ_598', 'selected_model_id':MID,
    'scope':'Current source identity, source-context/temporal inspection, reusable geography and saved model-level diagnostic verification; no scientific rerun, input mutation, workbook write or researcher approval.',
    'identity_checks':models+[pdf_id]+geometry_checks+[identity(donor_review)],
    'source_pdf_is_full_original_bytes':True,
    'source_findings':source_findings, 'temporal':prior_source['temporal'],
    'independently_read_source_pages':[1,7,38,39,40,41,42],
    'geography':{'retained_calculation':rel(OUT/'geographic_estimate.json'), 'reused_calculation':True,
        'fresh_area_calculation':False, 'geometry_input_hashes_match':True,
        'old_boundary_path_relocation':'Historical geography/EEZs.geojson is now geography/boundaries/EEZs.geojson with identical bytes.',
        'region_area_km2':prior_geo['region_area_km2'], 'intersection_km2':prior_geo['intersection_km2'],
        'study_wet_area_km2':prior_geo['study_rectangle_wet_area_km2'], 'study_reported_area_km2':26964000,
        'A_percent':100.0, 'B_wet_rectangle_percent':prior_geo['B_study_in_region_percentage'],
        'B_published_area_percent':prior_geo['B_using_published_26964000_km2_percentage'],
        'report_text':'A ≈ 100%; B ≈ 9–10%.', 'study_bounds':[110,-15,180,15], 'method':prior_geo['method'],
        'interpretation':'The range reflects coordinate-domain versus published-area denominators and boundary uncertainty, not a statistical interval. Spatial containment does not establish coastal/reef representativeness.',
        'assets':assets,
        'figure_change':'The full-domain overlay replaces the close-up whose eastern regional tip is clipped. The retained full-domain graphic displays the entire PNG EEZ and selected fixed rectangle; the original article Figure 1 remains separately labeled context.'},
    'selected_model_rationale':'Recorded user adoption of D_fixed_M0 preserves juvenile other-mortality flows; source fidelity and native EwE validity are not claimed.',
    'article_selection_rationale':'Comparative reason unrecorded; do not invent one.',
    'local_registered_alternatives':[
        {'article':'Griffiths et al. 2019', 'doi':'10.1111/fog.12389', 'period':2005,
         'source':rel(ROOT/'regions/EEZ/EEZ_598/papers/Griffiths-2019/sources/main.pdf'),
         'model_variants':'46-group source extraction (unknown two-pool routing); 45-group pooled experiment (GE/TE/With Egestion FAIL). Both deferred, not selected.'}],
    'other_known_related_article':{
        'article':'Allain et al. 2021', 'title':'Tuna fisheries bycatch and climate change in the western tropical Pacific Ocean',
        'report':'WCPFC-SC17-2021/EB-IP-11', 'source':rel(ROOT/'regions/EEZ/EEZ_941/papers/Allain-2021/sources/main.pdf'),
        'relationship':'Known related source under EEZ_941; not a registered EEZ_598 model candidate.',
        'source_period_domain':'2013 annual average; 140°E–150°W, 20°N–20°S (PDF4); distinct from the selected 2007 source.'},
    'diagnostic_evidence':rel(OUT/'shared_diagnostics_verification_20261114.json'),
    'report_relative_links':{'source_pdf':rel(pdf,REPORT)+'#page=7', 'model':rel(MODEL/'model.json',REPORT),
        'model_notes':rel(MODEL/'model_notes.md',REPORT), 'source_context':rel(OUT/'source_review.md',REPORT),
        'source_identity':rel(OUT/'source_geography_review_20261114.json',REPORT) if (OUT/'source_geography_review_20261114.json').exists() else 'evidence/source_review/source_geography_review_20261114.json',
        'geography_figure':rel(GEO/'region_study_domain.png',REPORT), 'source_figure':rel(GEO/'article_figure1_crop.png',REPORT),
        'floor_GE_TE':rel(OUT/'shared_diagnostics_verification_20261114.json',REPORT)},
    'limitations':['Accepted Option1 is an experimental surrogate with known source departures; no author-confirmed repair or new all-cell extraction audit.',
                   'High overlap and shared model identity do not transfer taxon mapping, catch composition or researcher approval between regions.',
                   'No new geography/SPPR run or regional annual calculation performed by this evidence task.']}
(OUT/'source_geography_review_20261114.json').write_text(json.dumps(review, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(json.dumps({'source_review':rel(OUT/'source_geography_review_20261114.json',ROOT),
                  'diagnostics':rel(OUT/'shared_diagnostics_verification_20261114.json',ROOT),
                  'geography_assets':[rel(p,ROOT) for _,p in asset_pairs],
                  'model_hash':expected_model, 'matrices_checked':['GE 32x4','TE 32x4'],
                  'negative_entries':0, 'scientific_runs':0}, indent=2))
