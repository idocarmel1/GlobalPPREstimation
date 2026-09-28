"""Remove only the empty duplicate row created when appending after a spacer."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,os,json,hashlib,shutil
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());OUT=Path(__file__).parent;p=ROOT/'Project.xlsx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(p);assert before=='63a0e38fa83c2e0a0e1cd21a8c896b959f2f5b5a7b338e858c915d0425888c54'
backup=OUT/'Project_before_empty_spacer_removal.xlsx';shutil.copy2(p,backup)
with zipfile.ZipFile(p) as z:infos=z.infolist();raw={i.filename:z.read(i) for i in infos}
n='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}';E.register_namespace('',n[1:-1]);E.register_namespace('r','http://schemas.openxmlformats.org/officeDocument/2006/relationships')
part='xl/worksheets/sheet3.xml';x=E.fromstring(raw[part]);sd=x.find(n+'sheetData');dups=[r for r in sd if r.get('r')=='42'];assert len(dups)==2
blank=[r for r in dups if not ''.join(r.itertext())];assert len(blank)==1;sd.remove(blank[0]);assert len({r.get('r') for r in sd})==len(sd)
changed=E.tostring(x,encoding='utf-8');tmp=OUT/'Project_spacer_fix.xlsx'
with zipfile.ZipFile(tmp,'w') as z:
    for i in infos:z.writestr(i,changed if i.filename==part else raw[i.filename])
with zipfile.ZipFile(tmp) as z:
    for k,v in raw.items():
        if k!=part:assert z.read(k)==v
assert sha(p)==before;os.replace(tmp,p)
(OUT/'SPACER_REPAIR_VERIFICATION.json').write_text(json.dumps({'before_sha256':before,'after_sha256':sha(p),'only_changed_part':part,'removed_row':42,'removed_row_contained_no_values':True,'all_other_package_parts_byte_identical':True,'backup':str(backup.relative_to(ROOT))},indent=2),encoding='utf-8')
print('Removed exactly one empty duplicate row42; registered model data retained.')
