import json, hashlib, csv
from pathlib import Path
from decimal import Decimal as D
from copy import deepcopy

out=Path(__file__).resolve().parent
region=out.parents[2]
project=region.parents[1]
model=region/'models/28_646_Guinea_(1998)/model.json'
native=region/'papers/GUI-2004/28_646_Guinea_(1998).json'
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((out/'native_diet_ledger.json').read_text(encoding='utf-8'))
assert hashfile(model)==audit['canonical_sha256'],'Concurrent canonical change; stop without adoption'
cells=audit['cells']
exact=[]
for c in audit['per_consumer']:
    selected=[x for x in cells if x['consumer_seq']==c['consumer_seq']]
    total=D(c['printed_total'])
    errors=[abs(D(x['canonical_proportion'])-D(x['source_proportion'])/total) for x in selected]
    c['maximum_error_against_proportional_normalization_of_printed_cells']=str(max(errors))
    c['normalization_classification']='exact source column' if c['different_cells']==0 else 'unresolved native versus printed history; differing column not proportional normalization of printed column'
    c['entire_column_matches_printed_normalization_with_native_float_tolerance']=max(errors)<D('0.0000001')
    if c['different_cells']==0:exact.append(c['consumer_seq'])
    else: assert max(errors)>=D('0.0000001')
a=json.loads(model.read_text(encoding='utf-8')); n=json.loads(native.read_text(encoding='utf-8'))
for g in a['group']:g.pop('taxon_descr',None)
for g in n['group']:g.pop('taxon_descr',None)
assert a==n,'Native numeric equality no longer holds'
arc=out/'original_inputs'/audit['canonical_sha256']
arc.mkdir(parents=True,exist_ok=True)
archived=arc/'model.json'
if archived.exists(): assert hashfile(archived)==audit['canonical_sha256']
else: archived.write_bytes(model.read_bytes())
assert hashfile(archived)==hashfile(model)
ledger_dest=out/'native_diet_ledger.json'
ledger_dest.write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
with (out/'source_Table8_balanced_diet.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f); writer.writerow(['Prey no','Prey name']+[str(c) for c in range(1,43)])
    for p in range(1,46):
        row=[x for x in cells if x['prey_seq']==p]; assert len(row)==42
        writer.writerow([p,row[0]['prey_name']]+[next(x['printed_token'] for x in row if x['consumer_seq']==c) for c in range(1,43)])
diff=[x for x in cells if not x['exact_match']]
imports=[x for x in diff if x['prey_seq']==45]
diag=region/'validation_reports/28_646_Guinea_(1998)/direct_diagnostics/run_provenance.json'
prov=json.loads(diag.read_text(encoding='utf-8'))
protected=[model, region/'LME_028.xlsx',region/'Model_validation_28_646_Guinea_(1998).docx',region/'models/28_646_Guinea_(1998)/sppr_source.xlsx',diag]
result={'date':'2026-10-02','region':'LME_028','selected_model_id':'28_646_Guinea_(1998)',
    'outcome':'blocked: source versus native history unresolved; canonical unchanged',
    'normalization_confirmed':False,'normalization_not_present_proven':False,
    'initial_single_cell_normalization_hypothesis':'withdrawn after complete primary matrix comparison; neither sum=1 nor one-cell ratio proves normalization',
    'canonical_old_sha256':audit['canonical_sha256'],'canonical_new_sha256':hashfile(model),'native_model_sha256':hashfile(native),
    'source_pdf_sha256':audit['source_sha256'],'source_table':'Tableau 8, balanced first line; PDF141-144/printed137-140',
    'source_cell_count':len(cells),'different_cells':len(diff),'exact_source_consumer_sequences':exact,'different_consumer_count':42-len(exact),
    'import_differences':imports,'canonical_equals_native_except_taxonomy_annotations':True,
    'primary_source_evidence':'Local full primary volume recovered and all four diet pages geometry-parsed and visually checked; no missing primary pages.',
    'required_missing_evidence':[
        'Upstream EcoBase high-precision pre-normalization diet/export history identifying how each canonical column was generated.',
        'Cell-specific researcher approval or correction ledger for native-versus-printed revisions, especially Disques seq21 and import seq27.'
    ],
    'explicit_researcher_corrections_found':[],'researcher_review_status':'pending; no researcher signoff granted',
    'runtime_normalization':'Allowed by latest human steering; source fidelity/rounding review remains an evidence/trust status. No runtime or SPPR run performed.',
    'transformations':{'source_to_audit_table':'orientation transform and token positioning only; balanced first line retained; italic earlier diets excluded; dashes/blanks distinguished',
                       'source_to_canonical':'none; adoption blocked by unproven native history','runtime_new_transformations':'none'},
    'historical_diagnostics':{'stale_due_to_this_audit':False,'reason':'canonical input identity unchanged; retained historical raw/runtime normalization provenance preserved',
                             'input_hash_record':str(diag.relative_to(project)).replace('\\','/'),'prior_normalization_review_is_researcher_approval':False},
    'extracted_import_tables':'No retained regional extraction/import table exists. Source-only diet/import CSV written in audit evidence; not adopted as canonical extracted_tables.',
    'protected_file_sha256':{str(p.relative_to(project)).replace('\\','/'):hashfile(p) for p in protected},
    'original_input_archive':str(archived.relative_to(project)).replace('\\','/'),
    'writes':'Only separate diet_reextraction_20261002 audit evidence and exact original model archive; no canonical/Office/workbook/diagnostics/map writes'}
(out/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
assert hashfile(model)==audit['canonical_sha256']
print(json.dumps({k:result[k] for k in ['outcome','canonical_old_sha256','source_cell_count','different_cells','exact_source_consumer_sequences','import_differences']},indent=2,ensure_ascii=False))
