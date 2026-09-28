"""Proposal-only audit of every binomial in source Table S3; no workbook writes."""
from pathlib import Path
import concurrent.futures,json,re,requests,hashlib
from urllib.parse import quote
import pandas as pd
P=Path(__file__).resolve().parent;M=P.parent.parent;D=M/'50_502013_Coastal_Kyoto_Inoue_(2013)';E=P/'primary_taxonomy';E.mkdir(exist_ok=True)
groups=json.loads((D/'model.json').read_text(encoding='utf8'))['group']
names=[]
for g in groups:
 for n in g['taxon_descr'].split(';')[0].split(','):
  n=n.strip()
  if re.fullmatch(r'[A-Z][a-z]+ [A-Za-z]+',n):names.append({'source_name':n,'group':g['group_name'],'source_seq':int(g['group_seq'])})
def get(x):
 url='https://www.marinespecies.org/rest/AphiaRecordsByName/'+quote(x['source_name'],safe='')+'?like=false&marine_only=true'
 try:
  r=requests.get(url,timeout=30);dest=E/(x['source_name'].replace(' ','_')+'.json');dest.write_bytes(r.content)
  data=r.json() if r.status_code==200 else [];data=data if isinstance(data,list) else []
  return x|{'url':url,'http_status':r.status_code,'sha256':hashlib.sha256(r.content).hexdigest(),'records':data}
 except Exception as ex:return x|{'url':url,'error':str(ex),'records':[]}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(get,names))
(P/'source_name_taxonomy_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
catch=pd.read_csv(D/'selected_pipeline/all_taxa_membership_review.csv');unmapped=set(catch.loc[catch.group.isna(),'taxon']);new=[]
for x in out:
 for r in x['records']:
  if r.get('valid_name') in unmapped:new.append({'source_name':x['source_name'],'group':x['group'],'candidate_catch_name':r['valid_name'],'status':r.get('status'),'AphiaID':r.get('AphiaID'),'valid_AphiaID':r.get('valid_AphiaID')})
print(json.dumps({'source_binomials_queried':len(names),'no_exact_taxonomy_record':[x['source_name'] for x in out if not x['records']],'potential_new_accepted_name_matches':new},indent=2))
