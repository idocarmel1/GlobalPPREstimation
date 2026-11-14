from pathlib import Path
import json,hashlib,os,shutil
ROOT=Path(__file__).resolve()
while not (ROOT/'Project.xlsx').exists():ROOT=ROOT.parent
MODEL=ROOT/'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991'
BASE=MODEL/'model_validation'; EVIDENCE=BASE/'evidence'
REVIEW=ROOT/'regions/LME/LME_022/work/2026-11-14_160000_validation/outputs'
RESULTS=MODEL/'results/diagnostics/2026-11-14_validation'
artifacts=[]
def add(role,path):
    assert path.is_file(),path
    artifacts.append({'role':role,'path':os.path.relpath(path,EVIDENCE).replace('\\','/'),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'availability':'present'})
for name in ['candidate_review.json','mapping_audit.json','diagnostics_geography.json']:
    dest=EVIDENCE/'source_review'/name
    shutil.copy2(REVIEW/name,dest)
    if name!='mapping_audit.json':
        data=json.loads(dest.read_text(encoding='utf-8'))
        data['evidence_time_scope']='Saved-evidence assessment and comparison, supplemented by the separately authorized fresh ICES diagnostic attempts. The linked current attempt evidence is authoritative for the new execution outcomes.'
        data['fresh_diagnostic_attempts']=os.path.relpath(RESULTS,dest.parent).replace('\\','/')
        dest.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
for role,path in [
 ('report',BASE/'validation.docx'),('taxon_appendix',BASE/'taxon_mapping.xlsx'),
 ('source_model',MODEL/'model.json'),('source_departures',MODEL/'model_notes.md'),
 ('mapping_audit',EVIDENCE/'source_review/mapping_audit.json'),
 ('comparison',EVIDENCE/'source_review/candidate_review.json'),
 ('saved_diagnostic_review',EVIDENCE/'source_review/diagnostics_geography.json'),
 ('geography',EVIDENCE/'geography/geographic_assessment.json'),
 ('study_map',EVIDENCE/'geography/target_and_study_overlap.png'),
 ('source_area_passage',EVIDENCE/'geography/source_area_passage.png'),
 ('original_source_report',MODEL.parents[1]/'sources/ICES_WGSAM_2015.pdf')]:add(role,path)
for f in RESULTS.rglob('*'):
    if f.is_file() and f.suffix!='.png':add('diagnostic_evidence',f)
current=RESULTS/'structural_zero'
if not current.exists():current=RESULTS
for name,filename in [('GE','new_GE.json.gz'),('TE','new_TE_EEfix.json.gz'),('With_Egestion','new_WithEgestion.json.gz')]:
    add(name+'_outcome',current/filename)
artifacts.append({'role':'mapping_decisions','availability':'missing','reason':'No selected-model assignment or allocation is retained for any of the 384 regional catch labels. The appendix records the missing handoff without claiming biological rejection.','acquisition_status':'Not adopted or invented during this validation review; requires a source-grounded mapping stage.'})
index={'schema_version':1,'run_id':'2026-11-14_160000_validation','region_id':'LME_022','model_id':MODEL.name,
 'variant_id':'canonical_Rpath_port_with_explicit_runtime_assumptions',
 'source_identity':{'path':'../../model.json','sha256':hashlib.sha256((MODEL/'model.json').read_bytes()).hexdigest()},
 'computational_input_identity':{'baseline':'../../results/diagnostics/2026-11-14_validation/run_manifest.json','separate_nonfeeding_structural_zero_attempt':os.path.relpath(current,EVIDENCE).replace('\\','/')},
 'methods':['GE','TE','With Egestion'],
 'required_roles':['report','taxon_appendix','source_model','source_departures','mapping_audit','mapping_decisions','comparison','geography','GE_outcome','TE_outcome','With_Egestion_outcome'],
 'artifacts':artifacts,
 'reconciliation':{'appendix_universe_and_arithmetic':True,'protected_inputs_unchanged':True,'scotland_matrix_axes_and_signs_rechecked':True},
 'review_boundary':'Editable review draft. No researcher decision registered. Project, regional selection/results, map and trends unchanged.',
 'scientific_validation_complete':False,
 'remaining_limitations':['Selected-model taxon mapping remains unassessed.','Diagnostic results apply only to their explicitly recorded runtime assumptions and retain all returned restrictions.'],
 'template_note':'Current validation.docx and instructions.md used. The referenced taxon_mapping.xlsx template is absent; its current seven-column specification with a separate Sources sheet was followed.'}
(EVIDENCE/'evidence_index.json').write_text(json.dumps(index,indent=2,ensure_ascii=False),encoding='utf-8')
print('Evidence index written with',len(artifacts),'artifacts; mapping decisions explicitly unavailable.')
