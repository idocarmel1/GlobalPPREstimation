"""Finalize accurate handoff labels and independently verify the saved source cells."""
from pathlib import Path
import csv, hashlib, json, os
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rest=read('import_export_restoration.json');ledger=read('source_cell_ledger.json')
csvpath=ROOT/'regions/LME_024/models/Hernvann_2020_Celtic_Sea_1985/extracted_tables/Diet_composition.csv'
assert sha(csvpath)==rest['after_sha256']
rows=list(csv.reader(csvpath.open(encoding='utf-8-sig',newline='')))
lookup={row[0] or 'import':dict(zip(rows[0][2:],row[2:])) for row in rows[1:] if row[0].isdigit() or row[1]=='Import'}
for e in ledger:
    actual=lookup[e['prey_seq']][str(e['consumer_seq'])]
    assert actual==(e['source_decimal_literal'] or '')
    e['import_csv_before_literal']=e.pop('import_csv_literal')
    e['import_csv_after_literal']=actual
    e['csv_matches_source_after']=True
save('source_cell_ledger.json',ledger)
audit=read('normalization_audit.json')
audit['import_csv_nonmatching_missing_import_cells_before']=audit.pop('import_csv_nonmatching_missing_import_cells')
audit['import_csv_nonmatching_cells_after']=0
audit['import_csv_exact_source_cell_matches_after']=2750
audit['bounded_blank_import_export_restoration_performed']=True
save('normalization_audit.json',audit)
r=read('root_receipt.json')
r['outcome']='verified unnormalized canonical unchanged; bounded import-export blank restoration'
r['changed_diet_cells']=rest['changed_cells']
r['canonical_changed_diet_cells']=[]
r['active_import_csv_before_sha256']=rest['before_sha256']
r['active_import_csv_after_sha256']=rest['after_sha256']
r['precise_blockers']=[]
r['runtime_equivalence_scope']='Complete retained actual loaded calculator/ModelData state identity, unchanged canonical and computational inputs. Current-code replay differs in two engine hashes and is unverified separately.'
r['source_fidelity_limits'].append('Current PPRCalculator.py/ModelData.py hashes differ from historical calculation; current-code replay unverified, no diagnostic rerun. No diet/canonical/runtime-input change occurred.')
r['evidence_paths'].append('regions/LME_024/diet_reextraction_20261002/import_export_restoration.json')
save('root_receipt.json',r)
(P/'AUDIT.md').write_text('# LME_024 diet normalization audit, 2026-10-02\n\nSelected Hernvann_2020_Celtic_Sea_1985 model.json is source-faithful and unnormalized. All 2,750 primary DOCX B2 prey/import cells (tables 2–3, printed pages 14–15) match its exact literals, including unknown versus explicit zero. No source re-extraction or canonical changes were justified. Prior converter normalization had already been restored in the selected canonical; the generated normalized converter JSON is retained historical evidence, not the selected source input.\n\nThe active Diet_composition.csv retained five numeric imports correctly but rendered 45 primary-source blank imports as 0. Under the coordinator’s bounded authorization, only these 45 import-export cells were restored to blanks from the exact existing source/canonical ledger. Every prey cell, five numeric imports, totals/helper rows and unrelated bytes were preserved. After reopening, all 2,750 import-table cells match source decimal literals/blank status. Exact original bytes are archived by SHA256.\n\nThe actual saved calculation uses a separately accepted normalized diet/routing adapter. Its complete retained loaded pickle state including nested loader state compares exactly before/after: 9,962 numeric/tabular elements, maximum difference 0, tolerance absolute 1e-12 and relative 0. Canonical and actual computational inputs/settings were unchanged. This import-only blank-status restoration has no numerical runtime effect and requires no diet-induced scientific refresh. Current shared PPRCalculator.py/ModelData.py hashes differ from historical computation; current-code replay remains separately unverified. Existing results and actual historical hashes are preserved.\n\nThis audit grants no researcher signoff and does not resolve missing native/full-precision evidence, source balance conflicts, existing FAIL or unsupported TE. All 290 protected regional files, including Word/workbooks and canonical model, were verified unchanged; one active import CSV changed as documented. See root_receipt.json, source_cell_ledger.json, import_export_restoration.json and runtime_equivalence.json.\n',encoding='utf8')
paths=[p for p in P.glob('*') if p.is_file() and p.name not in ['evidence_index.json','completeness.json']]
index={'schema_version':1,'run_id':'LME024_diet_normalization_audit_20261002','region_id':'LME_024','model_id':'Hernvann_2020_Celtic_Sea_1985','variant_id':'source_canonical_and_retained_accepted_routing_runtime','source_identity':{'canonical_sha256':r['canonical_after_sha256'],'primary_docx_sha256':ledger[0]['source_sha256']},'computational_input_identity':{'retained_pickle_sha256':read('runtime_equivalence.json')['retained_state_sha256']},'methods':[],'required_roles':['source_cell_ledger','runtime_equivalence','root_receipt','import_export_restoration','protected_verification'],'artifacts':[{'role':p.stem,'path':p.name,'sha256':sha(p),'availability':'present'} for p in paths],'reconciliation':{'canonical_2750_exact_primary_cells':True,'active_import_csv_2750_source_cells_after':True,'only_45_blank_import_cells_changed':len(rest['changed_cells'])==45,'retained_actual_loaded_state_identical':True,'protected_files_unchanged':True}}
for a in read('input_archive_manifest.json'):
    target=ROOT/a['archive_path']; assert sha(target)==a['sha256']
    index['artifacts'].append({'role':'archived_original_input','path':os.path.relpath(target,P).replace('\\','/'),'sha256':a['sha256'],'availability':'present'})
save('evidence_index.json',index)
print(json.dumps({'canonical_sha256':r['canonical_after_sha256'],'restored_blank_import_cells':len(rest['changed_cells']),'csv_before_sha256':rest['before_sha256'],'csv_after_sha256':rest['after_sha256'],'source_and_import_cells_verified':len(ledger)},indent=2))
