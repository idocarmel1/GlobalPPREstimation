"""Save the final compact observed QA summary without further artifact edits."""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

run = Path(__file__).resolve().parents[1]
qa = run / 'qa'
log = qa / 'new_word_trial.json'
audit = json.loads(log.read_text(encoding='utf-8-sig'))
events = [json.loads(x) for x in (qa / 'new_word_trace.jsonl').read_text(encoding='utf-8').splitlines()]
counts = Counter(x['path'] for x in events)
audit['trace_summary'] = {'events': len(events), 'unique_paths': len(counts), 'repeated_reads': sum(n-1 for n in counts.values()),
                        'workbook_parses': sum(x['workbook_parses'] for x in events), 'read_bytes': sum(x['bytes'] for x in events),
                        'path_counts': dict(counts), 'token_telemetry': 'unavailable'}
audit['link_verification_limitation'] = 'No original broken targets found: all15appendixrelationships point to13existing original files; those targets are intentionally absent from the bounded clone. All stored links remain unchanged.'
audit['render_evidence_reuse']['basis'] = 'All 17 named DOCX package parts are byte-for-byte identical; only ZIP packaging and timestamps were disregarded.'
audit['render_evidence_reuse']['prior_pixel_comparison'] = 'Only page 3 heading pixels differ from the original; pages 1, 2, 4, 5 and 6 are identical.'
audit['visual_review']['reason'] = 'All 17 named ZIP parts are identical to the finalized document with existing six-page inspection proof.'
audit['qa_finalized_utc'] = datetime.now(timezone.utc).isoformat()
summary = {
    'status': 'Verified bounded heading edit with explicitly reused all-six-page rendering evidence',
    'report': audit['report'],
    'preservation': audit['final_preservation'],
    'rendering': {'all_named_DOCX_parts_identical_to_previously_rendered_final': True,
                  'parts_compared': 17, 'reused_inspected_pages': [1,2,3,4,5,6], 'new_successful_PDF_exports': 0,
                  'new_render_attempts_after_resume': 0, 'evidence': audit['render_evidence_reuse']['evidence'],
                  'evidence_sha256': audit['render_evidence_reuse']['evidence_sha256_from_trace_cli']},
    'appendix_links': {'missing_relationships_in_bounded_clone': 15, 'unique_original_targets': 13,
                       'original_targets_existing_and_hashed': 13, 'original_broken_targets': 0,
                       'links_changed': 0, 'checks': 'Existence and byte hashes only; scientific contents not interpreted'},
    'percentage_check': 'passed',
    'trace': {k:v for k,v in audit['trace_summary'].items() if k != 'path_counts'},
    'timing': {'initial_trace_start_utc': audit['trace_created_utc'], 'initial_user_stop_utc': audit['stopped_utc'],
               'initial_phase_wall_seconds': audit['wall_seconds_trace_creation_to_stop'],
               'resumed_binary_verification_start_utc': audit['resumed_verification_started_utc'],
               'resumed_binary_verification_end_utc': audit['resumed_verification_completed_utc'],
               'resumed_binary_verification_seconds': audit['resumed_verification_seconds'],
               'finalized_utc': audit['qa_finalized_utc'],
               'whole_resumed_turn_wall_seconds': 'not instrumented; binary verification duration is not a whole-turn duration',
               'environment_retries': 'Preserved separately in detailed operations; no environment setup or reused rendering savings attributed to skill routing'},
    'processes': 'No COM or process mutation after resume; prior Word sessions were preserved during earlier cleanup',
    'detailed_qa': str(log), 'trace_file': str(qa / 'new_word_trace.jsonl')}
log.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
(qa / 'new_word_trial_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False))
