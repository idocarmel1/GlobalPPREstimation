"""Independent adversarial tests. Never edits the installed skill or real models."""
from pathlib import Path
import json,csv,sys,subprocess,copy,hashlib,traceback,importlib.util,os
from decimal import Decimal
import openpyxl
from unittest.mock import patch
P=Path(__file__).resolve().parent
SK=Path('C:/Users/idoca/.agents/skills/ecopath-extraction')
PY=Path(sys.executable)
sys.path.insert(0,str(SK/'scripts'))
import source_fidelity as sf

BASE={
 'metadata':{'LME':'27 Canary Current','model_number':999,'model_name':'Independent adversarial fixture','model_year':1991},
 'groups':[
  {'n':1,'name':'Fish A','hab_area':'0.5','biomass':'10.00','z':'0.20','pb':'0.20','qb':'2.00','ee':'0.500','pq':'0.100','unassim':'0.20','ba':'2.00','tl':'3.20','parameter_roles':{'biomass':'model_estimated','pb':'published_input','qb':'published_input','pq':'derived'}},
  {'n':2,'name':'Fish B','hab_area':'1','biomass':'0','z':None,'pb':'0','qb':'0','ee':None,'ba':'-2.50','tl':None},
  {'n':3,'name':'Producer','hab_area':None,'biomass':'7.00','pb':'9.00','ba':'3.00','tl':'1.00'},
  {'n':4,'name':'Det A','hab_area':'1','biomass':'1','ba':'0','tl':'1.00'},
  {'n':5,'name':'Det B','hab_area':'1','biomass':None,'ba_rate':'-0.0100','tl':None}
 ],
 'consumers':[1,2],'diet_rows':5,'fleets':['Fleet A','Fleet B'],
 'landings':{'1':{'Fleet A':'1.20','Fleet B':'0.30'},'2':{'Fleet A':'0','Fleet B':None},'3':{'Fleet A':'0','Fleet B':'0'}},
 'discards':{'1':{'Fleet A':'0.20','Fleet B':'0'},'2':{'Fleet A':'0','Fleet B':'0'},'3':{'Fleet A':'0','Fleet B':'0'}},
 'detritus_groups':['Det A','Det B'],
 'detritus_fate':{'1':{'Det A':'0.2000','Det B':None,'Export':None},'2':{'Det A':'0.40','Det B':'0.40','Export':'0.10'},'3':{'Det A':'0','Det B':'0','Export':'0'}},
 'diet':{'1':{'1':'0','2':None,'3':'0.3000','4':'0.5000','5':'0','import':'0.1000'},'2':{'1':'0','2':'0','3':'0.200','4':'0.300','5':'0.400','import':'0.0100'}},
 'stanzas':[{'stock':'A','juvenile':2,'adult':1,'transition_months':'12','vbk':'0.01000'}],
 'extraction_notes':['All fields synthetic; not scientific source data.'],
 'companions':{
  'Source_fields.csv':{'description':'Quoted source fields; units and locators retained','rows':[['field','literal','units','source','status'],['growth','0.01000','yr-1','p.2, "Table A"','published'],['formula-like','=SUM(A1:A2)','literal','line\nbreak','published'],['unicode','é דג','text','Source','published'],['unknown',None,'unknown','Source','unknown'],['zero','0','unit','Source','published']]},
  'Source_stanzas.csv':{'description':'Published stanza metadata','rows':[['stock','juvenile','adult','months'],['A','2','1','12']]},
  'Source_grid.csv':{'description':'Verbatim source grid with merged headers','layout':'source_grid','rows':[['','Merged','Merged'],['ID','Value'],['1','0.0500',''],['2',None,'note']]}
 }
}
results=[]
def record(name,fn):
 try:detail=fn();results.append({'name':name,'passed':True,'detail':detail})
 except Exception as exc:results.append({'name':name,'passed':False,'error':str(exc),'traceback':traceback.format_exc()})
def run(cmd,log):
 r=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=60)
 (P/log).write_text(r.stdout+'\nSTDERR\n'+r.stderr,encoding='utf8')
 assert r.returncode==0,(r.returncode,r.stderr[-1600:])
 return r
def setup(name,model=None,convert=True):
 model=copy.deepcopy(BASE if model is None else model);inp=P/(name+'.json');inp.write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf8')
 run([PY,SK/'scripts/write_outputs.py',inp,'--outdir',P,'--dir-name',name],name+'_write.log')
 out=P/name
 if convert:run([PY,SK/'scripts/database_json.py','-d',out],name+'_convert.log')
 return out
def converted(out):
 for f in out.glob('*.json'):
  d=json.loads(f.read_text(encoding='utf8'))
  if 'group' in d:return d
 raise AssertionError('No converted database JSON')
def groups(d):return {str(g['group_seq']):g for g in d['group']}
def val(x):return Decimal(str(x))
def csvrows(p):
 with p.open(encoding='utf8',newline='') as f:return list(csv.reader(f))
OUT=setup('core')
DATA=converted(OUT);GS=groups(DATA)
def standard_schema():
 expected={
 'Basic_input.csv':',Group name,Hab area (proportion),Biomass in habitat area (t/km^2),Total mortality (/year),Production / biomass (/year),Consumption / biomass (/year),Ecotrophic Efficiency,Other mortality,Production / consumption,Unassim. consumption,Detritus import (t/km^2/year)',
 'Diet_composition.csv':',Source / fate,1,2',
 'Landings.csv':',Group name,Fleet A,Fleet B,Total',
 'Discards.csv':',Group name,Fleet A,Fleet B,Total',
 'Detritus_fate.csv':',Source / fate,Det A,Det B,Export,Sum',
 'Biomass_accumulation.csv':',Group name,Biomass accumulation (t/km^2/year),Biomass accumulation rate (/year)'}
 for n,h in expected.items():
  b=(OUT/n).read_bytes();assert b.split(b'\r\n')[0]==h.encode();assert b.endswith(b'\r\n') and b'"' not in b and not b.startswith(b'\xef\xbb\xbf')
  assert b.count(b'\n')==b.count(b'\r\n')
 for n in ['Basic_input.csv','Biomass_accumulation.csv']:
  assert (OUT/n).read_bytes().split(b'\r\n')[0]==(SK/'assets/templates'/('T'+n)).read_bytes().split(b'\r\n')[0]
 assert csvrows(OUT/'Basic_input.csv')[1][3]=='10.00'
 assert csvrows(OUT/'Biomass_accumulation.csv')[2][2]=='-2.50'
 wb=openpyxl.load_workbook(OUT/'TL.xlsx');assert wb.active['A1'].value is None and wb.active['B1'].value is None and wb.active['C1'].value=='TL';wb.close()
 wb=openpyxl.load_workbook(OUT/'Metadata.xlsx');assert [wb.active.cell(i,1).value for i in range(1,5)]==['LME','model_number','model_name','model_year'];wb.close()
 return 'Six CSV schemas exact with CRLF/no BOM/no quotes; two native workbook schemas verified.'
record('standard_import_schemas_and_literals',standard_schema)
def scalars():
 g=GS['1'];assert val(g['biomass'])==5 and val(g['biomass_accum'])==1
 assert g['biomass_habitat_area']=='10.00' and g['biomass_accum_source_literal']=='2.00'
 assert val(GS['2']['biomass'])==0 and val(GS['2']['biomass_accum'])==Decimal('-2.50')
 assert GS['2']['ee']=='-9999' and GS['3']['biomass']=='-9999' and GS['3']['biomass_accum']=='-9999'
 assert GS['4']['biomass_accum']=='0' and GS['5']['biomass_accum']=='-9999' and GS['5']['biomass_accum_rate']=='-0.0100'
 return 'h=.5 transforms B10/BA2 to B5/BA1; zero/negative/unknown and rate-only BA retained.'
record('zero_unknown_negative_BA_and_habitat_scaling',scalars)
def exports():
 assert val(GS['1']['landings_total'])==Decimal('1.5') and val(GS['1']['discards_total'])==Decimal('.2')
 assert val(GS['1']['export'])==Decimal('1.7') and val(GS['1']['total_removals'])==Decimal('1.7')
 assert GS['2']['landings_total']=='-9999' and GS['2']['landings_known_subtotal']=='0' and GS['2']['export']=='-9999'
 assert GS['2']['landings_by_fleet']['Fleet B']=='-9999' and GS['3']['export']=='0'
 return 'Known landings+discards included; incomplete fleet total remains unknown despite zero subtotal.'
record('known_landings_discards_and_partial_totals',exports)
def input_flags():
 assert GS['1']['b_hab_area_input']=='false' and GS['1']['ge_input']=='false' and GS['1']['pb_input']=='true'
 assert GS['2']['ee_input']=='false' and GS['1']['parameter_source_roles']['biomass']=='model_estimated'
 return 'Published model-estimated/derived role differs from importer-known input.'
record('author_parameter_roles',input_flags)
def dietfate():
 g=GS['1'];assert g['detritus_fate_by_pool']=={'4':'0.2000','5':'-9999'} and g['detritus_export']=='-9999'
 diet={x['prey_seq']:x['proportion'] for x in g['diet_descr']['diet']};assert diet['2']=='-9999' and diet['3']=='0.3000'
 assert g['diet_imp']=='0.1000'
 assert GS['2']['detritus_fate_by_pool']=={'4':'0.40','5':'0.40'} and GS['2']['detritus_export']=='0.10'
 sums={x['consumer_seq']:x for x in DATA['source_fidelity']['diet_sums']}
 assert sums['1']['diet_plus_import_sum'] is None and val(sums['2']['diet_plus_import_sum'])==Decimal('.91')
 assert DATA['source_fidelity']['normalization_applied'] is False
 return 'Partial routing/unknown diet cells and a complete .91 diet remain unnormalized.'
record('partial_detritus_and_diet_no_normalization',dietfate)
def companions():
 c=DATA['published_companions'];assert len(c)==3
 expected=[[str(x) if x is not None else '' for x in row] for row in BASE['companions']['Source_fields.csv']['rows']]
 assert c['Source_fields.csv']['rows']==expected
 assert DATA['stanzas']==BASE['stanzas'] and DATA['extraction_notes']==BASE['extraction_notes']
 assert b'"p.2, ""Table A"""' in (OUT/'companions/Source_fields.csv').read_bytes()
 assert c['Source_grid.csv']['rows'][1]==['ID','Value','']
 return 'Quoted/newline/Unicode/formula-like/decimal literals and padded source grids retained.'
record('companions_literals_schema_and_extended_fields',companions)
def reconstructed():
 check=json.loads((OUT/'SOURCE_FIDELITY_CHECK.json').read_text());assert check['numeric_value_and_missing_mask_match']
 files=[f for f in OUT.glob('*.xlsx') if f.name not in ['TL.xlsx','Metadata.xlsx']];assert len(files)==1,files
 wb=openpyxl.load_workbook(files[0]);s=wb['Basic_input'];assert s['D2'].data_type=='n' and s['D2'].value==10 and s['E3'].value is None
 assert wb['Biomass_accumulation']['C3'].value==-2.5 and wb['Biomass_accumulation']['C6'].value is None
 assert wb['Diet_composition']['C3'].value is None and wb['Diet_composition']['C2'].value==0
 sheets=[x for x in wb.sheetnames if x.startswith('Source_') and x!='Source_manifest']
 x=next(wb[s] for s in sheets if wb[s]['A2'].value=='growth');assert x['B2'].value=='0.01000' and x['B3'].value=='=SUM(A1:A2)' and x['B3'].data_type=='s'
 wb.close();return check
record('reconstructed_numeric_cells_missing_masks_literal_companions',reconstructed)
def blanktotal():
 out=setup('blank_total',convert=False);rows=csvrows(out/'Landings.csv');rows[1][-1]=''
 with (out/'Landings.csv').open('w',encoding='utf8',newline='') as f:csv.writer(f,lineterminator='\r\n').writerows(rows)
 d=sf.preserve_source(out,{'group':[]});g=groups(d)['1'];assert g['landings_total']=='-9999' and g['export']=='-9999'
 return 'An explicit blank Total stays unknown even when fleet cells are numeric.'
record('blank_reported_total_preservation',blanktotal)
def wholearea():
 m=copy.deepcopy(BASE);m['metadata'].update(biomass_basis='whole_model_area',ba_basis='whole_model_area',export_basis='reported_landings')
 out=setup('whole_area',m);d=converted(out);g=groups(d)['1'];assert val(g['biomass'])==10 and val(g['biomass_accum'])==2
 assert val(g['export'])==Decimal('1.5') and val(g['total_removals'])==Decimal('1.7')
 return 'Explicit whole-area and reported-landings conventions respected without dropping retained discards.'
record('explicit_area_and_export_conventions',wholearea)
def invalid_companions():
 bad=['../escape.csv','/escape.csv','a/b.csv','a\\b.csv','C:escape.csv','Basic_input.csv','bAsIc_InPuT.csv','a.txt','.hidden.csv']
 for i,name in enumerate(bad):
  out=P/f'bad_name_{i}';out.mkdir(exist_ok=True)
  try:sf.write_companions({'companions':{name:{'description':'test','rows':[['x'],['1']]}}},out)
  except ValueError:pass
  else:raise AssertionError('Unsafe name accepted: '+name)
 return {'rejected_names':bad}
record('safe_companion_paths_and_reserved_import_names',invalid_companions)
def windows_reserved():
 out=P/'reserved_names';out.mkdir(exist_ok=True)
 original_open=Path.open
 def intercepted(path,*args,**kwargs):
  if path.name.upper() in {'CON.CSV','NUL.CSV','AUX.CSV','PRN.CSV','COM1.CSV','LPT9.CSV'}:
   raise AssertionError('Reserved Windows device basename reached filesystem write: '+path.name)
  return original_open(path,*args,**kwargs)
 for name in ['CON.csv','NUL.csv','AUX.csv','PRN.csv','COM1.csv','LPT9.csv']:
  with patch.object(Path,'open',intercepted):
   try:sf.write_companions({'companions':{name:{'description':'test','rows':[['x'],['1']]}}},out)
   except ValueError:pass
   else:raise AssertionError('Reserved name not rejected: '+name)
 return 'Windows device basenames rejected before filesystem write (writes intercepted in test).'
record('windows_reserved_device_filenames',windows_reserved)
def malformed_companions():
 bad=[[['x','x'],['1','2']],[['x',''],['1','2']],[['x','y'],['1']],[[None,'y'],['1','2']]]
 accepted=[]
 for i,rows in enumerate(bad):
  out=P/f'bad_table_{i}';out.mkdir(exist_ok=True)
  try:sf.write_companions({'companions':{'bad.csv':{'description':'test','rows':rows}}},out)
  except ValueError:pass
  else:accepted.append(i)
 assert not accepted,{'accepted_invalid_table_cases':accepted,'cases':bad}
 return 'Duplicate/blank/null headers and ragged tables rejected.'
record('invalid_table_schema_rejection',malformed_companions)
def stale():
 out=P/'stale';out.mkdir(exist_ok=True);m=copy.deepcopy(BASE);sf.write_companions(m,out)
 del m['companions']['Source_stanzas.csv'];sf.write_companions(m,out)
 assert not (out/'companions/Source_stanzas.csv').exists();assert len(json.loads((out/'companions/manifest.json').read_text())['files'])==2
 m['companions']={};sf.write_companions(m,out);assert json.loads((out/'companions/manifest.json').read_text())['files']==[]
 assert not list((out/'companions').glob('*.csv'))
 sf.write_companions(BASE,out);(out/'companions/Source_fields.csv').write_text('modified',encoding='utf8')
 try:sf.write_companions({'companions':{}},out)
 except ValueError as exc:assert 'manually changed' in str(exc)
 else:raise AssertionError('Modified omitted companion deleted')
 assert (out/'companions/Source_fields.csv').read_text()=='modified'
 return 'Removed only hash-matching omitted companions; modified omitted file rejected and retained.'
record('stale_manifest_and_modified_omission',stale)
def trailing_grid():
 d=copy.deepcopy(DATA);d['published_companions']={'trailing.csv':{'description':'Trailing source rows','rows':[['ID','value',''],['1','0.00',''],['','','']]}}
 output=P/'trailing_grid.xlsx';sf.reconstruct_source_workbook(d,output)
 return 'Trailing entirely empty source-grid rows and columns retained.'
record('trailing_blank_source_grid',trailing_grid)
summary={'tested_revision_sha256':{n:hashlib.sha256((SK/'scripts'/n).read_bytes()).hexdigest() for n in ['source_fidelity.py','write_outputs.py','database_json.py']},'results':results,'passed':sum(x['passed'] for x in results),'failed':sum(not x['passed'] for x in results),'scope':'Synthetic independent fixtures only; actual regional and source model files untouched.'}
(P/'independent_results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
sys.exit(bool(summary['failed']))
