from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
RUN=Path(__file__).resolve().parents[1];MODEL=Path(__file__).resolve().parents[4]
ROOT=next(p for p in MODEL.parents if (p/'Project.xlsx').exists())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
assert load(RUN/'qa/final_verification.json')['status']=='PASS'
visual=dict(status='PASS',renderer='Separate hidden read-only Word and Excel COM instances; PDF rasterized with PyMuPDF',
 validation_report_pages=7,source_correction_rationale_pages=2,
 inspected_all_DOCX_pages=True,spreadsheet_sheets_inspected=['Validation summary','Negative SPPR','Sources','Taxon mappings','mapping Sources'],
 appendix_opened_in_Excel_without_repair=True,original_workbooks_not_saved_by_Office=True,
 fallback_reason='Bundled LibreOffice executable unavailable; dependency package paths verified before Office fallback.',
 fixes='Removed overlapping worksheet filter; native filters retained and extended Sources filter synchronized.',
 limitations='Only representative spreadsheet ranges rendered; all 218 rows and all six matrices structurally checked.')
dump(RUN/'qa/visual_review.json',visual)
artifacts=[MODEL/'model.json',MODEL/'model_notes.md',MODEL/'model_validation/validation.docx',
 MODEL/'model_validation/source_value_corrections.docx',MODEL/'model_validation/taxon_mapping.xlsx',MODEL/'sppr_source.xlsx',
 ROOT/'regions/LME/LME_013/LME_013.xlsx',ROOT/'Project.xlsx',MODEL/'results/regional_snapshot.xlsx',MODEL/'results/result_manifest.json']
sources=[MODEL.parents[1]/'sources'/n for n in ['1-s2.0-S0079661117303312-main.pdf','Supplementary material revised and final.xls']]
files=[p for area in ['code','outputs','qa'] for p in (RUN/area).rglob('*') if p.is_file()]
index=dict(schema_version=1,created_utc=datetime.now(timezone.utc).isoformat(),model_id=MODEL.name,
 current_run=RUN.relative_to(MODEL).as_posix(),accepted_model_sha256=sha(MODEL/'model.json'),
 scope='Authorized source corrections and full standard validation, with unpooled and pooled direct SPPR comparisons and regional integration.',
 methods=load(RUN/'outputs/validation_summary.json')['methods'],
 verification='PASS',scientific_status='Living mass balance passes; all GE/TE/With Egestion overall FAIL grades retained.',
 source_rationale='Article and author supplement only; independently read source cells retain actual source hash.',
 uncertainty='Monte Carlo NOT_RUN; no current uncertainty bounds claimed.',
 map='Not refreshed by this workflow; corrected model absent from map; independently changed HTML files documented in qa/map_deferred.json.',
 researcher_review='pending; no verdict or signature registered',production_eligible=False,
 source_files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources],
 delivered_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in artifacts],
 evidence_files=[dict(path=p.relative_to(MODEL).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(files)])
dump(MODEL/'model_validation/evidence/evidence_index.json',index)
print('Current evidence index complete:',len(files),'run files and',len(artifacts),'current artifacts.')
