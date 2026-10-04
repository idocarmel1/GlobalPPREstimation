"""Portable native evidence inventory; run after all cohort files are frozen."""
from pathlib import Path
import hashlib,json,os
H=Path(__file__).resolve().parent
ROOT=next(p for p in H.parents if (p/'Project.xlsx').exists())
CAND=H.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
artifacts=[]
def add(role,p):
 artifacts.append(dict(role=role,availability='present',path=Path(os.path.relpath(p,H)).as_posix(),sha256=sha(p)))
roles={'model.json':'native_model','final_verification.json':'actual_reload_physical_gate',
 'native_reload_result.json':'actual_native_state','runtime_settings.json':'runtime_settings',
 'runtime_provenance.json':'runtime_provenance','reload_consistency.json':'repeat_reload_consistency','source_to_final_ledger.json':'all_departures',
 'food_component_ledger.json':'food_and_import_evidence','case_coverage.json':'required_variant_coverage',
 'alternative_hypotheses.json':'alternative_hypotheses','all_arrow_decisions.json':'all_source_arrow_decisions',
 'ewe_roundtrip_verification.json':'eight_import_roundtrip','microbial_split_consistency.json':'microbial_assumption_consistency',
 'REPORT.md':'native_findings','protected_source_hashes.json':'source_preservation',
 'diagnostics/GE_lossless_return.json':'GE_full_direct_return','diagnostics/TE_lossless_return.json':'TE_full_direct_return',
 'diagnostics/With_Egestion_lossless_return.json':'WithEgestion_full_direct_return',
 'diagnostics/serialization_masks.json':'diagnostic_masks','diagnostics/reconciliation.json':'diagnostic_reconciliation',
 'diagnostics/scope_arithmetic_metrics.json':'scope_arithmetic_precision','diagnostics/scoped_SPPR.csv':'scoped_coefficients',
 'diagnostics/negative_entries.csv':'negative_entry_table','sensitivity/F62_summary.json':'F62_sensitivity',
 'ewe_imports/constructor_admission_ledger.json':'converter_admission_ledger'}
eight=['Basic_input','Diet_composition','Landings','Discards','Detritus_fate','Biomass_accumulation','TL','Metadata']
for p in H.rglob('*'):
 if not p.is_file() or p.name in ['evidence_index.json','evidence_completeness.json'] or '__pycache__' in p.parts:continue
 rel=p.relative_to(H).as_posix();role=roles.get(rel,'retained_native_evidence')
 if p.parent==H/'ewe_imports' and p.stem in eight:role='EwE_import_'+p.stem
 if p.parent==H/'exporter_code':role='exporter_code_identity'
 add(role,p)
papers=ROOT/'regions/LME_052/papers/OKH-GM2019'
for name in ['gorbatenko_melnikov_2019.pdf','gorbatenko_2018_dissertation.pdf','gorbatenko_melnikov_2019_English_translation.pdf']:add('original_source_document',papers/name)
for name in ['model.json','carbon_reconstruction.json','conversion_factors.json','accepted_decisions.json','extraction.json']:
 add('accepted_source_baseline',CAND/'assumption_variants/researcher_readings_20261003'/name)
source=CAND/'research_20261003/source_feeding_repairs'
for name in ['evidence_index.json','candidate_constraints.json','diet_import_plan.json',
 'hyperiid_salmon/salmon_group8_prey_ledger.json','hyperiid_salmon/hyperiid_other_food_evidence.json',
 'jellyfish_text_diet/aggregated_source_prey_categories.json','jellyfish_error_audit/hypotheses.json']:
 p=source/name
 if p.is_file():add('recovered_source_evidence',p)
for name in ['PPRCalculator.py','ModelData.py','utils.py']:add('unchanged_scientific_engine',ROOT/'tools/scientific_code/PPREstimation'/name)
verification=read(H/'final_verification.json');recon=read(H/'diagnostics/reconciliation.json')
protected=read(H/'protected_source_hashes.json')
baseline_keys=[key for key in protected['before'] if not key.endswith('Project.xlsx')]
recon.update({'primary_source_hash_matches_handoff':sha(papers/'gorbatenko_melnikov_2019.pdf')=='70b73d4341018e3fadb9955e9d19735188f12c8798eaed8921d1812bb6c2b860',
 'supporting_source_hash_matches_handoff':sha(papers/'gorbatenko_2018_dissertation.pdf')=='a26ef69acf1c00b32f49772e52b66f85baa79cf1e0ba3fecefe3800827787d45',
 'protected_source_model_baselines_unchanged':all(sha(ROOT/key)==protected['before'][key] for key in baseline_keys)})
index=dict(schema_version=1,run_id='LME052-GM2019-BALANCED-20261003',region_id='LME_052',
 model_id='52_GM2019_Fig9_Pelagic_balanced_(2000-2014)',variant_id='adopted_balanced_20261003',
 source_identity={'primary_pdf_sha256':'70b73d4341018e3fadb9955e9d19735188f12c8798eaed8921d1812bb6c2b860',
 'supporting_pdf_sha256':'a26ef69acf1c00b32f49772e52b66f85baa79cf1e0ba3fecefe3800827787d45'},
 computational_input_identity={'path':'model.json','sha256':sha(H/'model.json'),'settings':'runtime_settings.json','code':'runtime_provenance.json'},
 methods=['Actual native PPRCalculator balance','GE','TE','With Egestion','F62 sensitivity','Eight import field/runtime roundtrip'],
 required_roles=sorted(set(roles.values())|{'original_source_document','accepted_source_baseline','unchanged_scientific_engine','exporter_code_identity'}|{'EwE_import_'+name for name in eight}),
 artifacts=artifacts,reconciliation={**{k:bool(v) for k,v in verification['gates'].items()},**{k:bool(v) for k,v in recon.items()}},
 scope='Native model/extraction/directdiagnostics only. Overallregional/report/maphandoff coordinatedseparately. Inventoryintegritydoesnotvalidatescientificassumptions.')
(H/'evidence_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Indexed',len(artifacts),'native evidence artifacts; input',sha(H/'model.json'))
