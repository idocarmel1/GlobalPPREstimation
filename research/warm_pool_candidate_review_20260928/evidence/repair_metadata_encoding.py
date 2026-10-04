from pathlib import Path
import zipfile, os, xml.etree.ElementTree as ET, json, hashlib
root=Path(__file__).resolve().parents[3]
p=root/'Project.xlsx';tmp=p.with_name('Project_encoding_repair.tmp.xlsx')
with zipfile.ZipFile(p) as z:
    infos=z.infolist();raw={i.filename:z.read(i) for i in infos}
parts=['xl/tables/table2.xml','xl/worksheets/sheet2.xml','xl/tables/table3.xml','xl/worksheets/sheet3.xml']
new={}
for part in parts:
    new[part]=raw[part].replace(b"encoding='utf8'",b"encoding='utf-8'",1)
    ET.fromstring(new[part])
with zipfile.ZipFile(tmp,'w') as z:
    for i in infos:z.writestr(i,new.get(i.filename,raw[i.filename]))
with zipfile.ZipFile(tmp) as z:
    for part in raw:
        assert z.read(part)==new.get(part,raw[part])
os.replace(tmp,p)
print('Repaired and verified metadata XML encoding declarations; all other package bytes unchanged.')
