import sys,json,pathlib,hashlib,re,collections
sys.path.insert(0,'original_research_archive/research/regional_ge_integration_20260928')
from xml_audit_reader import read_book
out=pathlib.Path('original_research_archive/research/size_allocation_20260929/lme_east')
for num in [52]:
 u=f'LME_{num:03}'; p=pathlib.Path('regions')/u/f'{u}.xlsx'; b=read_book(p)
 def rows(s,t):
  h,d=b[s][t];return [dict(zip(h,r)) for r in d]
 settings={r['field']:r['value'] for r in rows('Overview','Settings')}
 g=rows('Selected model groups','Groups');m=rows('PPR','Matching')
 data={'unit_id':u,'settings':settings,'workbook_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'groups':g,'matching':m,'sppr':rows('Selected model groups','Group SPPR')}
 (out/f'{u}_audit.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 print(u,settings['selected_model_id'],settings.get('model_path'))
 print('GROUPS',[(x.get('seq'),x['group_name'],x['catch']) for x in g])
 print('SIZE MAPPINGS', [x for x in m if re.search(r'size|juven|adult|stage|small|large|pollock|croaker',str(x),re.I)])
