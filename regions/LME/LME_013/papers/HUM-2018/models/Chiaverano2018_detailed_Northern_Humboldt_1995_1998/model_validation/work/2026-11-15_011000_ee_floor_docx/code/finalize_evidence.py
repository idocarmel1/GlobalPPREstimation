"""Verify retained evidence and assemble a read-only registration handoff."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
from urllib.parse import urlsplit, unquote
import csv, gzip, hashlib, json, math, sys

root=Path.cwd().resolve()
m=root/'regions/LME/LME_013/papers/HUM-2018/models/Chiaverano2018_detailed_Northern_Humboldt_1995_1998'
run=m/'model_validation/work/2026-11-15_011000_ee_floor_docx'
staged=run/'outputs/validation.docx'
canonical=m/'model_validation/validation.docx'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(root).as_posix()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
cfg_path=root/'regions/LME/LME_003/work/2026-11-14_235900_deterministic_coverage/inputs/humboldt_docx_reviewed_configuration.json'
cfg=read(cfg_path)
weights_path=m/'results/diagnostics/engine_comparison_20261114/group_catch_weights.json'
weights=read(weights_path)
old_path=m/cfg['proof_refs']['coefficient_csv']['relative_path']
with old_path.open(encoding='utf-8-sig',newline='') as f: old_rows=list(csv.DictReader(f))
denominator=42068251754.19618
metrics={}
input_paths=[cfg_path,weights_path,old_path,canonical,m/'model.json',m/'sppr_source.xlsx',m/'model_validation/taxon_mapping.xlsx']
for method,key in [('GE','new_GE'),('TE','new_TE_EEfix')]:
    p=m/f'results/diagnostics/method_coverage/deterministic_completion_20261114/controls/{key}.json.gz'
    x=json.loads(gzip.decompress(p.read_bytes()));input_paths.append(p)
    current={name.strip():value for name,value in x['scopes']['all'].items()}
    historical={r['group_name'].strip():float(r['sppr_wet']) for r in old_rows if r['method']==method and r['scope']=='all'}
    w={name.strip():values[-1] for name,values in weights['bases']['landings']['weights'].items()}
    assert len(w)==len(weights['bases']['landings']['weights'])
    assert set(w)<=set(current) and set(w)<=set(historical)
    old=sum(value*historical[name] for name,value in w.items())/9
    new=sum(value*current[name] for name,value in w.items())/9
    expected=(244046985.9159432,227510177.46603224) if method=='GE' else (835805954.7337195,302008898.56518394)
    assert math.isclose(old,expected[0],abs_tol=1e-5) and math.isclose(new,expected[1],abs_tol=1e-5)
    data=x['source_matrix']['data'];assert len(data)==40 and all(len(r)==7 for r in data)
    assert all(math.isfinite(v) and v>=0 for row in data for v in row)
    assert x['negative_entries']==[]
    diag=x['diagnostics']
    assert diag['config']['det_collapse_mode']=='auto'
    assert diag['config']['use_ee_floor'] is True and diag['config']['ee_floor']==0.1
    metrics[method]={'diagnostics':diag,'current_matrix_shape':[40,7],'current_negative_pairs':[],
        'historical_tC':old,'current_tC':new,'change_percent':(new/old-1)*100,
        'historical_global_npp_percent':old/denominator*100,'current_global_npp_percent':new/denominator*100}

assert sha(staged)=='219443c7dc914e20da6838cd13762d58ed7d396fd07625b36f2a80c3439b8fc2'
assert sha(canonical)=='b356cb1f7891659dd15aae44caf8561c8c122709506234255e3bb7b9f384669d'
protected_before=read(run/'qa/protected_hashes_before.json')
protected_after={p:sha(root/p) for p in protected_before}
assert protected_before==protected_after, 'A protected input changed during report preparation'
links=[]
with ZipFile(staged) as z:
    r=E.fromstring(z.read('word/_rels/document.xml.rels'))
    for e in r:
        if e.attrib.get('TargetMode')!='External':continue
        t=e.attrib['Target'];u=urlsplit(t)
        if not u.scheme:
            target=(canonical.parent/unquote(u.path)).resolve()
            assert target.is_relative_to(root) and target.exists(),t
            links.append({'id':e.attrib['Id'],'stored_target':t,'resolved_canonical_target':rel(target),'exists':True})

before=read(run/'qa/signoff_before.json');after=read(run/'qa/signoff_after_projected.json')
assert before[:2]==after[:2]==['Ido Carmel','2026-10-08']
for i,(b,a) in enumerate(zip(before[2]['sections'],after[2]['sections'])):
    if i!=1:assert b==a
assert before[2]['note']==after[2]['note']
assert set(before[2])==set(after[2])
assert weights['excluded_group_ids']==['Fishery offal','Pinnipeds','Seabirds','Chrysaora plocamia']
sys.path.insert(0,str(root))
from tools.project_core.validation.validation_percentage_format import verify_report
verify_report(staged)

evidence={'schema_version':1,'scope':'Report-only review of saved EE-floor results; no scientific solve',
    'input_sha256':{rel(p):sha(p) for p in input_paths},'metrics':metrics,
    'comparison_context':{'year':2019,'catch_basis':'landings','scope':'all','original_allocation_shares':True,'wet_to_carbon_divisor':9,'excluded_names':weights['excluded_group_ids'],
        'global_npp_denominator_tC_year':denominator,'global_npp_source':'Project.xlsx / Definitions & build / Metadata / global_npp / annual[2019].npp_denominator_tC_yr',
        'global_npp_verified_project_sha256':'11d68cdbc3f06b098f1cadbf6680632da836690b0cde6a8e80176006daef598f','reference':'atlas_lme_high_seas_union_v1','status':'coverage_limited'},
    'report_status_interpretation':{'GE_pooled_result':'WARN','GE_unpooled':'FAIL','GE_saved_engine_aggregate':'FAIL','TE_result':'WARN','TE_budget':'OK'},
    'independent_content_review':'PASS; checked against full returns, ledger, historical proof refs, original DOCX and parser summaries'}
(run/'qa/numerical_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf8')

qa={'schema_version':1,'staged_sha256':sha(staged),'renderer':'Microsoft Word independent hidden COM instance; read-only open, macros disabled, no save, own instance closed',
    'packaged_renderer_attempt':'Failed: soffice.exe absent on PATH; documented native Word fallback used',
    'rasterizer':'Bundled pypdfium2, scale 1.5 (108 dpi)','page_count':9,'all_pages_visually_inspected':list(range(1,10)),
    'findings':'PASS: readable text/tables; no clipping, overlap, missing glyphs, accidental blank pages or stranded headings. Original confidence/mapping and geographic pages preserved.',
    'page_sha256':{p.name:sha(p) for p in sorted((run/'qa/final_render').glob('page-*.png'))},
    'rendered_pdf_sha256':sha(run/'qa/final_render/report.pdf'),'percentage_format':'PASS',
    'protected_inputs_unchanged':protected_before==protected_after,'protected_sha256':protected_after,
    'canonical_relative_local_links':links}
assert len(qa['page_sha256'])==9
(run/'qa/render_and_integrity_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')

registration="register_review(root / 'Project.xlsx', report, 'LME_013', 'Chiaverano2018_detailed_Northern_Humboldt_1995_1998', [37, 32, 31, 7])"
handoff={'schema_version':1,'ready_for_parent_promotion':True,'unit_id':'LME_013','model_id':m.name,
    'canonical_report':rel(canonical),'canonical_expected_before_sha256':sha(canonical),
    'staged_report':rel(staged),'staged_sha256':sha(staged),
    'retained_historical_original':rel(run/'inputs/validation_reviewed.docx'),
    'reviewer':'Ido Carmel','signed_date':'2026-10-08','verdict':'MODEL VALIDATED','registered_status':'Validated by researcher',
    'excluded_seq':[37,32,31,7],'excluded_group_names':weights['excluded_group_ids'],
    'preserved_configuration_condition':"det_collapse_mode='auto'",
    'intended_parser_changes':['GE and TE diagnostics; both current rows only'],
    'all_other_parser_fields_identical':True,'parser_path_projection':'Staged ZIP bytes read at canonical path via file-open redirection. No canonical file was overwritten.',
    'signoff_before':{'path':rel(run/'qa/signoff_before.json'),'sha256':sha(run/'qa/signoff_before.json')},
    'signoff_after':{'path':rel(run/'qa/signoff_after_projected.json'),'sha256':sha(run/'qa/signoff_after_projected.json')},
    'parser_diff':{'path':rel(run/'qa/intended_parser_changes.json'),'sha256':sha(run/'qa/intended_parser_changes.json')},
    'render_qa':{'path':rel(run/'qa/render_and_integrity_qa.json'),'sha256':sha(run/'qa/render_and_integrity_qa.json')},
    'package_qa':{'path':rel(run/'qa/package_preservation.json'),'sha256':sha(run/'qa/package_preservation.json')},
    'numerical_evidence':{'path':rel(run/'qa/numerical_evidence.json'),'sha256':sha(run/'qa/numerical_evidence.json')},
    'registration_module':'tools.project_core.validation.researcher_review','registration_api':registration,
    'refresh_api':"refresh_reviews(project, previous_project, ['LME_013'], model_ids={'LME_013': 'Chiaverano2018_detailed_Northern_Humboldt_1995_1998'})",
    'parent_sequence':['Finish science/page publication against original report as coordinated','Check original and staged SHA guards','Snapshot Project and publication transaction before promotion','Promote staged report atomically to canonical destination','Reread with read_report; compare exact after summary and verify percentages','Register exact signed review and exclusions','Run strict bounded refresh_reviews; verify both source-equal page payloads','Rollback coherently on any failure; parent owns final commit'],
    'ownership':'Parent chat 01a1dbe6-3320-7e82-b886-782a9f1e9320 owns promotion, registration, Project, views and commit. This chat made no central/source writes, reruns, builds or commits.',
    'staging_link_note':'Links are relative for canonical destination. Do not register staged path or rebase links for its work directory.',
    'cleanup_after_parent_acceptance':'Render images/PDF and qa/temp are transient verification assets. Keep the signed original, staged/final DOCX and compact QA evidence needed for the adoption record.'}
(run/'outputs/handoff.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'staged_sha256':sha(staged),'handoff':rel(run/'outputs/handoff.json'),'handoff_sha256':sha(run/'outputs/handoff.json'),'verified_pages':9,'protected_inputs':'unchanged','parser_changes':['GE and TE diagnostics']},ensure_ascii=False))
