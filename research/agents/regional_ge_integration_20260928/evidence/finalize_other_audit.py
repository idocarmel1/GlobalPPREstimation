from pathlib import Path
import sys,json,zipfile,xml.etree.ElementTree as ET,math,hashlib
ROOT=Path.cwd();D=Path(__file__).resolve().parent;NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
sys.path.insert(0,str(ROOT/'tools'));from workbooks import numeric_status

def sheet_tables(path,num):
 with zipfile.ZipFile(path) as z:
  root=ET.fromstring(z.read(f'xl/worksheets/sheet{num}.xml'));tables={};name=None;hdr=None
  for row in root.findall('s:sheetData/s:row',NS):
   vals=[]
   for c in row:
    col=''.join(t for t in c.get('r','') if t.isalpha());idx=0
    for t in col:idx=idx*26+ord(t)-64
    while len(vals)<idx:vals.append(None)
    tt=c.findall('.//s:t',NS);v=c.find('s:v',NS);value=''.join(t.text or '' for t in tt) if tt else None
    if v is not None:
     value=v.text
     if c.get('t')=='b':value=value=='1'
     elif c.get('t') not in ['s','str','inlineStr']:
      value=float(value);value=int(value) if value.is_integer() else value
    if idx:vals[idx-1]=value
   if not vals:continue
   if vals[0]=='@table':name=vals[1];hdr=None;tables[name]=[]
   elif name:
    if hdr is None:hdr=vals
    else:tables[name].append(dict(zip(hdr,vals+[None]*max(0,len(hdr)-len(vals)))))
  return tables

raw=json.loads((D/'other_regions_raw_audit.json').read_text(encoding='utf-8'));inv=json.loads((D/'all_region_overview_inventory.json').read_text(encoding='utf-8'));out=[]
caveats={
'LME_003':'Existing separately verified conditional author-equation reconstruction; retained GS/routing defaults, low-confidence unidentified demersal pooling and unknown geographic overlap. Partial mapped catch, not annual ecosystem reconstruction.',
'LME_014':'Existing selected native Falkland shelf2020 model; three direct configurations WARN and geographically local model. Partial mapped catch and fixed model over history; preserved rather than rerun.',
'LME_028':'Geographic transfer from country Guinea111932km2 to Guinea Current LME;13 B/EE printed-source discrepancies retained. Low-confidence coarse allocation and source-supported synonyms remain assumptions.',
'LME_032':'Karnataka shelf27000km2 transferred to Arabian Sea LME. Mapping sources rederived previously, with estimated coarse-catch allocations, not published composition.',
'LME_034':'Whole-LME catch allocated across model geographical subregions2/3 using biomass/shelf-area proxies. Maldives region1 excluded.100% label assignment is not100% geographic/scientific validation.',
'LME_035':'MATERIAL IDENTITY WARNING: selected filename/year1963 actually contains1980 parameters (11/11 printed biomass values agree1980;10 differ1963).10-50m shelf to full LME transfer; no complete printed parameter table. Preserve identity warning.',
'LME_036':'Northern Chinese shelf(<200m) transferred to full South China Sea LME. Printed source numerical conflicts unresolved; coarse catch and stage selectivity proxies retained.',
'LME_038':'Explicitly user-authorized normalized/BA-completed Java Sea variant. Macrozoobenthos diet divided0.660,28 signed BA values computational not measured. Local area471000km2 transferred to LME; inherited stage/biomass proxies. Historical Monte Carlo exists but none run in this task.',
'LME_047':'2018 source membership feeding-guild model with coarse catch-composition allocations. Whole-LME coverage historically assumed without verified model area; no new scientific approval here.',
'LME_050':'Prior direct/source review and exact/synonym-only mapping preserved; Kyoto coastal model yields25.05%2019 catch subtotal. Most whole-LME stocks unsupported; production_eligible false.',
'LME_052':'Sea of Okhotsk NE is model identifier, not northeastern subregion. Printed consumer inputs agree; detritus biomass and full diet not independently source-verified. Pollock stages use model-biomass weights because model catch zero; composition proxy, not observed catch split.',
'LME_024':'Selected configuration originally FAIL with explicit routed experimental numeric outputs; delegated provisional mapping/integration handled by separate worker.',
'LME_026':'Source construction NOT_RUN; no numerical coefficient may be invented. Selected identity retained, unavailable until source/constructor block resolved.',
'LME_029':'Selected configuration FAIL; traceable numeric provisional integration delegated to separate worker.',
'EEZ_598':'WCPO Option1 mixed-period selected experiment: regional/provisional mapping handled by separate worker.',
'EEZ_941':'WCPO Option1 mixed-period selected experiment: regional/provisional mapping handled by separate worker.',
'HS_071':'WCPO Option1 mixed-period selected experiment: regional/provisional mapping handled by separate worker.'}
for x in raw:
 rid=x['unit_id'];p=ROOT/'regions'/rid/f'{rid}.xlsx';tables=sheet_tables(p,5);annual=tables.get('Annual',[]);matches=[r for r in annual if r.get('scope')=='all' and r.get('method')=='new_GE' and r.get('catch_basis')=='catch' and r.get('unidentified')=='method'];vals={r['metric']:r.get(2019,r.get('2019')) for r in matches};status=next((r.get('status') for r in matches if r['metric']=='ppr'),None)
 o={r['field']:r.get('value') for r in sheet_tables(p,1)['Settings']};vpath=p.parent/'models/regional_ge_integration_20260928/integration_verification.json';ver=json.loads(vpath.read_text(encoding='utf-8')) if vpath.is_file() else None
 prov='new exact-runtime replay and supported/provisional integration' if ver else 'retained migrated results; current bytes/fingerprints audited, no new scientific revalidation' if x['overview'].get('calculation_status','').startswith('migrated') else 'retained recent selected evidence audited; no new model rerun' if matches else 'no regional model output at this snapshot; see blocker/delegated work'
 record={'unit_id':rid,'selected_model_id':o['selected_model_id'],'selected_model_path':o['model_path'],'selection_rationale':o.get('selection_rationale'),'production_eligible':o.get('production_eligible'),'selected_model_sha256':x['model_sha256'],'workbook_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'provenance_class':prov,'initial_freshness_validation':x['freshness_validation'],'initial_result_fingerprint_matches':x['result_fingerprint_matches'],'current_status':status,'ge_carbon_tonnes_2019':vals.get('ppr')/9 if numeric_status(status) and isinstance(vals.get('ppr'),(int,float)) else None,'total_catch_tonnes_2019':vals.get('catch',x['mapping_coverage_2019']['total_catch_tonnes']),'covered_catch_tonnes_2019':vals.get('covered_catch'),'coverage_fraction_2019':vals['covered_catch']/vals['catch'] if vals.get('covered_catch') is not None and vals.get('catch') else None,'initial_mapping_coverage':x['mapping_coverage_2019'],'initial_ge_health':[r for r in x['diagnostics'].get('model_health',[]) if r.get('TE_option')=='GE'],'caveats':ver['caveats'] if ver else caveats.get(rid,''),'new_integration_verification':ver,'initial_largest_unresolved':x['largest_unresolved_2019']}
 m=p.parent/o['model_path'];record['retained_mapping_evidence_files']=[str(v.relative_to(ROOT)).replace('\\','/') for v in m.parent.glob('source_evidence/mapping/*.notes.md') if m.parent.name in v.name][:3]
 out.append(record)
report={'scope':'All current regional Overview selections inventoried; this worker excludes LME022,LME027,HS077. WCPO trio,LME024,LME029 delegated subsequently. No selection changes, source edits, global SPPR or Monte Carlo performed. Current regional snapshot; coordinating parent owns Project/map.','total_regions':len(inv),'selected_count':sum(bool(x.get('selected_model_id')) for x in inv),'unselected_count':sum(not x.get('selected_model_id') for x in inv),'unselected_regions':[x['unit_id'] for x in inv if not x.get('selected_model_id')],'unselected_blocker':'No selected Ecopath model; new selections not authorized in this subtask; independent classic/NPP preserved.','results_convention':'2019, source_scope all, total catch landings+discards, unidentified treatment method; source wet-equivalent PPR divided by9 once. Provisional means numerical output pending scientific validation. Partial catch coverage is not geographic model coverage. Do not sum overlapping regions.','regions':out,'changed_workbooks':['regions/LME_013/LME_013.xlsx','regions/LME_037/LME_037.xlsx','regions/LME_049/LME_049.xlsx']}
(D/'other_regions_audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# Other selected regions: GE integration and preservation audit','',report['scope'],'',f'{len(inv)} regional workbooks: {report["selected_count"]} selected, {report["unselected_count"]} without a selected model. No new selections made.','',report['results_convention'],'','| Region | 2019 GE t carbon | Catch coverage | Numerical status / provenance |','|---|---:|---:|---|']
for x in out:lines.append(f'| {x["unit_id"]} | '+(f'{x["ge_carbon_tonnes_2019"]:,.3f}' if x['ge_carbon_tonnes_2019'] is not None else 'unavailable')+' | '+(f'{x["coverage_fraction_2019"]:.2%}' if x['coverage_fraction_2019'] is not None else 'unavailable')+' | '+str(x['current_status'] or x['provenance_class']).replace('|','/')+' |')
lines+=['','## Scientific limitations','']
for x in out:lines.append(f'- **{x["unit_id"]}**: {x["caveats"]} Evidence class: {x["provenance_class"]}.')
lines+=['','## Checks and preservation','','Every assigned selected workbook initially passed freshness validation and result fingerprint checks. Original Openpyxl Overview-only inventory is all_region_overview_inventory.json; fast independent XML inventory agreed selected identities. Existing high mapping coverage does not revalidate ecological assumptions. New integration evidence is within each changed regional models/regional_ge_integration_20260928 folder: backups, exact runtime state, source bytes, full direct returns, health grades, transformations, coefficients, all taxon decisions and verification. No Project.xlsx or map writes by this worker.','',f'Unselected regions ({report["unselected_count"]}) remain explicitly categorized in JSON; no selection research was started.']
(D/'other_regions_audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print('Report written',len(out))
