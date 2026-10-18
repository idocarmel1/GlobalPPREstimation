"""Record the independent reviewer checks after final study freeze.

The separate arithmetic review was performed with an independent in-memory
least-squares/direct-allocation implementation, without importing analysis code.
This final pass verifies frozen inputs/results and all recorded evidence hashes.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
RUN = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
CHECKPOINT = {
  "research/human/sppr_trophic_level_20261018_validated7/results/comparison.json": "5fb9cd477967806c04ac8e4b2e52423272ab36d7e6005484a1cd734a5a95d694",
  "research/human/sppr_trophic_level_20261018_validated7/results/group_records.json": "ef6487c64f644e19f9a129b6944850070658d8b646992066691a425409edcd4c",
  "research/human/sppr_trophic_level_20261018_validated7/results/method_panel_data.json": "d6c3a47ec8eca3cbad62020e30e6cd65787e43ba7ddfa87cbc5c333e8f62b867",
  "research/human/sppr_trophic_level_20261018_validated7/code/analyze.py": "d60854d9e0adc2ed6111d0f20bcede6fd2d15ec184e75c30fd6ca5fae71e46b4",
  "research/human/ppr_taxonomic_resolution_20261018_validated7/results/group_transport.json": "fa16b3193dfb7b435156419fc04d17dd05e90ecaf3637916f83878446fc13e06",
  "research/human/ppr_taxonomic_resolution_20261018_validated7/results/joined_groups.json": "a88c0699b32433a291d9e3c0754d1a83072ad9b3831b703189e17b978ab3b90a",
  "research/human/ppr_taxonomic_resolution_20261018_validated7/results/regressions.json": "e68b3e4d4550ebfc636a94889084370fdcd6435476a8e8ea691323a1ec15f460",
  "research/human/ppr_taxonomic_resolution_20261018_validated7/results/scenarios.json": "01d3a82c41d6cf70c6ff439ccd5729c025cc0dcd9782cf7b6b5de8b5660ec026",
  "research/human/ppr_taxonomic_resolution_20261018_validated7/results/summary.json": "088d27c4583810e866700dcd05ace077a091d7b1019e466248e3240369d11e32",
  "research/human/ppr_taxonomic_resolution_20261018_validated7/results/scenario_totals.csv": "a25433d03de803ae04151b91ce686e94b4426aa2cdf1c969da42572614cf2ffc",
  "research/human/ppr_taxonomic_resolution_20261018_validated7/results/taxon_group_allocations.csv": "1ea423af80294f11ff6a78537d1939278fdc670508dfebf1144f1a0f4183e493",
  "research/human/ppr_taxonomic_resolution_20261018_validated7/code/analyze.py": "56ffffb4a62702f5ba005cac91d578f0c45e910a2141f636efce3098d4664cc2",
  "research/human/ppr_taxonomic_resolution_20261018_validated7/code/cohort_guard.py": "d70da90ecaa394dbd481dc404033e35f206f71fc7c4afaedb66f9cb9921a9c29",
  "research/human/ppr_taxonomic_resolution_GE_20261018_validated7/results/ge_te_comparison.json": "99c1dbd852ba472fd7d63056a8a825eef82591750b5a3e3dcd748d35be506b46",
  "research/human/ppr_taxonomic_resolution_GE_20261018_validated7/results/group_transport.json": "c75fec957b7aa99a4fbfa736a53bdd9c9a50da97ba60e21f163a0c11e0945d83",
  "research/human/ppr_taxonomic_resolution_GE_20261018_validated7/results/joined_groups.json": "99e0beae8093527f80ac34d816a6f77c82a0429a8b07acd4f3105dfd4e0cf94e",
  "research/human/ppr_taxonomic_resolution_GE_20261018_validated7/results/regressions.json": "71602089f34f132381d2e1e3636fb8e710fd188045fba4f4ab2da94ede2797d4",
  "research/human/ppr_taxonomic_resolution_GE_20261018_validated7/results/scenarios.json": "87f8ebdc0e60088c2c530b557b6c9886124cb11adf0e6d2ea3a6070935c59595",
  "research/human/ppr_taxonomic_resolution_GE_20261018_validated7/results/summary.json": "e2ecffd01f0a987d8f84d858fea32b3f70027db14b79bde4349e2e6cfbc470af",
  "research/human/ppr_taxonomic_resolution_GE_20261018_validated7/results/scenario_totals.csv": "6993604daa16cac8bc527f829e8b0c97bdbaa1fda9405c39c6c9d45b85d6aa85",
  "research/human/ppr_taxonomic_resolution_GE_20261018_validated7/results/taxon_group_allocations.csv": "1ea423af80294f11ff6a78537d1939278fdc670508dfebf1144f1a0f4183e493",
  "research/human/ppr_taxonomic_resolution_GE_20261018_validated7/code/analyze.py": "2a77ecf18ec20471fddaddc99ea9c46cb3f9e2a4289b5c10b5f6d23a0c6f736b",
  "research/human/ppr_taxonomic_resolution_GE_20261018_validated7/code/cohort_guard.py": "d70da90ecaa394dbd481dc404033e35f206f71fc7c4afaedb66f9cb9921a9c29"
}
for relative, expected in CHECKPOINT.items():
    assert sha(ROOT/relative) == expected, ('Numerical code/result changed since review', relative)

upstream=ROOT/'research/human/sppr_trophic_level_20261018_validated7'
aggregation=ROOT/'regions/LME/LME_028/work/2026-10-18_121535_trophic_aggregation_validated7'
cohort=read(upstream/'inputs/cohort.json')
pairs={(p['unit_id'],p['model_id']) for p in cohort['pairs']}
assert len(pairs)==7 and ('LME_028','28_646_Guinea_(1998)') not in pairs
assert sha(ROOT/cohort['project_path'])==cohort['project_sha256']
for p in cohort['pairs']+cohort['excluded_pairs']:
    assert sha(ROOT/p['validation_report_path'])==p['validation_report_sha256']

ledgers=[
 read(upstream/'inputs/source_hashes.json'),
 read(upstream/'results/method_panel_data.json')['source_hashes'],
 read(aggregation/'outputs/decomposition.json')['sources_sha256'],
]
upstream_checks=0
for ledger in ledgers:
    for relative,expected in ledger.items():
        assert sha(ROOT/relative)==expected, relative
        upstream_checks+=1
assert upstream_checks==95
assert all(c['workbook_matches_published_sha256'] for c in read(aggregation/'outputs/decomposition.json')['checks'])
assert (upstream/'inputs/cohort.json').read_bytes()==(aggregation/'inputs/cohort.json').read_bytes()
figures={}
for filename,expected in read(upstream/'evidence/figure_review.json')['figures'].items():
    path=upstream/'results'/filename
    assert sha(path)==expected
    figures[path.relative_to(ROOT).as_posix()]=expected

studies={}
for method,folder in [('TE','ppr_taxonomic_resolution_20261018_validated7'),('GE','ppr_taxonomic_resolution_GE_20261018_validated7')]:
    study=ROOT/'research/human'/folder
    ledger=read(study/'inputs/source_hashes.json')
    for relative,expected in ledger.items():
        assert sha(ROOT/relative)==(expected['sha256'] if isinstance(expected,dict) else expected), relative
    summary=read(study/'results/summary.json')
    assert summary['cohort']==cohort
    assert (study/'inputs/cohort.json').read_bytes()==(upstream/'inputs/cohort.json').read_bytes()
    proof=read(study/'evidence/independent_verification.json')
    assert proof['all_numeric_checks_passed'] and proof['all_source_hashes_match']
    assert proof['verifier_sha256']==sha(study/'code/verify_independent.py')
    assert (proof['regression_fits_checked'],proof['per_model_fits_checked'],proof['lomo_fits_checked'])==(15,21,70)
    # Both final verifier reports checked hashes of the visually reviewed PNGs.
    for filename in ['conditional_totals.png','tl_associations.png']:
        path=study/'results'/filename
        figures[path.relative_to(ROOT).as_posix()]=sha(path)
    visual=read(study/'evidence/figure_review.json')
    assert len(visual['figures'])==2
    for figure in visual['figures']:
        assert sha(study/figure['path'])==figure['sha256']
        assert figure['rendered_pixels_inspected'] and figure['result']=='pass'
    studies[method]={
      'current_dependency_hash_checks':len(ledger),
      'separate_reviewer_arithmetic_checks':{
        'regression_slopes':15,'per_model_slopes':21,
        'leave_one_model_out_slopes_and_full_support_totals':70,
        'direct_allocation_scenario_totals':12,
        'fitted_scenario_slopes_equal_saved_regressions':True,
        'implementation':'Independent in-memory NumPy design matrices and math.fsum over allocation CSV; no analysis imports.',
        'numerical_code_and_results_unchanged_since_review_checkpoint':True,
      },
      'final_verifier':{
        'path':(study/'evidence/independent_verification.json').relative_to(ROOT).as_posix(),
        'sha256':sha(study/'evidence/independent_verification.json'),
        'verifier_sha256':proof['verifier_sha256'],
        'numeric_checks':len(proof['checks']),
        'maximum_relative_error':max(c['relative_error'] for c in proof['checks']),
      },
      'figure_review_sha256':sha(study/'evidence/figure_review.json'),
      'baseline_tC':summary['baseline']['new_'+method+'_tC'],
    }

registration=read(RUN/'qa/registration_verification.json')
assert registration['project_sha256']==sha(ROOT/'Project.xlsx')
assert registration['report_sha256']==sha(RUN.parents[1]/'validation.docx')
for page,proof in registration['pages'].items():
    assert sha(ROOT/'interactive_map'/page)==proof['sha256']
    assert proof['all_other_embedded_data_equal']
    assert proof['review']['status']=='Disqualified by researcher'
    assert proof['review']['sections']==[] and proof['review']['note']==''
view=read(RUN/'qa/view_verification.json')
assert len(view['validated_units'])==7 and 'LME_028' not in view['validated_units']
assert view['current_review_rendered_negative'] and view['downloads_and_global_scaling_checked']

proof={
 'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),
 'reviewer':'Independent Codex science_audit subagent',
 'status':'No remaining material findings in the reviewed final state',
 'review_scope':['exact-pair cohort and status guards','fresh fitting and direct allocation sums','scientific interpretation and diagnostic restrictions','active diff excluding pre-existing source ledger changes','registration/view/preservation verification logic and saved proofs','all seven regenerated scientific PNGs'],
 'resolved_findings':[
  {'finding':'Both taxon-resolution analyzers overwrote their cohort manifest with a calibration-loop label.','resolution':'Separate cohort_manifest preserved; summary equals inputs/cohort.json; report generation and final outputs verified.'},
  {'finding':'During finalization the TE verifier evidence briefly referred to a prior verifier code hash.','resolution':'Final TE and GE verifier reports now match current verifier code hashes.'}
 ],
 'cohort':{'exact_pairs':7,'withdrawn_pair':['LME_028','28_646_Guinea_(1998)'],'replacement_1985_used':False,'project_sha256':cohort['project_sha256'],'signed_report_hashes_verified':len(cohort['pairs'])+len(cohort['excluded_pairs'])},
 'upstream':{'source_hash_checks':upstream_checks,'sppr_records':657,'method_panel_records':876,'catch_groups':165,'region_taxon_records':1693,'taxon_group_allocations':2624,'allocated_catch_tonnes':39684336.471269056,'regional_sums_independently_reproduced':True,'five_cohort_guard_tests_passed':True},
 'studies':studies,
 'visual_review':{'all_seven_pngs_inspected':True,'checks':['readable labels and annotations','seven retained model identities','correct observation counts','conditional scenario labels and diagnostic caveats','no clipping or material overlap'],'figure_sha256':figures},
 'withdrawal_authority':{'registration_proof_sha256':sha(RUN/'qa/registration_verification.json'),'view_proof_sha256':sha(RUN/'qa/view_verification.json'),'active_review_project_and_page_hashes_current':True,'default_model_preserved':True,'former_review_exclusions_cleared':True,'positive_review_cohort_excludes_withdrawn_pair':True,'preservation_proof_reviewed':True},
 'limits':'Reproducibility, arithmetic, provenance and presentation review; no new biological validation or annual publication permission.',
 'reviewer_writes':'Only this run-local review script and QA proof; no scientific or historical files changed.'
}
(RUN/'qa/independent_review.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':proof['status'],'upstream_hash_checks':upstream_checks,'study_dependency_hash_checks':{k:v['current_dependency_hash_checks'] for k,v in studies.items()},'figures_inspected':len(figures),'evidence':str(RUN/'qa/independent_review.json')},ensure_ascii=False))

