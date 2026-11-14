"""Publish only explicitly authorized model-local review artifacts and evidence."""
from pathlib import Path
import hashlib, json, os, shutil, sys, zipfile
from urllib.parse import unquote, urlsplit
from lxml import etree

ROOT = Path.cwd().resolve()
sys.path.insert(0, str(ROOT))
from tools.project_core.validation.researcher_review import read_report, removed_group_names, STATUS
from tools.project_core.validation.validation_percentage_format import verify_report

MODEL = ROOT / 'regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native'
VALID = MODEL / 'model_validation'
WORK = VALID / 'work/2026-11-14_185545_signed_review'
EVIDENCE = VALID / 'evidence/researcher_review_20261114'
EXPECTED = {'validation.docx':'d1b088fa0d01d6401b6d9ebfad942e80e5d7068276763185620219731da2165d',
            'taxon_mapping.xlsx':'e7bf3e80cb5d6aa2521a2a5b6c1e6a1fdcfcd71664d16300fba3a8b599e80bd0'}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def copy_checked(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    assert sha(source) == sha(target), str(target)

assert sha(MODEL/'model.json') == '9880e521a406974367530ffb06f13392714dba57b9645c38a1b1448926d83d17'
assert not EVIDENCE.exists(), 'Do not overwrite retained evidence'
for name, digest in EXPECTED.items():
    assert sha(VALID/name) == digest, f'Concurrent edit detected: {name}'
assert sha(WORK/'outputs/taxon_mapping.xlsx') == '427570e31f01224fc162c8df667c4dde7b9eeb5be45d1fdf1ca2e7053cec7a8c'
assert sha(WORK/'outputs/validation.docx') == '2854655b494fc8d9220c86962da02f043d9f1180a86dc9bb77d310787af072be'
verify_report(WORK/'outputs/validation.docx')
save(WORK/'qa/page_review.json', {
    'passed': True, 'document_sha256':sha(WORK/'outputs/validation.docx'),
    'rendered_pdf_sha256':sha(WORK/'qa/render/validation.pdf'),
    'renderer':'Separate hidden Microsoft Word COM read-only export; bundled LibreOffice was unavailable',
    'rasterizer':'Bundled pypdfium2, scale 1.5',
    'all_ten_pages_visually_inspected':True,
    'findings':'No clipping, overlap, missing glyphs, broken tables or misplaced figures. Repeated table headings and continuation rows remain readable. Signature and scenario conditions are legible.',
    'pages':[{'page':i, 'sha256':sha(WORK/f'qa/render/page-{i:02d}.png')} for i in range(1,11)]})

promoted = []
try:
    for name in EXPECTED:
        temp = VALID/(name+'.review-promotion.tmp')
        copy_checked(WORK/'outputs'/name, temp)
        os.replace(temp, VALID/name)
        promoted.append(name)
    name, date, summary = read_report(ROOT, VALID/'validation.docx', MODEL.name)
    assert name == 'Ido Carmel' and date == '2026-11-14'
    assert summary.get('status', STATUS) == 'Validated by researcher'
    calc = summary['sections'][2]['rows'][0]['text']
    assert removed_group_names(calc) == []
    assert 'EE floor ON at 0.1' in calc and 'sensitivity scenario only' in calc
    verify_report(VALID/'validation.docx')
    links = []
    for filename in EXPECTED:
        with zipfile.ZipFile(VALID/filename) as archive:
            for part in archive.namelist():
                if part.endswith('.rels'):
                    for rel in etree.fromstring(archive.read(part)):
                        if not rel.get('Type','').endswith('/hyperlink'):
                            continue
                        target = rel.get('Target','')
                        parts = urlsplit(target)
                        record = {'artifact':filename, 'target':target}
                        if not parts.scheme and parts.path:
                            local = (VALID/unquote(parts.path)).resolve()
                            assert local.is_relative_to(ROOT) and local.exists(), target
                            assert not Path(parts.path).is_absolute()
                            record['local_target_exists'] = True
                        links.append(record)
            if 'docProps/app.xml' in archive.namelist():
                app = etree.fromstring(archive.read('docProps/app.xml'))
                assert not any((e.text or '').strip() for e in app.iter() if etree.QName(e).localname=='HyperlinkBase')
    review = {'researcher_name':name, 'researcher_review_date':date,
             'status':summary.get('status',STATUS), 'excluded_group_seq':[], 'summary':summary,
             'canonical_model_sha256':sha(MODEL/'model.json'),
             'report_sha256':sha(VALID/'validation.docx'), 'appendix_sha256':sha(VALID/'taxon_mapping.xlsx'),
             'configuration':'source_exact_returns_to_36; EE floor ON 0.1; threshold 0.1; det_collapse_mode=never; det_open_mode=none',
             'physical_merge':'sensitivity only', 'GE_status':'WARN','TE_status':'WARN',
             'Project_map_trends_updated_by_this_task':False}
    save(WORK/'qa/parsed_review.json', review)
    save(WORK/'qa/final_links.json', {'passed':True, 'hyperlinks':links})
except Exception:
    for filename in promoted:
        if sha(VALID/filename) == sha(WORK/'outputs'/filename):
            copy_checked(WORK/'inputs'/filename.replace('.', '_before.',1), VALID/filename)
    raise

# Retain the actual evidence and QA; keep temporary authoring exports and backups in work only.
for p in (WORK/'code').iterdir():
    if p.is_file(): copy_checked(p, EVIDENCE/'code'/p.name)
for name in ['document_patch.json','appendix_verification.json','adoption_audit.json',
             'page_review.json','parsed_review.json','final_links.json','artifact.md']:
    copy_checked(WORK/'qa'/name, EVIDENCE/'qa'/name)
for name in ['appendix_final_middle.png','appendix_final_sources_tail.png','appendix_final_zero_rows.png']:
    copy_checked(WORK/'qa'/name, EVIDENCE/'qa'/name)
for p in (WORK/'qa/render').iterdir():
    if p.is_file(): copy_checked(p, EVIDENCE/'qa/render'/p.name)
copy_checked(WORK/'outputs/adoption_handoff.json', EVIDENCE/'adoption_handoff.json')
save(EVIDENCE/'signed_artifact_binding.json', review)

artifacts=[]
def artifact(role, path):
    artifacts.append({'role':role,'availability':'present',
                      'path':os.path.relpath(path,EVIDENCE).replace('\\','/'),'sha256':sha(path)})
for name in EXPECTED: artifact('signed_report' if name.endswith('docx') else 'mapping_appendix',VALID/name)
artifact('canonical_input', MODEL/'model.json')
artifact('GE_full_return',VALID/'evidence/discards_reconciliation_20261114/outputs/diagnostics/source_exact_returns_to_36/GE_full_return.json')
artifact('TE_full_return',VALID/'evidence/discards_reconciliation_20261114/outputs/diagnostics/source_exact_returns_to_36/TE_full_return.json')
artifact('physical_merge_sensitivity',VALID/'evidence/physical_detritus_merge_20261114/physical_detritus_merge.md')
artifact('native_source_reconciliation',VALID/'evidence/discards_reconciliation_20261114/outputs/source/native_probe_verification.json')
for p in sorted(EVIDENCE.rglob('*')):
    if p.is_file():
        role = 'adoption_handoff' if p.name=='adoption_handoff.json' else 'review_binding' if p.name=='signed_artifact_binding.json' else 'QA' if 'qa' in p.parts else 'code'
        artifact(role,p)
index={'schema_version':1,'run_id':'LME014_researcher_review_20261114','region_id':'LME_014',
       'model_id':MODEL.name,'variant_id':'source_exact_returns_to_36_ee_floor_on',
       'source_identity':{'paper':'Buring et al. 2024; DOI 10.1017/S0025315423000887','native_source':'PAT-2023 retained native 2020 Ecopath source'},
       'computational_input_identity':{'canonical_model_sha256':sha(MODEL/'model.json'),'configuration':review['configuration']},
       'methods':['GE','TE'],'required_roles':['signed_report','mapping_appendix','canonical_input','GE_full_return','TE_full_return','physical_merge_sensitivity','native_source_reconciliation','adoption_handoff','review_binding','QA','code'],
       'artifacts':artifacts,'reconciliation':{'signed_identity_and_date':True,'no_exclusions':True,'all_pages_reviewed':True,'appendix_science_preserved':True,'all_final_links_resolve':True},
       'scope':'Model-local signed artifacts only. No new solve, no canonical mutation, no Project/map/trends write. Coordinator owns numerical adoption and publication.',
       'cleanup_policy':'Remove only this task work directory after retained hashes and final evidence verification pass; source backup and authoring exports are temporary.'}
save(EVIDENCE/'evidence_index.json',index)
print(json.dumps({'published':True,'report_sha256':review['report_sha256'],'appendix_sha256':review['appendix_sha256'],'reviewer':name,'date':date,'evidence_directory':str(EVIDENCE),'indexed_artifacts':len(artifacts)},indent=2))
