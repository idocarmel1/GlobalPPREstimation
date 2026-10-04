"""Cross-check source extraction against official HTML and retained artifacts."""
from pathlib import Path
import json,hashlib,csv,shutil,sys
from decimal import Decimal
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_050';REV=Path(__file__).parent;SRC=REG/'papers/SOJ-2023';EV=SRC/'evidence'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
t1=read(EV/'publisher_table_1_all_tables.json');t2=read(EV/'publisher_table_2_all_tables.json')
assert len(t1)==2 and len(t2)==1
report={'independent_source_verification':'PDF coordinate extraction versus official publisher HTML tables; the web table also contains only one diet matrix','models':[],'source_checksums':{}}
for path,expected in [(next(SRC.glob('*.pdf')),'eaca3b45c0e93645aa071099876a4490ac5cac4418a3eb4472ef8a85188a46c3'),(next(SRC.glob('*.docx')),'8d668bb077ed7149b8bd83a862d46911fabb16c3b34bb3553b399ecc7071602e')]:
 actual=hashlib.sha256(path.read_bytes()).hexdigest();assert actual==expected;report['source_checksums'][path.name]=actual
assert (EV/'publisher_supplement_verification.docx').read_bytes()==next(SRC.glob('*.docx')).read_bytes()
for yi,year in enumerate([1985,2013]):
 mid=f'50_50{year}_Coastal_Kyoto_Inoue_({year})';d=REG/'models'/mid;e=d/'extracted_tables';s=read(e/'model.json');c=read(d/'model.json');checks=0
 for g,row in zip(s['groups'],t1[yi][1:]):
  assert int(row[0])==g['n'] and row[1]==g['name']
  for key,value in zip(['tl','biomass','pb','qb','pq','ee'],row[2:]):
   assert g[key]==(value or None),(year,g['n'],key,g[key],value);checks+=1
 dietchecks=0;implicit_blanks=0;explicit_zeros=0
 for original_row in t2[0][1:]:
  row=list(original_row)
  # Official HTML spans the Spanish-mackerel name over its blank predator-1 cell.
  # Verified from td colspan=2 and the rendered PDF; preserve raw HTML separately.
  if row[0]=='10' and len(row)==39:row.insert(2,'')
  prey=row[0] or row[1].lower()
  if prey=='sum':continue
  assert len(row)==40
  for predator,value in enumerate(row[2:],1):
   extracted=s['diet'][str(predator)].get(str(prey))
   assert extracted==(value or None),(year,prey,predator,value,extracted)
   dietchecks+=1;implicit_blanks+=not bool(value);explicit_zeros+=bool(value) and Decimal(value)==0
 for name in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx','Taxonomy.xlsx']:
  assert (e/name).exists()
 for name in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv']:
  data=(e/name).read_bytes();assert b'"' not in data and b'\r\n' in data
 checksum=hashlib.sha256((d/'model.json').read_bytes()).hexdigest()
 assert read(d/'evidence/diagnostic_provenance.json')['source_sha256']==checksum
 for opt in ['GE','TE','With_Egestion']:
  r=read(d/f'evidence/diagnose_sppr_{opt}.json');assert r['call_error'] is None and r['direct_diagnose_sppr_return']['status']=='WARN'
  assert set(r['direct_diagnose_sppr_return'])=={'status','model_input','divergence','balance','footprint','config','warnings'}
  assert r['configuration']['short'] is False and r['configuration']['flat'] is False
  assert r['configuration']['TE_option']!='global'
 assert (d/'evidence'/f'{mid}.json').read_bytes()==(d/'model.json').read_bytes()
 manifests=read(d/'source_manifest.json')
 for m in manifests:
  m['source_url']='https://doi.org/10.1007/s12562-023-01691-9' if m['path'].endswith('.pdf') else 'https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs12562-023-01691-9/MediaObjects/12562_2023_1691_MOESM1_ESM.docx'
 dump(d/'source_manifest.json',manifests)
 report['models'].append({'model_id':mid,'source_parameter_cells':checks,'diet_cells_including_import_checked':dietchecks,'diet_blank_cells_preserved':implicit_blanks,'diet_printed_zeros_preserved':explicit_zeros,'source_group_count':40,'diagnostic_options':['GE','TE','With Egestion'],'diagnostic_statuses':['WARN','WARN','WARN'],'canonical_sha256':checksum,'roundtrip_status':read(d/'evidence/ROUNDTRIP_VERIFICATION.json')['status']})
 code=REV/'extraction_code';code.mkdir(exist_ok=True)
 for name in ['write_outputs.py','validate.py','massbalance_check.py','database_json.py','pdf_backend.py','prose_sweep.py','check_environment.py']:
  shutil.copy2(Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')/name,code/name)
 for name in ['extract_sources.py','finalize_review.py','verify_deliverables.py']:shutil.copy2(REV/name,d/'diagnostic_code'/name)
 for name in ['extract_sources.py','finalize_review.py','verify_deliverables.py']:shutil.copy2(REV/name,code/name)
report['extraction_code_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in code.glob('*.py')}
report['python']=sys.version;report['production_workbook_not_written_by_review']=True;report['central_registration']='prepared_not_registered';report['result']='PASS'
dump(REV/'FINAL_VERIFICATION.json',report)
print(json.dumps({k:v for k,v in report.items() if k not in ['extraction_code_sha256','source_checksums']},indent=2))
