from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=BASE.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((BASE/'diagnostics/run_manifest.json').read_text(encoding='utf-8'))
engine={n:sha(ROOT/'tools/scientific_code/PPREstimation'/n) for n in old['engine']}
assert engine==old['engine'], 'Engine mismatch'
assert sha(BASE/'source/computational/model.json')==old['input_sha256'], 'Input mismatch'
code=(BASE/'diagnostics/run_direct_candidate.py').read_text(encoding='utf-8')
code=code.replace('HERE / "vendor"','HERE.parent / "diagnostics" / "vendor"')
code=code.replace('det_collapse_mode="never"','det_collapse_mode="auto"')
code=code.replace('HUM2018_20261003_detailed_source_candidate','HUM2018_20261003_auto_preflight')
code=code.replace('not authorized; candidate evidence only','Conditional selection authorized after successful preflight; no researcher verdict authorized')
(OUT/'run_direct_auto.py').write_text(code,encoding='utf-8')
paths=[ROOT/'Project.xlsx',ROOT/'regions/LME_013/LME_013.xlsx',
       *(ROOT/'regions/LME_013').glob('*.docx'),*(ROOT/'regions/LME_013').glob('*appendix*.xlsx'),
       *(ROOT/'interactive_map').rglob('*.html'),ROOT/'tools/knowledge_graph/graph.json',
       BASE/'source/resolved_native/model.json',BASE/'source/computational/model.json',
       BASE/'mapping/mapping_review.json',BASE/'diagnostics/run_manifest.json']
(OUT/'active_baseline.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in paths},ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'comparison_setup.json').write_text(json.dumps({'engine_matches':True,'input_matches':True,'never_manifest_sha256':sha(BASE/'diagnostics/run_manifest.json')},indent=2),encoding='utf-8')
print('Controlled input and engine match; isolated driver ready.',flush=True)
