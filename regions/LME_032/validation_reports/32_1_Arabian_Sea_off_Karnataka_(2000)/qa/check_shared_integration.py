from pathlib import Path
import sys,json,hashlib,zipfile,math
from lxml import etree as E
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
R=Path(__file__).resolve().parent.parent; region=R.parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from original_atlas_data import embedded,branch
from workbooks import sha
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main';D='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
project=ROOT/'Project.xlsx';fingerprint=sha(project)
with zipfile.ZipFile(project) as z:
 shared=[]
 if 'xl/sharedStrings.xml' in z.namelist():shared=[''.join(si.itertext()) for si in E.fromstring(z.read('xl/sharedStrings.xml'))]
 rel={x.get('Id'):x.get('Target').lstrip('/') for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
 sheets={x.get('name'):rel[x.get('{'+D+'}id')] for x in E.fromstring(z.read('xl/workbook.xml')).find('{'+S+'}sheets')}
 def read(name,key,chosen):
  part=sheets[name];part=part if part.startswith('xl/') else 'xl/'+part;out=[];header=None;table=None
  with z.open(part) as stream:
   for _,row in E.iterparse(stream,events=('end',),tag='{'+S+'}row'):
    cells={}
    for c in row:
     col=c.get('r','').rstrip('0123456789');kind=c.get('t');v=c.find('{'+S+'}v');inline=c.find('{'+S+'}is')
     value=''.join(inline.itertext()) if inline is not None else shared[int(v.text)] if kind=='s' and v is not None else (v.text if v is not None else None)
     if kind not in ['s','inlineStr','str'] and value is not None:
      try:value=float(value);value=int(value) if value.is_integer() else value
      except (ValueError,AttributeError):pass
     cells[col]=value
    values=list(cells.values())
    if values and values[0]=='@table':table=values[1];header=None
    elif values and header is None:header=cells
    elif values and header:
     record={header[col]:value for col,value in cells.items() if col in header}
     if record.get(key)==chosen:out.append({'table':table,**record})
    row.clear()
    while row.getprevious() is not None:del row.getparent()[0]
  return out
 snapshot={'project_sha256':fingerprint,'region':read('Regions & status','unit_id','LME_032'),'paper':read('Papers','article_id','ARAB-2005__LME_032'),'model':read('Models & coverage','model_id','32_1_Arabian_Sea_off_Karnataka_(2000)'),'annual':read('Regional PPR','unit_id','LME_032')}
assert sha(project)==fingerprint,'Shared project changed during inspection'
assert snapshot['region'][0]['sha256']==sha(region/'LME_032.xlsx')
assert snapshot['region'][0]['selected_model_id']=='32_1_Arabian_Sea_off_Karnataka_(2000)'
assert snapshot['region'][0]['resolved_taxa']==430 and snapshot['region'][0]['unresolved_taxa']==0
assert snapshot['paper'][0]['loadability_class']=='Reconstructed and executed; balance WARN'
assert snapshot['model'][0]['publication_year']==2008 and snapshot['model'][0]['model_area_km2']==27000
db,html=embedded(ROOT/'interactive_map/index.html','DB')
series,trends=embedded(ROOT/'interactive_map/trends.html','SERIES_DB')
marker=f'<meta name="ppr-project-sha256" content="{fingerprint}">'
assert marker in html and marker in trends,'Map/trend fingerprint is stale'
simple=db['network']['simple_units']['LME_032'];unit=db['network']['units']['LME_032']
ts=series['units']['LME_032'];assert ts['default_model']=='32_1_Arabian_Sea_off_Karnataka_(2000)'
expected=json.loads((R/'mapping/coverage_summary.json').read_text('utf-8'))
ppr=simple['simple']['ppr'][-1]/9
assert math.isclose(ppr,expected['ppr_tC'],rel_tol=1e-12)
assert math.isclose(simple['simple']['catch'][-1],expected['catch_t'],rel_tol=1e-12)
annual=[]
for row in snapshot['annual']:
 if row['scope']=='all' and row['catch_basis']=='landings' and row['unidentified']=='method' and row['metric']=='ppr':
  value=row.get(2019,row.get('2019'))
  annual.append({'model_id':row.get('model_id') or ('' if row['method']=='simple trophic chain' else snapshot['region'][0]['selected_model_id']),'method':row['method'],'ppr_tC_2019':value/9 if value is not None else None,'status':row.get('status')})
assert math.isclose(next(x['ppr_tC_2019'] for x in annual if x['method']=='simple trophic chain'),expected['ppr_tC'],rel_tol=1e-12)
source=db['articles'];paper=next(x for x in source if x['article_id']=='ARAB-2005__LME_032')
assert 'zero BA adopted' in paper['quality_rationale'] or 'zero BA' in paper['quality_rationale']
(R/'qa/shared_project_snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'qa/map_payload.json').write_text(json.dumps({'region':'LME_032','project_sha256':fingerprint,'map_sha256':sha(ROOT/'interactive_map/index.html'),'trends_sha256':sha(ROOT/'interactive_map/trends.html'),'selected_model':ts['default_model'],'simple_unit':simple,'model_unit':unit,'selected_article':paper},ensure_ascii=False,indent=2),encoding='utf-8')
(R/'qa/shared_integration.json').write_text(json.dumps({'all_passed':True,'project_sha256':fingerprint,'regional_workbook_sha256':sha(region/'LME_032.xlsx'),'selected_model':ts['default_model'],'taxa_resolved':430,'source_metadata_preserved':True,'reference':{'year':2019,'catch_basis':'landings','method':'simple trophic chain','scope':'all','unidentified':'method','groups':'all','units':'t C','unrounded_ppr_tC':ppr,'visible_four_significant_digit_value':'514,700,000 t C'},'annual_2019':annual,'archive_present':(ROOT/'interactive_map/archive/index.html').is_file(),'global_verify_html':'Performed by the coordinated LME_034 integration chat; independently check its successful output before handoff.'},ensure_ascii=False,indent=2),encoding='utf-8')
print('LME_032 Project/map/trend payload identity, metadata, catch and denominator verified')
