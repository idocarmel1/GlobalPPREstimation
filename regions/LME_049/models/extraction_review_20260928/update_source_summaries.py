from pathlib import Path
import json
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_049';P=Path(__file__).parent/'metadata_registration_proposal.json';proposal=json.loads(P.read_text(encoding='utf-8'))
for record in proposal['paper_updates']:
    pid=record['paper_id'];old=pid=='KUR-2019';mp=REG/'papers'/pid/'metadata.json';meta=json.loads(mp.read_text(encoding='utf-8'))
    meta['legacy_loadability_class_before_extraction']=meta.get('loadability_class');meta['loadability_class']='Source tables extracted; SPPR loader blocked by missing routing' if old else 'Source tables extracted; conditional loader run completed, scientific diagnostics FAIL'
    meta['model_file_status']='extracted_canonical_json_with_missingness';meta['extraction_readiness']='extracted_with_explicit_source_limits';meta['download_failure_reason']='Publisher supplement exact-byte retrieval blocked HTTP401; main PDF verified locally.' if old else None
    meta['quality_rationale']='Historical numeric quality scores have not been reassessed. '+meta['loadability_class']+'. See source/model extraction evidence; this is not production adoption.'
    meta['loadability_evidence']=record['notes'];meta['documentation_evidence']=record['notes']
    if not old:meta['recommendation']='Complementary 2023 candidate; not selected. Fifty-four censored diet cells remain unresolved; conditional GE/TE/With Egestion diagnostics FAIL and both MC methods accept0/100.'
    mp.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    record.update({k:meta[k] for k in ['loadability_class','model_file_status','extraction_readiness','download_status','downloaded_file_count','download_failure_reason','quality_rationale','loadability_evidence','documentation_evidence','recommendation']})
    readme=REG/'papers'/pid/'README.md';text=readme.read_text(encoding='utf-8')
    update=f'''## Verified extraction update 2026-09-28

The main PDF is present and its exact bytes are verified in the model source manifest. {'The identified publisher supplement remains unavailable for exact-byte download (HTTP401 bot check).' if old else 'The author DOCX supplement is present; all five tables were inspected.'} The earlier source availability and quality narrative below is an inherited historical assessment and is superseded by this update.

Candidate: `{next(x['model_id'] for x in proposal['models'] if x['paper_id']==pid)}`; {record['functional_groups']} groups; modeled year {record['model_years']}. {meta['recommendation']}

Source-faithful extracted tables, taxonomy, canonical JSON, validation and candidate-only diagnostics: [extraction report](../../models/{next(x['model_id'] for x in proposal['models'] if x['paper_id']==pid)}/extracted_tables/REPORT.md). No exact model was selected for production.

'''
    readme.write_text(update+text,encoding='utf-8')
P.write_text(json.dumps(proposal,ensure_ascii=False,indent=2),encoding='utf-8')
