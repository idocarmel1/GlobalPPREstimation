"""Aggregate observed traces and evidence limits, without scientific adoption."""
import collections
import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parent.parent
QA = RUN / 'qa'
def load(path): return json.loads(path.read_text(encoding='utf8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def trace(name):
    rows = [json.loads(line) for line in (QA / (name + '_trace.jsonl')).read_text(encoding='utf8').splitlines() if line.strip()]
    references = [r for r in rows if r['operation'] == 'read' and
                  (r['path'] in ['AGENTS.md', 'README.md'] or r['path'].startswith(('tools/skills/', 'tools/templates/', 'explainers/')) or
                   '/inputs/old_' in r['path'])]
    crossing = [r for r in references if name == 'old_word' and r['path'] == 'tools/skills/paper-to-ppr/SKILL.md']
    references = [r for r in references if r not in crossing]
    return {'raw_events': len(rows), 'raw_unique_paths': len({r['path'] for r in rows}),
            'project_instruction_requests': len(references),
            'unique_project_instructions': len({r['path'] for r in references}),
            'repeated_project_instruction_requests': len(references) - len({r['path'] for r in references}),
            'workbook_parses': sum(r['workbook_parses'] for r in rows),
            'reader_seconds': sum(r['elapsed_seconds'] for r in rows),
            'content_bytes': sum(r['bytes'] for r in rows),
            'excluded_version_crossing_rows': crossing,
            'trace_sha256': sha(QA / (name + '_trace.jsonl'))}

traces = {name: trace(name) for name in ['old_pipeline', 'new_pipeline', 'old_validation', 'new_validation', 'old_word', 'new_word']}
benchmark = load(QA / 'workbook_read_benchmark.json')
blind = load(QA / 'blind_extraction_comparison.json')
diagnostics = load(QA / 'diagnostic_replication.json')
word = load(QA / 'new_word_trial.json')
mapping = load(QA / 'single_mapping_handoff_trial.json')
result = {
    'checked_at': datetime.now(timezone.utc).isoformat(),
    'purpose': 'Bounded skill routing and read reuse; preserve scientific instructions and once-per-run mapping across both skills',
    'baseline_commit': '85ae543693887a5439fb13ebd84bcb91f8ecc360',
    'actual_traces': traces,
    'cold_task_wall_seconds': {'pipeline_explanation': {'old': 168, 'new': 122.409},
                               'validation_definition': {'old': 192, 'new': 104},
                               'word': {'old': 757.520573, 'new_pre_pause_environment_dominated': 1317.558932}},
    'controlled_workbook': benchmark,
    'measurement_limits': [
        'One fresh matched agent per instruction variant/task; observed rereads, output truncation and environmental retries retained.',
        'Project instruction counts exclude shared system-skill/helper reads; raw traces retain them.',
        'Old Word read a revised pipeline entry before checkpoint correction; that row remains raw and is excluded only from matched project instruction counts.',
        'Revised explanation benchmarks preceded the extra single-mapping paragraph. Routing/read scope is unchanged; no token-length or subsequent wall-time claim is inferred.',
        'Word total elapsed time is confounded by renderer failures, reused environment knowledge and user pause. Resume package verification is separate; no general Word speedup is claimed.',
        'Workbook benchmark alternates variants in one process with uncontrolled OS caches; SHA reads cause more file opens even while parsing is reduced.',
        'Tokens and monetary cost unavailable. Deterministic AST zero-token records are not semantic-agent usage measurements.'
    ],
    'replication': {
        'original_publication': {'role': 'fresh blind source extraction, conversion, round trip and raw load',
            'groups': blind['groups'], 'known_basic_cells_exact': blind['known_basic_cells'],
            'positive_diet_cells_exact': blind['blind_positive_diets'],
            'roundtrip_cells_exact': blind['roundtrip']['cells_checked'],
            'canonical_fields_masks_roles_equal': False,
            'mask_differences': blind['diet_mask_difference_count'],
            'remaining': 'Strict diet-tolerance construction fails; source unknowns and native stanza equations remain unsupported. Names/role flags/derived versus unknown fields differ. No source repair or adoption.'},
        'json_only': {'role': 'supplied canonical candidate consumption/raw loader check; not paper extraction',
            'evidence': 'json_input_check.json', 'remaining': 'Original publication/provenance unavailable in current package.'},
        'diagnostics': {'role': 'tool regeneration using exact historical code and explicitly distinct current compatibility settings',
            'full_reports_matrices_exact': diagnostics['exact_historical_full_direct_returns_and_runtime_equivalent'] and diagnostics['current_compatibility_full_direct_returns_and_runtime_equivalent'],
            'saved_coefficients_reconciled': diagnostics['all_trials_equivalent_under_frozen_policy'],
            'remaining': 'GE/TE aggregate saved coefficients exceed frozen absolute1e-12; max4.65661e-10. Full reports/matrices/statuses/masks are exact. No tolerance relaxation.'},
        'mapping': {'role': 'saved interpretation reused; independently verified arithmetic and same-decision-set handoff',
            'arithmetic_evidence': 'mapping_arithmetic_check.json', 'handoff': mapping},
        'word': {'role': 'independent minimal edit and package/manual/link checks; existing visual evidence reused after all17named parts match',
            'all_parts_identical': word['resumed_final_package_comparison']['all_named_parts_identical'],
            'pages_covered_by_reused_render': word['render_evidence_reuse']['page_count'],
            'fresh_revised_pdf_exports': 0,
            'original_appendix_broken_relationships': word['original_appendix_target_checks']['original_broken_relationships'],
            'signoff_parser_summary_equal': load(QA / 'word_signoff_parser_check.json')['summary_equal'],
            'adoption': 'Not adopted; artificial heading edit changes parser-captured sections. Shared router now requires the conditional parser compatibility check.'},
        'signed_review': {'validated_source_sync': 'review_sync_validated_trial.json',
            'real_rejection_guard': 'review_sync_trial.json',
            'remaining': 'Real LME027 rejection sync blocked before writes by inherited missing source hyperlink; synthetic rejection/date/freshness regressions passed separately.'},
        'full_pipeline_replication': False,
        'scientific_adoption_or_repair': False
    },
    'checks': {'focused_dependency_run': '52methods passed, including8 earlier ReadSession methods; 11final ReadSession methods pass separately,55distinct methods exercised',
               'fresh_reviews': ['independent_code_review.json', 'graph_refresh_code_review.json'],
               'unchanged_scientific_baseline_limits': ['decimal diet-sentinel regression', 'apostrophe validator disagreement', '8construction restrictions', '25unknown historical execution snapshots', 'LME038current coefficients pending', 'originally missing references'],
               'live_protection': 'final_protection_verification.json'},
    'graph_publication_state': 'Recorded separately in final_closure.json after current source/graph/staging/remote checks; this summary never promotes a partial scientific pipeline.'
}
inputs = [p for p in QA.glob('*.json') if p.name not in ['completion_report.json', 'final_closure.json']]
result['evidence_hashes_at_summary'] = {p.name: sha(p) for p in inputs}
(QA / 'completion_report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'instruction_requests': {k: v['project_instruction_requests'] for k,v in traces.items()},
                  'workbook_parses': {k: v['workbook_parses'] for k,v in traces.items()},
                  'source_basic_diet_numeric_exact': not blind['basic_parameter_differences'] and not blind['diet_numeric_differences'],
                  'full_pipeline_replication': False}))
