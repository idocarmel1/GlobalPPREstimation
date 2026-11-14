"""Apply only the authorized staged text changes; preserve all numeric XML."""
import copy, hashlib, json, os, shutil, zipfile
from collections import Counter
from xml.etree import ElementTree as ET

def numeric_xml(path):
 from tools.project_core.validation.researcher_review import S,sheet_xml
 with zipfile.ZipFile(path) as archive:
  skip=sheet_xml(archive,'Overview')[0];cells=[]
  for name in sorted(archive.namelist()):
   if name.startswith('xl/worksheets/sheet') and name.endswith('.xml') and name!=skip:
    for cell in ET.fromstring(archive.read(name)).findall('.//{'+S+'}c'):
     value=cell.find('{'+S+'}v')
     if value is not None and cell.get('t') in (None,'n','b'):cells.append([name,cell.get('r'),cell.get('t'),value.text])
 return hashlib.sha256(json.dumps(cells,separators=(',',':')).encode()).hexdigest()

def patch_workbook(path,overrides,statuses,result_hash):
 from tools.project_core.validation.researcher_review import S,table_rows,sheet_xml
 ns='{'+S+'}'
 def put(row,column,value):
  address=column+row.get('r');cell=next((c for c in row if c.get('r')==address),None)
  if cell is None:cell=ET.SubElement(row,ns+'c',{'r':address})
  for child in list(cell):cell.remove(child)
  if value is None:cell.attrib.pop('t',None)
  else:
   cell.set('t','inlineStr');ET.SubElement(ET.SubElement(cell,ns+'is'),ns+'t').text=str(value)
 with zipfile.ZipFile(path) as archive:
  entries={i.filename:(i,archive.read(i.filename)) for i in archive.infolist()}
  name=sheet_xml(archive,'Overview')[0];sheet,_,_,records=table_rows(archive,'Overview','Settings')
  present={record['field']:row for row,record in records}
  last_setting=max(int(row.get('r')) for row in present.values())
  for key,value in {**overrides,'calculation_result_sha256':result_hash}.items():
   row=present.get(key)
   if row is None:
    data=sheet.find(ns+'sheetData');index=last_setting+1
    for later in reversed(list(data)):
     old_index=int(later.get('r'))
     if old_index>=index:
      later.set('r',str(old_index+1))
      for cell in later:
       letters=''.join(c for c in cell.get('r') if c.isalpha())
       cell.set('r',letters+str(old_index+1))
    row=ET.Element(ns+'row',{'r':str(index)})
    position=next((i for i,r in enumerate(data) if int(r.get('r'))>index),len(data))
    data.insert(position,row);put(row,'A',key);last_setting=index
   put(row,'B',value)
  dimension=sheet.find(ns+'dimension')
  if dimension is not None:dimension.set('ref','A1:B'+str(max(int(r.get('r')) for r in sheet.find(ns+'sheetData'))))
  entries[name]=(entries[name][0],ET.tostring(sheet,encoding='utf-8',xml_declaration=True))
  name=sheet_xml(archive,'PPR')[0];sheet,_,_,records=table_rows(archive,'PPR','Annual');counts=Counter()
  for row,record in records:
   change=statuses.get(record['method'])
   if change and record.get('status')==change['before']:put(row,'G',change['after']);counts[record['method']]+=1
  if counts!=Counter({key:63 for key in statuses}):raise ValueError('Wrong status replacement count')
  entries[name]=(entries[name][0],ET.tostring(sheet,encoding='utf-8',xml_declaration=True))
 temporary=path.with_name(path.stem+'.metadata-staging.xlsx')
 with zipfile.ZipFile(temporary,'w') as archive:
  for info,data in entries.values():archive.writestr(info,data)
 with zipfile.ZipFile(temporary) as archive:
  if archive.testzip() is not None:raise ValueError('Invalid staged ZIP')
 os.replace(temporary,path)

def reconcile(base,package,plan,manifest):
 from tools.project_core.workbooks.workbooks import read_book,overview,rows,input_hash
 from tools.project_core.calculations.regional import set_setting,result_hash
 from tools.project_core.calculations.snapshots import dependencies
 model=package/'model'/base.MID;regional=package/'regional'/(base.UNIT+'.xlsx')
 book=read_book(regional);prior=copy.deepcopy(book);settings=overview(book)
 old_numeric=numeric_xml(regional);source_sha=base.sha(model/'sppr_source.xlsx');old_workbook=base.sha(regional)
 original={
 'new_GE':'provisional: GE overall OK; strict SPPR balance false; missing Seabirds B=1/PB=QB=0; scientific validation pending',
 'new_TE_EEfix':'provisional: TE FAIL; negative unfished Seabirds sources; near-singular; source/default problems; scientific validation pending; negative source-group SPPR',
 'new_WithEgestion':'provisional: With Egestion overall OK; strict SPPR balance false; missing Seabirds B=1/PB=QB=0; scientific validation pending'}
 labels={'new_GE':'current GE diagnostic OK; strict input and SPPR balance pass; no negative source contributions',
 'new_TE_EEfix':'current TE diagnostic WARN for near-zero toothed-whale TE; strict input and SPPR balance pass; no negative source contributions; toothed whales excluded from displayed calculations only',
 'new_WithEgestion':'current With Egestion diagnostic OK; strict input and SPPR balance pass; no negative source contributions'}
 common='provisional: retained model, regional mapping and source-geography transfer assumptions; researcher validated 2026-11-14; '
 statuses={key:{'before':value,'after':common+labels[key]} for key,value in original.items()}
 counts=Counter((row[2],row[6]) for row in rows(book,'PPR','Annual'))
 for key,value in original.items():
  if counts[(key,value)]!=63 or counts[(key,'unavailable: simple reference has no source decomposition')]!=18:raise ValueError('Historical restriction inventory differs')
 direct={}
 for key,option in [('new_GE','GE'),('new_TE_EEfix','TE'),('new_WithEgestion','With_Egestion')]:
  diag=base.read(model/base.RETAINED/'outputs'/(option+'_diagnostic.json'))
  if diag['status']!=('WARN' if option=='TE' else 'OK') or diag['balance']['is_balanced'] is not True or diag['model_input']['is_model_balanced'] is not True:raise ValueError('Actual diagnostic does not support reconciliation')
  direct[key]={'status':diag['status'],'strict_input_balanced':True,'strict_sppr_balanced':True,'evidence':(base.RETAINED/'outputs'/(option+'_diagnostic.json')).as_posix()}
 current='Researcher-validated retained 2013 pooled-detritus scenario (2026-11-14): EE floor 0.1, seabird M0 and egestion exported, finalized BA/accounting. Current direct diagnostics GE OK, TE WARN (near-zero toothed-whale TE), With Egestion OK; all strict input and SPPR balances pass, with no negative source contributions. Both retained MC methods accepted 100/100 samples. '
 ledger_relative=base.PREFIX+'/metadata_reconciliation.json'
 overrides={
 'production_eligible':None,
 'production_eligibility_note':'Researcher-validated scenario; unqualified whole-region production eligibility is not established. Retained model, mapping, source and geography assumptions limit inference; approval does not infer missing source parameters or unrestricted regional applicability.',
 'source_note':current+'All 253 existing taxon allocations and applicable mapping/source/geography limitations remain; scientific inputs and regional mappings are unchanged. Toothed whales (all), seq 2, are excluded only from displayed calculations under the signed review and remain in full model diagnostics.',
 'calculation_status':'provisional: researcher-validated retained final-accounting scenario; 22 method returns; current GE OK, TE WARN, With Egestion OK; strict direct balances pass; model, mapping and source-geography transfer assumptions retained',
 'deferred_TE_investigation':'Historical request and former outcome (2026-09-28; superseded execution evidence): '+settings['deferred_TE_investigation']+' Current authenticated final-accounting outcome (2026-11-14): TE WARN, strict input/SPPR balance pass, no negative source contributions; MC TE accepted 100/100 with no rejected/diverged samples. Near-zero toothed-whale TE remains a current warning; that group is excluded from display only. Source-parameter uncertainty and the deferred seabird biomass/rate discrepancy remain.',
 'computational_runtime_evidence':os.path.relpath(base.MODEL/base.RETAINED/'outputs/initial_runtime.json.gz',base.REGION.parent).replace('\\','/'),
 'computational_state_sha256':base.sha(model/base.RETAINED/'outputs/initial_runtime.json.gz'),
 'diagnostic_status_provenance':os.path.relpath(base.MODEL/'results/diagnostics'/ledger_relative,base.REGION.parent).replace('\\','/')}
 overview_changes=[{'field':key,'before':settings.get(key),'after':value,'reason':'Current authorized scenario/review supersedes historical execution claims; scientific applicability limitations remain explicit.'} for key,value in overrides.items()]
 annual_changes=[]
 for row in rows(book,'PPR','Annual'):
  change=statuses.get(row[2])
  if change and row[6]==change['before']:
   annual_changes.append({'key':row[:6],'before':row[6],'after':change['after']});row[6]=change['after']
 for key,value in overrides.items():set_setting(book,key,value)
 if base._protected(book)!=base._protected(prior) or input_hash(book)!=input_hash(prior) or overview(book)['selection_rationale']!=settings['selection_rationale']:raise ValueError('Protected input changed')
 for key,change in statuses.items():
  outcome=manifest['method_coverage']['methods'][key]
  for scope,value in outcome['annual_status'].items():
   if value==change['before']:outcome['annual_status'][scope]=change['after']
 patch_workbook(regional,overrides,statuses,result_hash(book))
 if numeric_xml(regional)!=old_numeric or base.sha(model/'sppr_source.xlsx')!=source_sha:raise ValueError('Numeric cells changed')
 snapshot=model/'results/regional_snapshot.xlsx';shutil.copyfile(regional,snapshot)
 manifest['snapshot_sha256']=base.sha(snapshot);manifest['dependencies']=dependencies(book)
 provenance=base.MODEL/'extracted_tables/evidence/metadata_registration_proposal.json'
 ledger={'schema_version':1,'scope':'Authorized staged metadata-only reconciliation after retained-output import',
 'authorization':'Root confirmed current user validation and approved this exact metadata reconciliation; no live writes.',
 'overview_changes':overview_changes,'annual_status_changes':annual_changes,
 'source_provenance_for_eligibility':{'path':base.relative(provenance),'sha256':base.sha(provenance),'meaning':'production_eligible=false originated in unselected/not-production-adopted experiment; no independent unrestricted whole-region eligibility test was defined.'},
 'current_authenticated_direct_diagnostics':direct,
 'current_mc':{key:{'accepted':100,'rejected_negative':0,'rejected_diverged':0} for key in ('MC_new_GE','MC_new_TE_EEfix')},
 'preserved':{'numeric_xml_sha256_before':old_numeric,'numeric_xml_sha256_after':numeric_xml(regional),'source_workbook_sha256':source_sha,
 'scientific_inputs':True,'full_classic':True,'selection_rationale_verbatim':True,'mapping_source_geography_limits':True,'unsupported_rows_per_original_method':18,'new19_method_statuses_unchanged':True,'raw_mc_draws':True,'provisional_prefixes':True},
 'historical_restrictions_suppressed_current_numerical_display':False,
 'historical_restriction_reason':'All three old execution restrictions began provisional; replacement corrects false current labels without enabling suppressed numbers.',
 'original_staged_workbook_sha256':old_workbook,'reconciled_staged_workbook_sha256':base.sha(regional),
 'scientific_solve_performed':False,'live_writes':False}
 destination=model/'results/diagnostics'/ledger_relative
 base.write(destination,ledger);base.write(base.RUN/'qa/metadata_reconciliation.json',ledger)
 plan['consumed_inputs'][base.relative(provenance)]=base.sha(provenance)
 return destination,ledger

