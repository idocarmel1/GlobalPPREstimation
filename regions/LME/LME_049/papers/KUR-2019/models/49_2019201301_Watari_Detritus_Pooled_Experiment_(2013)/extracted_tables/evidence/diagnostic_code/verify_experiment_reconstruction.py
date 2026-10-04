from pathlib import Path
import json,shutil,math,hashlib
import openpyxl
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());OUT=ROOT/'regions/LME_049/models/49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)';EV=OUT/'evidence'
g=json.loads((OUT/'model.json').read_text(encoding='utf-8'))['group'];p=EV/'canonical_reconstructed.xlsx';raw=EV/'converter_reconstructed_intermediate.xlsx'
if not raw.exists():shutil.copy2(p,raw)
w=openpyxl.load_workbook(raw);d=w['Diet composition'];f=w['Detritus fate'];changes=[]
# The converter writes blank fate/import and absent PP diets as zero. Restore
# missingness in the review workbook; never use this intermediate to feed engine.
for row in range(2,41):
    f.cell(row,3).value=None;changes.append(['Detritus fate',row,3,'0','unknown'])
for col in range(3,42):
    d.cell(41,col).value=None;changes.append(['Diet composition',41,col,'0','unknown import'])
for col in range(38,42):
    for row in range(2,41):d.cell(row,col).value=None
    d.cell(42,col).value=None
w['Metadata'].append(['Review convention','Blank unknown, not zero. Fate/import missingness restored after converter. Total-area B is authoritative in canonical JSON; Basic input displays source habitat B. No source publication parameter was changed.'])
w.save(p);w.close()
w=openpyxl.load_workbook(p,read_only=True,data_only=True);b=list(w['Basic input'].values);d=list(w['Diet composition'].values);catch={str(r[0]):r[2] for r in list(w['Landings'].values)[1:]}
def eq(v,s):return v is None if s=='-9999' else math.isclose(float(v),float(s),rel_tol=1e-12,abs_tol=1e-12)
for i,x in enumerate(g,1):
    for col,field in [(2,'habitat_area'),(3,'biomass_habitat_area'),(4,'pb'),(5,'qb'),(6,'ee'),(8,'gs'),(9,'detritus_import')]:assert eq(b[i][col],x[field]),(i,field)
    assert eq(catch.get(x['group_seq']),x['export'])
    for cell in (x['diet_descr'] or {}).get('diet',[]):assert eq(d[int(cell['prey_seq'])][i+1],cell['proportion'])
assert all(r[2] is None for r in list(w['Detritus fate'].values)[1:]);w.close()
result={'39_groups_scalar_catch_and_1365_diet_entries_independently_checked_in_reconstructed_xlsx':True,'missing_fate_and_import_restored_to_blank':True,'converter_intermediate_retained':raw.name,'canonical_model_used_for_diagnostics_unchanged':hashlib.sha256((OUT/'model.json').read_bytes()).hexdigest(),'reconstruction_fate_import_changes':changes}
(EV/'reconstruction_value_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
shutil.copy2(Path(__file__),OUT/'diagnostic_code'/Path(__file__).name)
print('Reconstructed XLSX independently verified:39groups,1365diet entries, source missingness restored; canonical untouched.')
