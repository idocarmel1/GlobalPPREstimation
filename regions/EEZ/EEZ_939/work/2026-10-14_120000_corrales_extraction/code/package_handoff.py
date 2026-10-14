"""Finish inventories and remove only verified redundant task artifacts."""
from pathlib import Path
import json,csv,sys,hashlib,os,shutil,datetime,ast,subprocess
from urllib.parse import unquote
import openpyxl
ROOT=Path(__file__).resolve().parents[6];WORK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));from tools.project_core.registry.discovery import discover_models
from tools.project_core.workbooks.workbooks import read_book,digest_tables,records
PAPER=ROOT/'regions/EEZ/EEZ_939/papers/Corrales-2010';BASE=PAPER/'models';RUN=WORK.name
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def rel(p,d):return Path(os.path.relpath(p,d)).as_posix()
manifest=load(PAPER/'source_manifest.json');registration=load(WORK/'outputs/registry_receipt.json')
assert len(discover_models(ROOT/'regions/EEZ/EEZ_939'))==8
original_region=load(WORK/'inputs/region_tables.json');assert digest_tables(original_region)==digest_tables(read_book(ROOT/'regions/EEZ/EEZ_939/EEZ_939.xlsx'))
# Explicit threshold inventory from the executed, already hash-checked engine.
tree=ast.parse((ROOT/'tools/scientific_code/PPREstimation/PPRCalculator.py').read_text(encoding='utf-8'));thresholds=None
for n in tree.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DEFAULT_DIAGNOSTIC_THRESHOLDS' for t in n.targets):thresholds=ast.literal_eval(n.value)
assert thresholds is not None
dispositions=[];outcomes=[]
for m in sorted(BASE.iterdir()):
 if not (m/'model.json').exists():continue
 e=m/'extracted_tables/evidence';d=m/'results/diagnostics';period='1990_1994' if '1990_1994' in m.name else '2008_2012';source=BASE/f'Corrales_2017_ICS_{period}';full=(m/'model_validation/validation.docx').exists();fit='gray_fit' in m.name
 dump(d/'method_contract.json',{'schema_version':1,'constructor_identity':'PPRCalculator.from_modeldata','method_identity':'PPRCalculator.diagnose_sppr(short=False, flat=False, return_sppr=True)','requested_options':['GE','TE','With Egestion'],'thresholds':thresholds,'threshold_overrides':None,'negative_entry_tolerance':1e-12,'source_scope_definitions':{'all':'All retained basal sources including synthetic imported diet, Discards, natural Detritus and both primary producers','inner':'All basal sources except synthetic imported diet','PP':'The two primary-producer columns only'},'SPPR_units':'wet-weight primary-production equivalent per wet-weight group production','SPPR_orientation':'Rows recipient group; columns basal source','A_L_orientation':'Engine original square group axes retained','synthetic_import':'One extra computational group, excluded from ecological group count','restriction':'Finite coefficients retained with actual diagnostic grades; no validated annual adoption'})
 if fit:dump(d/'diagnostic_documentation.json',{'schema_version':1,'annotation':'The historical source_gray_cells boilerplate in diagnostic_manifest.json describes the parent source extraction. This fitted variant has numeric inferred gray values; canonical group payload, loaded_before.json and fitted-cell ledger show the exact executed values. No return, scientific grade, input hash or timestamp is altered.','current_model_sha256':sha(m/'model.json'),'current_extraction_check':'../../extracted_tables/evidence/CURRENT_VARIANT_CHECK.json'})
 shutil.copy2(WORK/'code/run_sppr.py',d/'run_sppr.py')
 # The rerun helper now labels source and inferred gray cells correctly. Its actual
 # historical returned files remain unchanged and retain the documentation above.
 helper=(d/'run_sppr.py').read_text(encoding='utf-8');helper=helper.replace("'source_gray_cells':'Preserved as -9999; zero conversion occurs only in ModelData.get_DC'","'source_gray_cells':('Inferred numeric gray fractions in this variant; original source markers retained in the parent model' if 'gray_fit' in model.name else 'Preserved as -9999; zero conversion occurs only in ModelData.get_DC')")
 (d/'run_sppr.py').write_text(helper,encoding='utf-8')
 if not (d/'README.md').exists():(d/'README.md').write_text('# Source-only direct diagnosis\n\nThe exact source JSON loads, but construction is blocked by absent native multi-detritus fate. GE, TE and With Egestion are NOT_RUN. The exception and actual settings remain in diagnostic_manifest.json. `python run_sppr.py` reproduces that admission outcome using a scientific Python environment with numpy, pandas, scipy, sympy, igraph and tqdm. It never invents fate.\n',encoding='utf-8')
 # Remove stale inherited conversion/reconstruction evidence now superseded by
 # the exact current reconstruction and source/variant audit.
 obsolete=[p for p in e.glob('*_reconstructed.xlsx')]
 if fit:obsolete.extend(e/n for n in ['MASS_BALANCE.md','DIET_SOURCE_SUMS.json','ewe_conversion.log'] if (e/n).exists())
 for p in obsolete:
  assert p.resolve().is_relative_to(m.resolve()) and p.is_file() and not p.is_symlink();oldhash=sha(p);p.unlink();dispositions.append([p.relative_to(ROOT).as_posix(),'',oldhash,'','removal','Redundant or inherited parent-only check superseded by current variant reconstruction, CURRENT_VARIANT_CHECK and all-group runtime balances','EEZ_939',m.name,RUN])
 # Additional context is documentary; weights, classifications and arithmetic stay fixed.
 if full:
  v=m/'model_validation';ve=v/'evidence';review=load(ve/'review_checks.json');review['all_12_report_pages_visually_inspected_in_run']=True;review['appendix_views_visually_inspected']=['top rows','long split rows','Sources hyperlinks'];dump(ve/'review_checks.json',review)
  allocations=load(ve/'allocation_assumptions.json')
  for row in allocations:
   row['target_catch_basis']='2019 landings';row['source_proxy_basis']='published total removals (landings plus discards)' if row['source_catch_usable'] else 'published model biomass'
   row['basis_transfer_assumption']='When total-removal catch proportions are used, their composition is assumed applicable to landings. Biomass proportions instead assume comparable catchability. Neither is observed target catch composition.'
  dump(ve/'allocation_assumptions.json',allocations)
  for name in ['template_fidelity.json']:
   shutil.copy2(v/'work'/RUN/'qa'/name,ve/name)
  # A portable structural distillation replaces its temporary machine-specific path.
  text=(v/'work'/RUN/'inputs/artifact.md').read_text(encoding='utf-8');text=text.replace((ROOT/'tools/templates/validation.docx').as_posix(),rel(ROOT/'tools/templates/validation.docx',ve));(ve/'template_contract.md').write_text(text,encoding='utf-8')
  comparison=[]
  for sibling in sorted(BASE.glob(f'Corrales_2017_ICS_{period}*')):
   sd=load(sibling/'results/diagnostics/diagnostic_manifest.json')
   for method,record in sd['methods'].items():
    diag=record.get('diagnostics',{});mi=diag.get('model_input',{});balance=diag.get('balance',{})
    comparison.append({'model_id':sibling.name,'method':method,'outcome':diag.get('status',record.get('status')),'max_production_relative_residual':mi.get('p_max_rel_residual'),'max_consumption_relative_residual':mi.get('q_max_rel_residual'),'strict_mass_balance':mi.get('is_model_balanced'),'runtime_total_catch_t_per_km2_yr':mi.get('total_catch'),'PP_budget_relative_gap':balance.get('rel_gap'),'strict_PP_budget_balance':balance.get('is_balanced')})
  with (ve/'reconstruction_comparison.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
 # Bind the inventory to current artifacts. Data hash-checking remains independent
 # of scientific balance and reviewer approval.
 dest=(m/'model_validation/evidence') if full else e;artifacts=[];required=[]
 def present(role,p,required_role=False):
  assert p.is_file(),p;artifacts.append({'role':role,'path':rel(p,dest),'sha256':sha(p),'availability':'present'})
  if required_role:required.append(role)
 present('source_article',PAPER/'sources/1-s2.0-S0924796316302329-main.pdf',True);present('source_supplement',PAPER/'sources/supplements/1-s2.0-S0924796316302329-mmc1.docx',True);present('source_manifest',PAPER/'source_manifest.json',True);present('canonical_model',m/'model.json',True);present('departure_notes',m/'model_notes.md',True)
 for name in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx','Taxonomy.xlsx']:present('extraction_'+name,m/'extracted_tables'/name,True)
 for p in (m/'extracted_tables/companions').iterdir():
  if p.is_file():present('published_companion_'+p.name,p)
 for name in ['REPORT.md','CURRENT_VARIANT_CHECK.json','SOURCE_FIDELITY_CHECK.json','reconstructed.xlsx','registry_receipt.json']:present('evidence_'+name,e/name,True)
 present('diagnostic_manifest',d/'diagnostic_manifest.json',True);present('method_contract',d/'method_contract.json',True);present('diagnostic_reproducer',d/'run_sppr.py',True)
 current=load(d/'diagnostic_manifest.json');methods=list(current['methods']);successful=current.get('constructor_outcome',current.get('constructor'))=='passed'
 if successful:
  for method in methods:present('full_return_'+method,d/(method.replace(' ','_')+'_full_return.json'),True)
  for name in ['loaded_before.json','runtime_state.json','runtime_transformations.json','mass_balance_by_group.csv','group_sppr.csv','matrix_verification.json','negative_entries_all_matrices.json']:present('diagnostic_'+name,d/name,True)
 else:
  for method in methods:artifacts.append({'role':'full_return_'+method,'availability':'inapplicable','reason':current['exception'],'acquisition_status':'Construction attempted and failed; method was not executed'})
 for name in ['source_identity_bridge.json','diagnostic_documentation.json']:
  if (d/name).exists():present('annotation_'+name,d/name)
 if fit:
  for p in (e/'gray_diet_fit').rglob('*'):
   if p.is_file():present('fit_'+rel(p,e/'gray_diet_fit'),p)
  present('fit_feasibility',e/'gray_diet_fit/fit_summary.json',True)
 if full:
  present('validation_report',m/'model_validation/validation.docx',True);present('taxon_appendix',m/'model_validation/taxon_mapping.xlsx',True)
  for p in dest.iterdir():
   if p.is_file() and p.name not in ['evidence_index.json','completeness.json']:present('validation_evidence_'+p.name,p,p.name in ['mapping_handoff.json','allocation_assumptions.json','region_context.json','geography_review.json','region_boundary.geojson','region_boundary.png','study_figure.jpg','review_checks.json','render_verification.json'])
 unavailable=[{'role':'native_EwE_database','availability':'missing','reason':'No verified native export for the two exact periods found in the bounded source recovery','acquisition_status':'Researcher supplied PDF and author DOCX; accepted version and catalogue search did not recover a native file'},{'role':'researcher_signoff','availability':'inapplicable','reason':'Report is an unsigned candidate review; no human verdict or selection supplied','acquisition_status':'No approval inferred'},{'role':'regional_annual_adoption','availability':'inapplicable','reason':'No model selection/mapping adoption; strict mass balance remains false','acquisition_status':'Not executed'},{'role':'conditional_detritus_fallbacks','availability':'inapplicable','reason':'Researcher required a mass-balanced model before these alternatives; strict mass balance is false','acquisition_status':'Deferred under explicit condition'}]
 artifacts.extend(unavailable)
 index={'schema_version':1,'run_id':RUN,'region_id':'EEZ_939','model_id':m.name,'variant_id':m.name,'source_identity':{'doi':manifest['doi'],'source_sha256s':[x['sha256'] for x in manifest['files']]},'computational_input_identity':{'current_canonical_sha256':sha(m/'model.json'),'executed_input_sha256':current.get('source_sha256',current.get('input_sha256')),'identity_bridge':'annotation_source_identity_bridge.json' if (d/'source_identity_bridge.json').exists() else None},'methods':methods,'required_roles':required,'artifacts':artifacts,'reconciliation':{'source_bytes_retained':True,'current_import_JSON_roundtrip_and_missing_masks_verified':True,'protected_source_values_and_fitted_departures_verified':True,'diagnostic_admission_and_full_return_inventory_verified':True,**({'saved_matrix_masks_scopes_and_footprints_reconciled':True} if successful else {}),**({'report_appendix_denominators_links_and_visual_checks_verified':True} if full else {})}}
 dump(dest/'evidence_index.json',index)
 checker=ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py';r=subprocess.run([sys.executable,'-X','utf8',str(checker),str(dest/'evidence_index.json'),'--output',str(dest/'completeness.json')],capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr
 assert load(dest/'completeness.json')['complete'];outcomes.append({'model_id':m.name,'inventory_complete':True,'artifact_count':len(artifacts),'scientific_mass_balanced':False,'signed_approval':False});print(m.name,'evidence integrity verified',len(artifacts),'entries',flush=True)
 # Incidental artifact-tool inspection files belong to transient QA, not delivery.
 for p in (m/'model_validation').glob('*.inspect.ndjson'):
  oldhash=sha(p);p.unlink();dispositions.append([p.relative_to(ROOT).as_posix(),'',oldhash,'','removal','Incidental spreadsheet preview inspection output superseded by final review checks','EEZ_939',m.name,RUN])
 # Report work contains only this task's template inventory and renders, all now
 # evidenced by final receipts. Each deletion is bounded and logged.
 report_work=m/'model_validation/work'/RUN
 if report_work.exists():
  resolved=report_work.resolve();assert resolved.is_relative_to(m.resolve()) and resolved.name==RUN
  assert not any(p.is_symlink() or p.is_junction() for p in report_work.rglob('*'))
  for p in report_work.rglob('*'):
   if p.is_file():dispositions.append([p.relative_to(ROOT).as_posix(),'',sha(p),'','removal','Temporary report builder contract or render QA promoted to model evidence; all final pages inspected','EEZ_939',m.name,RUN])
  shutil.rmtree(resolved)
  try:report_work.parent.rmdir()
  except OSError:pass
# Preserve a compact completed handoff receipt in each current report model.
complete={'schema_version':1,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'region_id':'EEZ_939','completed_stages':['Source extraction for two periods','Eight canonical source/authorized experimental variants','Source and current-variant reconstruction checks','Three direct diagnostic methods per constructible candidate; explicit source-only NOT_RUN','Single mapping handoff per period, all 96 taxa','Two Word candidate reports and linked Excel appendices with visual and numerical QA','Serialized narrow paper/model registration and portable evidence checks'],'models':outcomes,'regional_inputs_selection_and_researcher_review_unchanged':True,'scientific_limit':'Strict mass balance remains false in both periods; older F-removal methods WARN, later FAIL. No balanced native model or approved annual PPR claimed.','conditional_fallbacks':'Deferred because the required balanced prerequisite is not met','registry_receipt':'../../extracted_tables/evidence/registry_receipt.json'}
for m in BASE.glob('*F_removals'):dump(m/'model_validation/evidence/handoff_receipt.json',complete)
# The handoff receipt is supplementary and not in the earlier frozen inventories.
# Reindex it and recheck before cleanup of the shared regional task work.
for m in BASE.glob('*F_removals'):
 d=m/'model_validation/evidence';idx=load(d/'evidence_index.json');p=d/'handoff_receipt.json';idx['artifacts'].append({'role':'completed_handoff','path':p.name,'sha256':sha(p),'availability':'present'});dump(d/'evidence_index.json',idx)
 r=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py'),str(d/'evidence_index.json'),'--output',str(d/'completeness.json')],capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stdout
 # Correct the relative registry link from a validation-evidence directory.
 # Receipt content is a context field, not a hyperlink or authority.
assert digest_tables(original_region)==digest_tables(read_book(ROOT/'regions/EEZ/EEZ_939/EEZ_939.xlsx'))
ledger=ROOT/'common_reference_data/provenance/source_paths.csv'
with ledger.open('a',encoding='utf-8',newline='') as f:csv.writer(f,lineterminator='\n').writerows(dispositions)
dump(WORK/'outputs/cleanup_handoff.json',{'schema_version':1,'all_model_inventory_integrity_complete':True,'redundant_files_removed':len(dispositions),'regional_work_can_be_removed_after_unlinking_known_dependency_junction':True})
print('All eight portable inventories complete; source, diagnostics and report restrictions retained.',flush=True)
