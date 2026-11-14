"""Prepare the authorized discard sensitivity without modifying baseline inputs."""
from pathlib import Path
import hashlib
import json
import runpy
import shutil

RUN_ID = 'discards_div10_20261114'
ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT.parents[2]
BASELINE = ROOT.parent / 'pooled_20261114'
REPO = next(p for p in MODEL.parents if (p / 'Project.xlsx').is_file())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    check = runpy.run_path(str(REPO / 'tools/skills/paper-to-ppr/scripts/check_evidence.py'))['check']
    baseline_check = check(BASELINE / 'evidence_index.json')
    assert baseline_check['complete'], baseline_check
    original = BASELINE / 'code/run_diagnostics.py'
    assert sha(original) == '4c58242906ad2386c02f1949d9d92fbf0ab0921c92f40d95e2dc7e28c814cdf2'
    assert sha(MODEL / 'model.json') == '281d8543a165bf67652168cbc47f09db224e51bddb6768e9365f8c52d03ac956'
    index = json.loads((BASELINE / 'evidence_index.json').read_text(encoding='utf-8'))
    pinned = []
    for item in index['computational_input_identity']['executed_engine']:
        source = BASELINE / item['pinned_path']
        assert sha(source) == item['sha256'], source
        target = ROOT / item['pinned_path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        pinned.append({**item, 'sha256': sha(target)})

    text = original.read_text(encoding='utf-8')
    replacements = [
        ('pooled_20261114', RUN_ID),
        ("BASE_ID =", "VARIANT_ID = MODEL_ID + '__discards_div10_six_groups'\nDISCARD_FACTOR = 0.1\nSCALED_GROUPS = (1, 2, 3, 4, 11, 12)\nBASE_ID ="),
        ("    engine = repo / 'tools/scientific_code/PPREstimation'", "    pinned_root = Path(__file__).resolve().parent / 'executed_engine'\n    engine = pinned_root / 'tools/scientific_code/PPREstimation'\n    serializer = pinned_root / 'tools/scientific_helpers/sppr/method_coverage.py'\n    if sha(model_path) != '281d8543a165bf67652168cbc47f09db224e51bddb6768e9365f8c52d03ac956':\n        raise ValueError('Pooled baseline model changed')\n    if sha(serializer) != 'f855b88eebeb52d8814b0eb1dc8e9ed37e943fe62ed77d5bec88522b1cf19905':\n        raise ValueError('Pinned serializer changed')\n    if sha(engine / 'create_PPRS_excel.py') != '5f94a4d885643e706a57a9e8faa1bf9fa5338e8626831d74dfe59f2d833158a1':\n        raise ValueError('Pinned exporter changed')"),
        ("repo / 'tools/scientific_helpers/sppr/method_coverage.py']", "serializer]"),
        ('    from tools.scientific_helpers.sppr.method_coverage import encode_lossless', "    import importlib.util\n    spec = importlib.util.spec_from_file_location('pinned_sensitivity_serializer', serializer)\n    serialization = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(serialization)\n    encode_lossless = serialization.encode_lossless"),
        ("                totals = fishery_totals(base, source_ids)", "                totals = fishery_totals(base, source_ids)\n                baseline_totals = copy.deepcopy(totals)\n                factor = DISCARD_FACTOR if int(seq) in SCALED_GROUPS else 1.0\n                if factor != 1.0:\n                    totals['discards'] = float(Decimal(str(totals['discards'])) * Decimal(str(factor)))\n                    totals['catch'] = float(Decimal(str(totals['landings'])) + Decimal(str(totals['discards'])))"),
        ("                               **totals, 'destination_pool_id': pool,", "                               **totals, 'baseline_landings': baseline_totals['landings'],\n                               'baseline_discards': baseline_totals['discards'],\n                               'baseline_catch': baseline_totals['catch'],\n                               'discard_multiplier': factor,\n                               'destination_pool_id': pool,"),
        ("                'routing_is_assumption': True, 'fraction_returned': 1.0,", "                'routing_is_assumption': True, 'fraction_returned': 1.0,\n                'discard_scaling_is_assumption': True,\n                'discard_multiplier': DISCARD_FACTOR, 'scaled_group_ids': list(SCALED_GROUPS),\n                'scope': 'Hypothetical sensitivity; not a published-parameter correction',"),
        ("    summary = {'schema_version': 1, 'unit_id': 'LME_026', 'model_id': MODEL_ID,", "    summary = {'schema_version': 1, 'unit_id': 'LME_026', 'model_id': MODEL_ID,\n               'variant_id': VARIANT_ID, 'run_id': 'discards_div10_20261114',\n               'scenario': {'discard_multiplier': DISCARD_FACTOR, 'scaled_group_ids': list(SCALED_GROUPS),\n                            'biological_parameters_changed': False, 'canonical_input_changed': False},"),
        ("'custom_audited_pooled_discard_bridge'", "'custom_audited_pooled_discard_bridge_div10_six_groups'"),
        ("This saved runner, original fleet evidence, and the distinct pooled model are required; a stock constructor alone does not reproduce internal discard returns.", "This saved runner multiplies donor discards and pooled returns by 0.1 for IDs1,2,3,4,11,12 before construction, preserving biology and applying EE floor ON0.1 once. This is hypothetical, not an extraction correction. A stock constructor cannot reproduce this runtime."),
        ("'model_id': MODEL_ID, 'required_methods': list(METHODS)", "'model_id': MODEL_ID, 'variant_id': VARIANT_ID, 'required_methods': list(METHODS)"),
    ]
    for old, new in replacements:
        assert old in text, old
        text = text.replace(old, new)
    text = text.replace('Run only GE/TE/With Egestion for the authorized pooled Mediterranean scenario.', 'Run the authorized six-group discards-divided-by-ten pooled sensitivity.')
    compile(text, str(ROOT / 'code/run_diagnostics.py'), 'exec')
    (ROOT / 'code/run_diagnostics.py').write_text(text, encoding='utf-8')
    manifest = {
        'run_id': RUN_ID, 'variant_id': 'Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114__discards_div10_six_groups',
        'authorization': 'User requested factor-10 sensitivity and explicitly confirmed Divide discards by10 for the six flagged groups.',
        'baseline_runner_path': '../pooled_20261114/code/run_diagnostics.py',
        'baseline_runner_sha256': sha(original), 'runner_sha256': sha(ROOT / 'code/run_diagnostics.py'),
        'baseline_index_sha256': sha(BASELINE / 'evidence_index.json'),
        'baseline_verification': baseline_check,
        'canonical_model_sha256': sha(MODEL / 'model.json'),
        'discard_multiplier': 0.1, 'scaled_group_ids': [1, 2, 3, 4, 11, 12],
        'scope': 'Runtime sensitivity only; no canonical-model changes, new selection, researcher decision or publication.',
        'pinned_executed_engine': pinned,
        'runner_modifications': [{'before': old, 'after': new} for old, new in replacements],
    }
    (ROOT / 'preparation.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'plan.md').write_text('''# Discards divided by ten: pooled model sensitivity

User-authorized hypothesis: multiply discards by 0.1 for Bottlenose dolphin (1), Striped dolphin (2), Common dolphin (3), Fin whale (4), Loggerhead turtle (11) and Green turtle (12). Reduce donor catch and internal discard returns together. Landings, living biological parameters, diets and missingness remain unchanged. This is not an extraction correction.

Reuse the authenticated pooled initialization, 100% pooled routing and exact pinned engine. Apply EE floor ON at 0.1 once after staging; retain the external mortality sink and verify EE = 1 - M0/P, where M0 enters pooled detritus. Retain zero missing living BA/migration and existing default GS assumptions. Refresh the calculated detritus stock residual through the same engine.

Run GE, TE and With Egestion once each, retaining their full returns and SPPR/A/L matrices, coefficients, masks, negative-entry tables and diagnostic grades. Method settings remain det_collapse_mode=never, det_open_mode=none, det_theta=1, det_external_sppr=0 and fix_EE_0_cases=False. No diet normalization, forced balance or parameter repair.

The saved baseline cannot answer the changed-flow scenario. Compare its authenticated floor-ON-at-0.1 results with the new execution, including signed production residuals, global PP budgets and SPPR coefficients. The baseline run took approximately two minutes; allow several minutes plus QA. Output remains model-local, ordinarily a few MB. No workbooks, DOCX, source inputs, selected model, Project.xlsx, map/trends or review records are changed.
''', encoding='utf-8')
    print(json.dumps({'prepared': True, 'runner': str(ROOT / 'code/run_diagnostics.py'), 'baseline_artifacts_verified': len(baseline_check['verified_artifacts'])}))


if __name__ == '__main__':
    main()
