from pathlib import Path
import json,sys,subprocess,os,shutil,hashlib,csv
from decimal import Decimal as D
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def flat(records):
 keys=list(dict.fromkeys(k for r in records for k in r))
 return [keys]+[[json.dumps(r[k],ensure_ascii=False) if isinstance(r.get(k),(dict,list)) else ('' if r.get(k) is None else str(r[k])) for k in keys] for r in records]
tables=load(HERE/'original_docx_tables.json')['tables'];env=dict(os.environ,PYTHONIOENCODING='utf-8');styles=load(HERE/'original_docx_styles.json')
titles=['S1_membership','S2_diet_block1','S2_diet_block2','S2_diet_block3','S3_fleet_effort','S4_mammals','S5_birds','S6_benthos','S7_time_series','S8_scenarios','S9_1991_2006_outputs']
results=[]
for v in ['Base','M30','P30']:
 d=ROOT/f'regions/LME_027/models/Guenette2014_BancArguin_{v}_1991';e=d/'extracted_tables';m=load(e/'extraction.json')
 m['metadata']['biomass_basis']='whole_model_area';m['metadata']['export_basis']='reported_landings'
 pl=load(e/'PARAMETER_CELL_LEDGER.json')
 for g in m['groups']:
  g['parameter_roles']={field:('unknown' if g.get(field) is None else 'published_input') for field in ['biomass','pb','qb','ee','pq']}
  for entry in pl:
   if entry['group']==g['n'] and entry['field'] in g['parameter_roles']:g['parameter_roles'][entry['field']]=entry['category'] if entry['category'] in ['model_estimated','derived'] else ('unknown' if entry.get('adopted_literal') is None else 'published_input')
  if v!='Base':
   for field,col in [('biomass',6 if v=='M30' else 10),('ee',7 if v=='M30' else 11)]:
    style=next(x for x in styles if x['physical_table']==10 and x['row']==g['n']+3 and x['column']==col)
    g['parameter_roles'][field]='model_estimated' if style['explicit_bold'] else 'published_input'
 m['companions']={}
 for name,rows in zip(titles,tables):m['companions']['Source_'+name+'.csv']={'description':'Original supplement Table '+name+'; mixed table headers preserved, interpret with source caption; source evidence, not EwE import or asserted focal-variant input','layout':'source_grid','rows':rows}
 for filename,desc in [('DIET_CELL_LEDGER.json','Exact source diet %, conversion, source blank versus unpublished variant cell and inherited status'),('PARAMETER_CELL_LEDGER.json','Exact Table1/S8 fields, source locators and parameter provenance'),('STANZAS.json','Published adult/juvenile links and ages; unknown VBK and native equation limits'),('GROUP_CROSSWALK.json','Exact group identities and Table1/S8 source-name aliases'),('SOURCE_CONFLICTS.json','Competing Table1 versus S8 Base values and adopted source')]:
  m['companions']['Source_'+Path(filename).stem.lower()+'.csv']={'description':desc+'; source evidence, not EwE import','rows':flat(load(e/filename))}
 vec=load(HERE/f'{v}_vectors.json')
 m['companions']['Source_catch_totals.csv']={'description':'Published Table1 total catch and recalculated 3-fleet sum; variant catch inherited Base; no discard information','rows':[['group_id','group_name','reported_total_t_km2_year','fleet_sum_t_km2_year','status']]+[[str(g['n']),g['name'],vec['reported_total_catches'][str(g['n'])],str(sum((D(x) for x in m['landings'][str(g['n'])].values() if x is not None),D(0))),'published_Base' if v=='Base' else 'inherited_Base'] for g in m['groups']]}
 m['companions']['Source_variant_constraints.csv']={'description':'S8 aggregate pBA; does not uniquely identify unpublished prey redistributions','rows':flat(m['extraction_notes']['pBA_constraints'])}
 m['companions']['Source_model_fields.csv']={'description':'Published/source-identity fields outside Metadata.xlsx fixed 4-row schema; evidence only','rows':[['field','value','status','source']]+[[k,str(x),'published_or_identity','article p2; DOI'] for k,x in m['metadata'].items()]}
 m['companions']['Source_S8_formatting.csv']={'description':'Original DOCX explicit run bold/italic markup; S8 caption defines bold B/EE as model estimated','rows':flat([x for x in styles if x['physical_table']==10])}
 m['companions']['Source_parameter_roles.csv']={'description':'Source input versus Ecopath-estimated roles from Table1 bold markup and S8 bold cells; rates and values unchanged','rows':[['group_id','field','role']]+[[str(g['n']),f,r] for g in m['groups'] for f,r in g['parameter_roles'].items()]}
 # Retain original XLS Table2 even though it summarizes downstream model outputs.
 tb=load(HERE/'Table_2-3434d627.xls.cells.json')['sheets'][0]
 m['companions']['Source_Table2_cells.csv']={'description':'Original article Table2 comparison of model outputs; not imported as Ecopath parameters','rows':flat(tb['cells'])}
 save(e/'extraction.json',m)
 # Snapshot existing canonical's biological values before improved conversion.
 old=load(d/'model.json');save(HERE/f'{v}_pre_improved_standard_fields.json',old['group'])
 (e/'REPORT.md').write_text('# '+v+' source extraction\n\n## Mass balance\nPending final review.\n',encoding='utf-8')
 for name,args,log in [('write_outputs.py',[str(e/'extraction.json'),'--outdir',str(d),'--dir-name','extracted_tables'],'IMPROVED_WRITER_LOG.txt'),('validate.py',[str(e)],'VALIDATION.txt'),('massbalance_check.py',[str(e)],'MASS_BALANCE_CHECK.txt'),('database_json.py',['-d',str(e),'--update-report'],'IMPROVED_CONVERTER_LOG.txt')]:
  p=subprocess.run([sys.executable,str(SKILL/name)]+args,capture_output=True,text=True,encoding='utf-8',env=env);(e/log).write_text(p.stdout+p.stderr,encoding='utf-8');print(v,name,p.returncode,flush=True)
  if name in ['write_outputs.py','database_json.py']:assert p.returncode==0,p.stderr[-1500:]
 # Database converter derives its identity from the unchanged standard Metadata workbook.
 candidates=[p for p in e.glob('*.json') if p.name.startswith('27_Canary_Current_Guenette2014_')]
 assert len(candidates)==1,[p.name for p in candidates]
 jp=candidates[0];new=load(jp);shutil.copyfile(jp,d/'model.json');shutil.copyfile(jp,e/'canonical_database.json')
 xp=jp.with_name(jp.stem+'_reconstructed.xlsx');shutil.copyfile(xp,e/'canonical_reconstructed.xlsx')
 # Check exact standard fields against fresh source extraction, not only JSON extension.
 errors=[]
 for g,s in zip(new['group'],m['groups']):
  assert g['group_name']==s['name'] and g['group_seq']==str(s['n'])
  for a,b in [('biomass','biomass'),('pb','pb'),('z','z'),('qb','qb'),('ee','ee'),('ge','pq'),('tl','tl'),('biomass_accum_rate','ba_rate')]:
   expected='-9999' if s.get(b) is None else str(s[b])
   if g[a]!=expected:errors.append([s['n'],a,expected,g[a]])
  if s['n']<=47:
   for cell in g['diet_descr']['diet']:
    expected=m['diet'][str(s['n'])][cell['prey_seq']];expected='-9999' if expected is None else expected
    if cell['proportion']!=expected:errors.append([s['n'],'diet',cell['prey_seq'],expected,cell['proportion']])
  for fleet,expected in m['landings'][str(s['n'])].items():
   if g['landings_by_fleet'][fleet]!=('-9999' if expected is None else expected):errors.append([s['n'],'fleet',fleet])
 sf=load(e/'SOURCE_FIDELITY_CHECK.json');assert sf['numeric_value_and_missing_mask_match'];assert not errors,errors
 result={'variant':v,'installed_workflow':True,'source_to_standard_json_checks_passed':not errors,'standard_schema_unchanged':True,'workbook':sf,'errors':errors,'canonical_sha256':sha(d/'model.json'),'extraction_sha256':sha(e/'extraction.json'),'companion_tables':len(m['companions']),'canonical_path':str((d/'model.json').relative_to(ROOT)).replace('\\','/')}
 save(e/'ROUNDTRIP_CHECK.json',result);results.append(result)
 print(v,'installed workflow complete',len(m['companions']),'companions',flush=True)
save(HERE/'improved_workflow_results.json',results)
