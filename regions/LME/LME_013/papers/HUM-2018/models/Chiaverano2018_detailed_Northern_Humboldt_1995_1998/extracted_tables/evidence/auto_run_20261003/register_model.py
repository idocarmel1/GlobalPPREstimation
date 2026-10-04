from pathlib import Path
import sys,json,copy
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
MODEL='Chiaverano2018_detailed_Northern_Humboldt_1995_1998'
project=ROOT/'Project.xlsx';fingerprint=sha(project);p=read_book(project)
manifest=json.loads((OUT/'run_manifest.json').read_text(encoding='utf-8'))
headers,rr=p['Models & coverage']['Models']
add_fields=['configuration','computational_input_sha256','canonical_source_path','canonical_source_sha256','engine_hashes','diagnostic_manifest','production_eligible','diagnostic_grades']
for field in add_fields:
    if field not in headers:headers.append(field);[r.append(None) for r in rr]
assert not any(dict(zip(headers,r)).get('model_id')==MODEL for r in rr),'Already registered'
d={'unit_id':'LME_013','model_id':MODEL,'model_path':(BASE/'source/computational/model.json').relative_to(ROOT).as_posix(),
   'source_filename':'model.json','selected':False,'paper_ids':'HUM-2018__LME_013','model_year':'1995–1998',
   'variant':'resolved detailed native supplement; exact audited computational translation; det_collapse_mode=auto',
   'model_area_km2':165000,'availability':'selected provisional research preview after successful sign/finite preflight; DIRECT GE/TE/With Egestion overall FAIL; production-ineligible; no researcher verdict',
   'publication_year':2018,'model_years':'1995–1998 static baseline','target_coverage_ratio':None,'coverage_class':'partial; approximate region coverage 6–8%',
   'doi':'10.1016/j.pocean.2018.04.009','coverage_note':'Approximate A 6–8%, B 90–100%; reviewed source Figure 1 trace and reported-area discrepancy retained. Fixed model and allocations over 1950–2019 remain extrapolations.',
   'validation_report_path':'regions/LME_013/Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx',
   'validation_report_sha256':sha(ROOT/'regions/LME_013/Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx'),
   'configuration':json.dumps(manifest['method_call']), 'computational_input_sha256':manifest['input_sha256'],
   'canonical_source_path':(BASE/'source/resolved_native/model.json').relative_to(ROOT).as_posix(),
   'canonical_source_sha256':sha(BASE/'source/resolved_native/model.json'),'engine_hashes':json.dumps(manifest['engine']),
   'diagnostic_manifest':(OUT/'run_manifest.json').relative_to(ROOT).as_posix(),'production_eligible':False,
   'diagnostic_grades':'GE: FAIL / FAIL / FAIL; TE: FAIL / WARN / FAIL; With Egestion: FAIL / FAIL / WARN (input / convergence / SPPR balance)'}
rr.append([clean(d.get(h)) for h in headers])
ph,pr=p['Papers']['Papers']
for r in pr:
    row=dict(zip(ph,r))
    if row.get('article_id')=='HUM-2018__LME_013':
        patch={'title':'Evaluating the role of large jellyfish and forage fishes as energy pathways, and their interplay with fisheries, in the Northern Humboldt Current System',
          'model_years':'1995–1998 detailed and aggregated static baselines; structural scenarios retained separately',
          'functional_groups':'39 source ecological stocks plus two source fleets; 40 calculator groups including synthetic import',
          'download_status':'verified_local_sources','main_file_status':'verified_local_main_file','supplement_status':'verified_local_native_xls_and_word_supplement',
          'model_file_status':'source-faithful reconstruction and separate audited computational JSON retained',
          'full_model_loadable':'Audited computational input loads; all direct methods FAIL under auto; nonnegative finite coefficients only establish numerical preflight success',
          'loadability_class':'Verified computational input; source conflicts and unsupported native-flow translation remain; overall FAIL',
          'download_failure_reason':'Historical unavailable-source claims superseded by retained verified PDF, native XLS and Word supplement; original retrieval counts remain historical.',
          'quality_rationale':'Historical numerical scores retained without regrading. Current verified sources and exact computational translation produce overall FAIL in all DIRECT methods. Auto pooling removes negative SPPR, but does not establish scientific validity.',
          'recommendation':'User-selected detailed Northern Humboldt 1995–1998 provisional review model; production-ineligible; no researcher verdict',
          'notes':'See '+d['diagnostic_manifest']+' and the unsigned validation document. Selection does not constitute researcher validation.',
          'coverage_note':d['coverage_note'],'target_coverage_ratio':None,'geometry_method':'approximate graticule-calibrated source Figure 1 shading trace','geometry_confidence':'low',
          'geometry_note':d['coverage_note'],'loadability_evidence':d['diagnostic_manifest'],'documentation_evidence':(BASE/'source/REPORT.md').relative_to(ROOT).as_posix()}
        for k,v in patch.items():
            if k in ph:r[ph.index(k)]=v
# Reconcile the displayed selected article boundary to the existing reviewed trace.
g=unchunks(rows(p,'Map geography','Geometry'))
old_geometry=g.get('article:HUM-2018__LME_013')
trace=json.loads((BASE/'geography/study_trace.geojson').read_text(encoding='utf-8'))
geometry=trace['geometry'] if trace['type']=='Feature' else trace['features'][0]['geometry'] if trace['type']=='FeatureCollection' else trace
g['article:HUM-2018__LME_013']=geometry
p['Map geography']['Geometry']=(['key','chunk','json'],[r for key,val in g.items() for r in chunks(key,val)])
(OUT/'previous_article_geometry.json').write_text(json.dumps(old_geometry),encoding='utf-8')
assert sha(project)==fingerprint,'Project changed during registration'
write_book(project,p)
print('Exact new model registered with unsigned report, configuration and source/input hashes; no researcher verdict.',flush=True)
