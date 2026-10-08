from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
RUN=Path(__file__).resolve().parents[1];MODEL=Path(__file__).resolve().parents[4]
ROOT=next(p for p in MODEL.parents if (p/'Project.xlsx').exists())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
qa=json.loads((RUN/'qa/publication_checks.json').read_text(encoding='utf-8'))
assert qa['status']=='PASS'
assert sha(MODEL/'model.json')==sha(RUN/'inputs/model.json')
index={'schema_version':1,'created_utc':datetime.now(timezone.utc).isoformat(),'model_id':MODEL.name,'scope':'Signed conditional researcher approval; fresh auto diagnostics, exact matrix equivalence, protected numerical inputs and bounded publication. Source, mapping and geography validation reused.','current_run':RUN.relative_to(MODEL).as_posix(),'base_validation_evidence':'model_validation/work/2026-10-08_132433_balanced_validation','accepted_model_sha256':sha(MODEL/'model.json'),'researcher_review':{'status':'Validated by researcher','researcher_name':qa['reviewer'],'review_date':qa['review_date'],'condition':qa['condition'],'excluded_names':qa['excluded_names']},'production_eligible':False,'scientific_status':'GE, TE, With Egestion engine overall FAIL unchanged. Human conditional approval remains distinct.','map':{'status':'published and verified at this handoff','Project_sha256_at_publication':qa['Project_sha256'],'HS_077_preserved_at_publication':True},'methods':json.loads((RUN/'outputs/auto/methods_summary.json').read_text(encoding='utf-8')),'source_rationale':'model_validation/source_value_corrections.docx','uncertainty':'No Monte Carlo rerun or current uncertainty bounds.'}
index['delivered_artifacts']=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [MODEL/'model.json',MODEL/'model_notes.md',MODEL/'sppr_source.xlsx',MODEL/'model_validation/validation.docx',MODEL/'model_validation/taxon_mapping.xlsx',MODEL/'results/result_manifest.json',MODEL/'results/regional_snapshot.xlsx',ROOT/'regions/LME/LME_013/LME_013.xlsx']]
index['evidence_files']=[{'path':p.relative_to(MODEL).as_posix(),'sha256':sha(p)} for p in sorted(RUN.rglob('*')) if p.is_file() and p.suffix not in ['.png','.pdf','.xlsx','.docx']]
(MODEL/'model_validation/evidence/evidence_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print('Current evidence index updated; canonical model unchanged; exact publication QA retained.')
