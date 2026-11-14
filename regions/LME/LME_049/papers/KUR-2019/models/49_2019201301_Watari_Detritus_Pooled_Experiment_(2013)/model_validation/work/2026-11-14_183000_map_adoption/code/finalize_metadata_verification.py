"""Repair only the staged Settings placement and bind final verifier provenance."""
from pathlib import Path
import importlib.util,json,os,shutil,zipfile
from xml.etree import ElementTree as ET
SCRIPT=Path(__file__).resolve()
spec=importlib.util.spec_from_file_location('_lme049_final_verifier',SCRIPT.with_name('verified_lme049_package.py'))
wrapper=importlib.util.module_from_spec(spec);spec.loader.exec_module(wrapper)
base=wrapper.base;meta=wrapper.meta
package=base.DEFAULT_PACKAGE;model=package/'model'/base.MID;regional=package/'regional'/(base.UNIT+'.xlsx')
evidence=model/'results/diagnostics'/base.PREFIX
plan=base.read(package/'preparation.json');manifest_path=model/'results/result_manifest.json';manifest=base.read(manifest_path)
ledger_path=evidence/'metadata_reconciliation.json';ledger=base.read(ledger_path)
if plan.get('metadata_finalization'):raise ValueError('Finalization already performed; use verify')
# Preserve the actual source bytes used by the completed initial metadata step.
initial_sources=[]
for old,name,role in [('postrun_verifier.py','initial_metadata_wrapper.py','initial_metadata_wrapper'),
                      ('metadata_reconciliation.py','initial_metadata_postprocessor.py','initial_metadata_postprocessor')]:
 destination=evidence/name;shutil.copyfile(evidence/old,destination);initial_sources.append(destination)
 workcopy=base.RUN/'inputs/postprocessing_initial_code'/name;workcopy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(destination,workcopy)
 manifest['method_coverage']['execution_evidence'][role]={'path':base.PREFIX+'/'+name,'sha256':base.sha(destination)}
before=meta.numeric_xml(regional)
from tools.project_core.validation.researcher_review import S,table_rows,sheet_xml
ns='{'+S+'}'
fields={'production_eligibility_note','diagnostic_status_provenance'}
with zipfile.ZipFile(regional) as archive:
 entries={i.filename:(i,archive.read(i.filename)) for i in archive.infolist()}
 name=sheet_xml(archive,'Overview')[0];sheet,_,_,settings=table_rows(archive,'Overview','Settings')
 data=sheet.find(ns+'sheetData');last=max(int(row.get('r')) for row,_ in settings)
 movers=[]
 for row in list(data):
  first=next((c for c in row if c.get('r').startswith('A')),None)
  label=''.join(first.itertext()) if first is not None else None
  if label in fields:movers.append(row);data.remove(row)
 if len(movers)!=2:raise ValueError('Expected two staged notes in wrong table')
 for row in movers:
  index=last+1
  for later in reversed(list(data)):
   old_index=int(later.get('r'))
   if old_index>=index:
    later.set('r',str(old_index+1))
    for cell in later:cell.set('r',''.join(c for c in cell.get('r') if c.isalpha())+str(old_index+1))
  row.set('r',str(index))
  for cell in row:cell.set('r',''.join(c for c in cell.get('r') if c.isalpha())+str(index))
  position=next((i for i,r in enumerate(data) if int(r.get('r'))>index),len(data));data.insert(position,row);last=index
 dimension=sheet.find(ns+'dimension')
 if dimension is not None:dimension.set('ref','A1:B'+str(max(int(r.get('r')) for r in data)))
 entries[name]=(entries[name][0],ET.tostring(sheet,encoding='utf-8',xml_declaration=True))
temporary=regional.with_name('LME_049.metadata-final.xlsx')
with zipfile.ZipFile(temporary,'w') as archive:
 for info,raw in entries.values():archive.writestr(info,raw)
with zipfile.ZipFile(temporary) as archive:
 if archive.testzip() is not None:raise ValueError('Final staging ZIP invalid')
 _,_,_,settings=table_rows(archive,'Overview','Settings');now={r['field']:r.get('value') for _,r in settings}
 for item in ledger['overview_changes']:
  if item['field'] in fields and now.get(item['field'])!=item['after']:raise ValueError('Staged notes not in Settings')
 with zipfile.ZipFile(base.REGION) as original:
  original_available=[r for _,r in table_rows(original,'Overview','Available models')[3]]
 if [r for _,r in table_rows(archive,'Overview','Available models')[3]]!=original_available:raise ValueError('Available model entries changed')
os.replace(temporary,regional)
if meta.numeric_xml(regional)!=before or before!=plan['postrun_verifier']['numeric_xml_sha256_unchanged']:raise ValueError('Numeric XML changed')
shutil.copyfile(regional,model/'results/regional_snapshot.xlsx')
manifest['snapshot_sha256']=base.sha(regional)
ledger['reconciled_staged_workbook_sha256']=base.sha(regional)
ledger['postprocessing_finalization']={'reason':'Initial verification caught two new notes under Available models; moved their exact text into Settings.',
 'scope':'Overview row placement only; no numeric, coefficient, input, status or wording changes.',
 'actual_initial_sources':{p.name:base.sha(p) for p in initial_sources},
 'source':base.relative(SCRIPT),'source_sha256':base.sha(SCRIPT),'numeric_xml_unchanged':True}
base.write(ledger_path,ledger);base.write(base.RUN/'qa/metadata_reconciliation.json',ledger)
added=initial_sources[:]
sources=[(wrapper.SCRIPT,'postrun_verifier.py','final_postrun_verifier'),
 (wrapper.SCRIPT.with_name('metadata_reconciliation.py'),'metadata_reconciliation.py','corrected_metadata_recipe_not_reexecuted'),
 (SCRIPT,'finalize_metadata_verification.py','executed_metadata_placement_finalizer')]
manifest['method_coverage']['execution_evidence'].pop('postrun_verification_only',None)
manifest['method_coverage']['execution_evidence'].pop('authorized_metadata_postprocessing_only',None)
for source,name,role in sources:
 destination=evidence/name;shutil.copyfile(source,destination);added.append(destination)
 manifest['method_coverage']['execution_evidence'][role]={'path':base.PREFIX+'/'+name,'sha256':base.sha(destination)}
 plan['consumed_inputs'][base.relative(source)]=base.sha(source)
manifest['method_coverage']['execution_evidence']['metadata_reconciliation']['sha256']=base.sha(ledger_path)
manifest['postrun_verification']['postrun_verifier_sha256']=base.sha(wrapper.SCRIPT)
manifest['postrun_verification']['finalization']='Explicit Settings-placement repair; actual initial postprocessing bytes retained separately.'
base.write(manifest_path,manifest)
existing={p['source'] for p in plan['promotions']}
for source in added:
 source_name=base.relative(source,package)
 if source_name not in existing:
  item={'source':source_name,'target':base.relative(base.MODEL/source.relative_to(model)),'sha256':base.sha(source)}
  plan['promotions'].append(item);plan['consumed_inputs'][item['target']]=base.fingerprint(base.ROOT/item['target'])
for item in plan['promotions']:item['sha256']=base.sha(package/item['source'])
plan['postrun_verifier'].update(sha256=base.sha(wrapper.SCRIPT),metadata_script_sha256=base.sha(wrapper.SCRIPT.with_name('metadata_reconciliation.py')),metadata_reconciliation_sha256=base.sha(ledger_path))
plan['metadata_finalization']={'path':base.relative(SCRIPT),'sha256':base.sha(SCRIPT),'numeric_cells_changed':False}
base.write(package/'preparation.json',plan)
wrapper.verify_package(package)
print(json.dumps({'package':base.relative(package),'promotions':len(plan['promotions']),'verified':True,'scientific_solve_performed':False}),flush=True)

