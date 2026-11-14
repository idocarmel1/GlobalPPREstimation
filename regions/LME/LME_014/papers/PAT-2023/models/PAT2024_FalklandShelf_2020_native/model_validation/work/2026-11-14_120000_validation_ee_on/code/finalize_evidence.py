import hashlib,json,os,shutil,sys
from pathlib import Path
RUN=Path(__file__).resolve().parents[1];VAL=RUN.parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
EV=VAL/'evidence';FLOOR=EV/'ee_floor_on_review'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=read(RUN/'qa/report_verification.json')
checks['visual_review']={'renderer':'isolated hidden Word; read-only output export, no save to source','page_count':10,'inspected_pages':list(range(1,11)),'result':'Readable pages; no clipping, overlaps, unintended blank pages or stranded figure headings. Flowing table continuation and repeated headers retained.','render_pdf_sha256':sha(RUN/'qa/validation_verified.pdf'),'rendered_page_sha256':{str(i):sha(RUN/f'qa/verified-page-{i}.png') for i in range(1,11)},'appendix':'Artifact-tool rendered top, middle, zero-catch and Sources views inspected; filters/panes/links also checked structurally.'}
checks['cleanup']={'scope':RUN.relative_to(ROOT).as_posix(),'reason':'Remove task-generated temporary Office copies, input alias, renders, builders and dependency junction after promoting current verification and exact diagnostic execution evidence. Original sources and all historical reviewed science remain unchanged.','retained_diagnostic_execution_code':'ee_floor_on_review/execution/run_floor_review.py'}
write(EV/'report_checks.json',checks)
mapping=read(RUN/'qa/mapping_validation_summary.json')
mapping['source_rows']=mapping['source_rows'].replace('\\','/')
write(EV/'mapping_review.json',mapping)
shutil.copy2(RUN/'artifact.md',EV/'report_production_contract.md')
for name in ['protected_verification.json','matrix_accounting_verification.json']:
    shutil.copy2(RUN/'qa'/name,FLOOR/name)
(FLOOR/'execution').mkdir(exist_ok=True)
for name in ['run_floor_review.py','verify_floor_review.py']:
    shutil.copy2(RUN/'code'/name,FLOOR/'execution'/name)
provenance=read(FLOOR/'run_provenance.json')
provenance['script']['original_execution_location']=provenance['script']['path']
provenance['script']['path']='execution/run_floor_review.py'
provenance['script']['retention_note']='Exact code bytes retained as execution evidence; originally run from the recorded task work directory, not an installed workflow runner.'
assert provenance['script']['sha256']==sha(FLOOR/'execution/run_floor_review.py')
write(FLOOR/'run_provenance.json',provenance)
index=read(FLOOR/'evidence_index.json')
for a in index['artifacts']:
    if a['role']=='protected-inputs':a['path']='protected_verification.json'
    if a['role']=='matrix-accounting-verification':a['path']='matrix_accounting_verification.json'
    if a['availability']=='present':a['sha256']=sha(FLOOR/a['path'])
index['artifacts'].append({'role':'execution-code','path':'execution/run_floor_review.py','sha256':sha(FLOOR/'execution/run_floor_review.py'),'availability':'present'})
write(FLOOR/'evidence_index.json',index)

roles={
'validation-report':VAL/'validation.docx','mapping-appendix':VAL/'taxon_mapping.xlsx',
'canonical-model':VAL.parent/'model.json','source-departures':VAL.parent/'model_notes.md',
'report-verification':EV/'report_checks.json','mapping-review':EV/'mapping_review.json',
'adopted-mapping-evidence':EV/'source_review/taxon_audit.json',
'allocation-evidence':EV/'source_review/allocation_evidence.json',
'source-review':EV/'source_review/source_review.md',
'geography-assessment':EV/'source_review/geography/geographic_assessment.json',
'target-figure':EV/'source_review/geography/target_region.png',
'study-figure':EV/'source_review/geography/source_figure1.png',
'ee-floor-diagnostic-index':FLOOR/'evidence_index.json',
'ee-floor-full-returns':FLOOR/'direct_diagnostics_full.json',
'ee-floor-accounting':FLOOR/'initialization_and_floor.json',
'current-template':ROOT/'tools/templates/validation.docx'}
root_index={'schema_version':1,'run_id':RUN.name,'region_id':'LME_014','model_id':'PAT2024_FalklandShelf_2020_native',
'variant_id':'selected-model-report-ee-floor-on-0.1','source_identity':{'canonical_model_sha256':sha(VAL.parent/'model.json')},
'computational_input_identity':{'canonical_model_sha256':sha(VAL.parent/'model.json'),'use_ee_floor':True,'ee_floor':0.1,'audited_initialization_verified':True},
'methods':['GE','TE'],'required_roles':list(roles),
'artifacts':[{'role':role,'path':os.path.relpath(p,EV).replace('\\','/'),'sha256':sha(p),'availability':'present'} for role,p in roles.items()],
'reconciliation':{'manual_rows_preserved':True,'all_250_taxa_reconciled':True,'all_196_very_low_taxa_named_once':True,'classic_denominators_reconciled':True,'protected_inputs_unchanged':True,'all_pages_inspected':True},
'limits':['Review artifacts remain unsigned; no researcher decision registered.','GE and TE remain WARN for the negative Discards stock residual despite strict balance passing.','Geographic overlap is conditional reported-area approximation; exact study polygon and distinct Article selection rationale are unavailable.','Mapping is verified reused adopted evidence, not a fresh remapping. No regional coefficient/result adoption, Project.xlsx update or map/trends refresh.'],
'related_prior_evidence':'source_review/evidence_index.json'}
write(EV/'evidence_index.json',root_index)
print('Promoted current review evidence and refreshed portable indexes')
