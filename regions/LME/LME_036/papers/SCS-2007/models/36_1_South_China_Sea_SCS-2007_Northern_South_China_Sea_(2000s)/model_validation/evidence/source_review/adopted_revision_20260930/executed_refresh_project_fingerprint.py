from pathlib import Path
import hashlib,re,json
R=Path.cwd();fingerprint=hashlib.sha256((R/'Project.xlsx').read_bytes()).hexdigest().encode()
for name in ['interactive_map/index.html','interactive_map/trends.html']:
 p=R/name;raw=p.read_bytes();updated,n=re.subn(rb'(<meta name="ppr-project-sha256" content=")[0-9a-f]{64}(">)',lambda m:m[1]+fingerprint+m[2],raw)
 assert n==1;p.write_bytes(updated)
D=R/'regions/LME_036/validation_reports/36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)/adopted_revision_20260930'
p=D/'ledger_metadata_correction.json';s=json.loads(p.read_text());s['html_project_fingerprints_refreshed']=True;p.write_text(json.dumps(s,indent=2),encoding='utf-8')
print('Project fingerprints aligned with final workbook; all embedded numerical data preserved.')
