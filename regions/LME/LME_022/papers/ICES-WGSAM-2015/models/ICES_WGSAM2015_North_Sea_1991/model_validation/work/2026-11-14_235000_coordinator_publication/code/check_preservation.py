from pathlib import Path
import importlib.util,json,sys
run=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('ices_driver_audit',run/'code/publish_ices.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
pins=m.read(run/'inputs/package_pin.json');assert m.sha(m.WRAPPER)==pins['wrapper_sha256'];assert m.sha(m.PACKAGE/'preparation.json')==pins['preparation_sha256']
plan=m.read(m.PACKAGE/'preparation.json');assert plan['ready_for_apply']
original=m.read_book(m.REGION);staged=m.read_book(m.PACKAGE/'regional/LME_022.xlsx')
actual=m.independent_inputs(original);expected=m.independent_inputs(staged)
diff=[]
for sheet in set(original)|set(staged):
    for name in set(original.get(sheet,{}))|set(staged.get(sheet,{})):
        if original.get(sheet,{}).get(name)!=staged.get(sheet,{}).get(name):diff.append([sheet,name])
qa={'package_pins_verified':True,'independent_digest_before':actual,'independent_digest_staged':expected,'independent_tables_equal':actual==expected,'old_table_counts':m.table_counts(original),'staged_table_counts':m.table_counts(staged),'staged_mapping_identity':m.mapping_identity(staged),'changed_tables':diff,'Project_or_pages_read':False,'shared_writes':False,'driver_executed':False,'script_sha256':m.sha(m.SCRIPT)}
print(json.dumps(qa,indent=2));m.write(run/'qa/preservation_check.json',qa)
assert actual==expected,'Unexpected independent/manual table differences'
identities=m.review_group_sequences(m.records(staged,'Selected model groups','Groups'));assert [identities[n] for n in m.NAMES]==m.EXCLUDED;assert len(identities)==70
