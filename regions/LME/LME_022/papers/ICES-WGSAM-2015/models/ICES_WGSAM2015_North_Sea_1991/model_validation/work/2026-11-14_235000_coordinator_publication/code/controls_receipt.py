from pathlib import Path
import hashlib,json
run=Path(__file__).resolve().parents[1]
files=['code/check_published_controls.js','inputs/display_exclusions.json','inputs/negative_reviews.json']
qa={'node_syntax_check_passed':True,'checker_executed':False,'published_payloads_read':False,'browser_UI_checked':False,'expected_prior_units':9,'ICES_added':True,'negative_models_declared':4,'new_negative_exact_pairs':3,'scope':'Prepared Node payload/control checker; static syntax check only','hashes':{p:hashlib.sha256((run/p).read_bytes()).hexdigest() for p in files}}
(run/'qa/controls_preparation.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
