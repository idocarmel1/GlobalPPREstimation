"""Preserve source evidence and create repository round-trip without changing candidates."""
from extract_candidates import *
from database_json import EwEConverter
for folder in ['22_20251890_East_Coast_of_Scotland_(1890-1895)','22_20251990_East_Coast_of_Scotland_(1991-1995)','22_20071991_North_Sea_report_Table_3.3_(1991)']:
    et=REG/'models'/folder/'extracted_tables';ev=et/'source_evidence';ev.mkdir(exist_ok=True)
    names=(['saygu_table1_cells.json','pdf-aa2228c7_page_6_220dpi.png'] if folder.startswith('22_2025') else ['mackinson_diet_cells.json','mackinson_table3_3_cells.json','mackinson_table3_5_tonnes.json','mackinson_table11_8_members.csv','mackinson_tables14_7_14_8_coordinates.json','tech142-ead77c0e_page_30_220dpi.png','tech142-ead77c0e_page_34_220dpi.png'])
    for name in names:shutil.copy2(OUT/name,ev/name)
    shutil.copy2(REG/'models'/folder/'source_provenance.json',ev/'source_provenance.json')
dest=REG/'models/457_457_North_Sea_(1991)';rr=dest/'repository_roundtrip';rr.mkdir(exist_ok=True)
out=rr/'457_457_North_Sea_(1991).json';shutil.copy2(dest/'model.json',out)
c=EwEConverter(str(rr/'conversion.log'));d=json.loads(out.read_text(encoding='utf-8'))
c.report_mass_balance(c.check_mass_balance(d['group'],0),out.stem,str(rr/'MASS_BALANCE.md'));c.json_to_excel(str(out))
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['NS-2025','LME022-Mackinson-2007'] for p in (REG/'papers'/folder).iterdir() if p.is_file()}
dump(OUT/'source_hashes.json',hashes)
print('Source evidence copied; repository round trip and source hash manifest retained.')
