"""Independent persisted arithmetic checks and honest regional handoff inventory."""
import pathlib,json,hashlib,math,sys,os,zipfile,urllib.parse,copy,datetime
import numpy as np
from lxml import etree as E
from docx import Document
import openpyxl
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[4];REGION=ROOT/'regions/LME_036';MID='36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,overview,input_hash,sha,validate_region,digest_tables
from regional import result_hash
sys.path.insert(0,str(ROOT/'tools/skills/original_skill_resources/combined-src/scripts'))
from check_evidence import check
save=lambda n,v:(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
load=lambda n:json.loads((HERE/n).read_text(encoding='utf-8'))
bookpath=REGION/'LME_036.xlsx';book=read_book(bookpath);o=overview(book);validate_region(book,bookpath)
audit=load('taxon_audit_adopted.json');summary=load('summary.json');changes=load('mapping_changes.json');disposition=load('proposal_dispositions.json')
assert o['selected_model_id']==MID and o['taxon_detail_year']==2019 and o['catch_basis']=='landings'
assert input_hash(book)==o['calculation_input_sha256'] and result_hash(book)==o['calculation_result_sha256']
catch={(r['taxon'],r['catch_basis']):r for r in records(book,'Catch','Catch')};simple={r['taxon']:r for r in records(book,'Classic PPR','Taxa')}
taxa=sorted({t for t,b in catch});assert len(taxa)==374 and set(taxa)=={r['taxon'] for r in audit}
mapping={r['taxon']:r['adopted_groups'] for r in audit};groupcoeff={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(book,'Selected model groups','Group SPPR')}
taxoncoeff={};num_coeff=0
for r in records(book,'PPR','Taxon SPPR'):
 vals=[groupcoeff.get((g['name'],r['scope'],r['method'])) for g in mapping[r['taxon']]]
 expect=round(math.fsum(g['weight']*v for g,v in zip(mapping[r['taxon']],vals)),6) if all(isinstance(v,(int,float)) and math.isfinite(v) for v in vals) else None
 assert expect==r['sppr'],(r,expect);taxoncoeff[r['taxon'],r['scope'],r['method']]=expect;num_coeff+=1
simple_ppr=[];missing=[]
for r in audit:
 c=catch[r['taxon'],'landings'][2019];sp=simple.get(r['taxon'],{}).get('sppr')
 if sp is None:missing.append(r['taxon']);assert c==0;v=0.0
 else:v=c*sp/9
 assert math.isclose(c,r['catch_t'],rel_tol=1e-12,abs_tol=1e-12)
 assert math.isclose(v,r['ppr_tC'],rel_tol=1e-12,abs_tol=1e-9),(r['taxon'],v,r['ppr_tC'])
 simple_ppr.append(v)
assert len(missing)==34 and math.isclose(math.fsum(simple_ppr),summary['ppr_tC'],rel_tol=1e-14)
assert all(math.isclose(math.fsum(g['weight'] for g in r['adopted_groups']),1.0,abs_tol=1e-12) for r in audit)
rank=['Unresolved','Very low','Low','Medium','High']
assert all(r['review_confidence']==min([r['membership_confidence'],r['weight_confidence']],key=rank.index) for r in audit)
for k in ['membership_rules','weight_rules']:assert math.isclose(math.fsum(r['PPR percentage'] for r in summary[k]),100.0,abs_tol=1e-12)
years=list(range(1950,2020));annual={};annual_cells=0;annual_max_rel=0.
for r in records(book,'PPR','Annual'):
 if r['metric']!='ppr':continue
 coeff=[]
 for t in taxa:
  sp=taxoncoeff[t,r['scope'],r['method']]
  if catch[t,r['catch_basis']]['unidentified']:
   if r['unidentified']=='zero':sp=0.0
   elif r['unidentified']=='simple':sp=simple.get(t,{}).get('sppr')
  coeff.append(np.nan if sp is None else sp)
 cm=np.array([[catch[t,r['catch_basis']][y] for y in years] for t in taxa],dtype=float)
 expected=np.nansum(cm*np.array(coeff)[:,None],axis=0)
 for y,v in zip(years,expected):
  stored=r[y]
  if stored is None:continue
  assert math.isclose(float(v),stored,rel_tol=2e-12,abs_tol=1e-8),(r['scope'],r['method'],r['catch_basis'],r['unidentified'],y,v,stored)
  annual_cells+=1;annual_max_rel=max(annual_max_rel,abs(float(v)-stored)/max(abs(stored),1.0))
 annual[r['scope'],r['method'],r['catch_basis'],r['unidentified']]=r
npp={r['method']:r for r in records(book,'NPP','NPP')};ratio_cells=0
for r in records(book,'PPR–NPP','Ratios'):
 if not r['model_id']:continue
 a=annual[r['scope'],r['method'],r['catch_basis'],r['unidentified']];n=npp[r['npp_method']]
 for y in years:
  if r[y] is None:continue
  expected=100*(a[y]/9)/n[y]
  assert math.isclose(expected,r[y],rel_tol=2e-12,abs_tol=1e-12);ratio_cells+=1
save('numeric_verification.json',{'region_validation_passed':True,'input_and_result_hashes_current':True,'taxa':374,'matching_candidates':sum(len(r['adopted_groups']) for r in audit),'taxon_coefficients_verified':num_coeff,'all_years_annual_ppr_cells_independently_verified':annual_cells,'maximum_annual_relative_round_trip_difference':annual_max_rel,'model_ratio_cells_verified':ratio_cells,'carbon_divisor_applied_once':9,'independent_simple_chain_tC':math.fsum(simple_ppr),'independent_simple_chain_denominator_is_entire_known_universe':True,'missing_coefficient_taxa':missing,'all_missing_coefficients_have_zero_2019_landings':True,'unknown_coefficients_preserved':True,'confidence_is_weakest_required_component':True,'both_rule_tables_partition_same_entire_PPR_once':True,'model_historical_sensitivity_bounds_invalidated':True})

# Verify stored report links and spelling, plus absence of machine HyperlinkBase.
docpath=REGION/f'Model_validation_{MID}.docx';doc=Document(docpath);W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';wn=lambda x:'{'+W+'}'+x
links=[]
for hl in doc._element.iter(wn('hyperlink')):
 rid=hl.get('{'+R+'}id');target=doc.part.rels[rid].target_ref if rid else None
 if target and not target.startswith(('http://','https://')):
  clean=urllib.parse.unquote(target).split('#')[0];assert not pathlib.PureWindowsPath(clean).is_absolute() and (docpath.parent/clean).exists(),target
 for run in hl.iter(wn('r')):
  rp=run.find(wn('rPr'));assert rp is not None and rp.find(wn('color')).get(wn('val'))=='0563C1' and rp.find(wn('u')).get(wn('val'))=='single'
 links.append({'text':''.join(hl.itertext()),'target':target})
with zipfile.ZipFile(docpath) as z:
 for n in z.namelist():
  if n.startswith('docProps/') and n.endswith('.xml'):
   tree=E.fromstring(z.read(n));assert not any((e.text or '').strip() for e in tree.iter() if E.QName(e).localname=='HyperlinkBase')
save('report_link_checks.json',{'hyperlinks':links,'all_local_targets_resolve_relative_to_document':True,'all_hyperlink_runs_explicitly_blue_and_underlined':True,'no_absolute_hyperlink_base':True,'report_status':'pending alignment draft until coordinator verifies current shared outputs'})

limitations=[
 {'issue':'Final benthopelagic pool scope','evidence':'Cheung Appendix 6.1 distinguishes small and large benthopelagic species; final 2000s table has one group 27 whose rates resemble the small component. The source does not document a merger.','treatment':'Retain group 27 extensions at Low confidence and explicit ambiguity; do not invent a merger or repair parameters.'},
 {'issue':'Geographic and temporal extrapolation','evidence':'Northern-shelf 2000s source applied to whole LME1950–2019. Visual A overlap/region about15–25%; B overlap/study about90–100%, without polygon measurement.','treatment':'Provisional ecological applicability; fixed source guild catch proxies do not establish annual target-label composition.'},
 {'issue':'Broad ranks and ecology','evidence':'Regional representatives support M9 candidate sets, not exhaustive global family membership. 42 proposals lack sufficient replacement set, reporting exclusions or length-metric/habitat resolution.','treatment':'36 individual corrections; 42 retained with precise source evidence; 57 Low and 10 Very low remain.'},
 {'issue':'Target-label allocation evidence unavailable','evidence':'Retained stage searches plus primary northern-SCS survey/catch-report searches did not recover wet-mass composition applying to the exact target labels and operative boundaries.','treatment':'All185 splits use complete reported model catches as assumed Medium W4; source catches precede any biomass fallback. Separate identified congener catches are not silently target-label observations.'},
 {'issue':'Accepted source and runtime differences','evidence':'Diet rounding/accepted normalization, default GS0.2, LIM-completed BA, source table/appendix conflicts and source group label mojibake are documented in reconstruction.','treatment':'All accepted model JSON, numerical Groups, diet, BA, balancing/routing and runtime conventions preserved. No paper-value repair or blanket encoding replacement.'},
 {'issue':'Researcher exclusion note discrepancy','evidence':'Manual note lists groups34–37 as removed. Saved and reproduced runtime retains all four with finite source-specific SPPR.','treatment':'Preserve manual XML; qualify the distinct configuration in Other. Do not apply exclusions.'},
 {'issue':'Direct diagnostics warnings','evidence':'GE WARN near-zero efficiency in34; TE WARN in34–36. With Egestion OK. All three finite matrices have zero negative SPPR entries; strict input and global SPPR balance flags true.','treatment':'Warnings remain scientific concerns; round-trip-scale coefficient differences do not justify replacing accepted Group SPPR.'},
 {'issue':'Historical source evidence and shared alignment','evidence':'Prior confidence-only index has stale hashes and prior sensitivity evidence predates the adopted candidate changes. Shared map/project/trends/archive are coordinator-owned.','treatment':'Retain historical evidence distinctly. Current regional arithmetic is verified, old model sensitivity bounds invalidated; current shared-output/browser/model-switch evidence remains required and pending.'},
]
save('scientific_limitations.json',limitations)
save('search_record.json',{'date':'2026-09-30','prior_search':'Retained confidence_reassessment_20260930 per-taxon sources and stage-composition searches reused where adequate.','new_checks':[
 {'query':'Hilsa kelee maximum length pelagic ecology','url':'https://www.fishbase.se/summary/Hilsa-kelee','material_read':'Species classification, habitat and size account','access':'full retrieved page','applicability':'35cm TL pelagic-neritic excludes <=30cm class','decision':'adopt large-pelagic pair'},
 {'query':'Decapterus maruadsi observed maximum length Ohshimo 2006 Uehara 2021 Table3','url':'https://www.jstage.jst.go.jp/article/jsfo/85/3/85_153/_pdf','material_read':'Primary comparative Table3 printedp160, observed35.4cm from Ohshimo2006; original abstract FL-asymptote342mm considered separately','access':'indexed full PDF text; original growth-paper abstract','applicability':'Observed fork length above30 excludes small TL class; mediated observed-record citation disclosed','decision':'adopt M5 Medium large-pelagic pair'},
 {'query':'Psettodidae Western Central Pacific family species maximum length','url':'https://www.fao.org/docrep/pdf/009/y0870e/y0870e43.pdf','material_read':'Regional family account printed3792–3793','access':'full PDF text','applicability':'One regional Psettodes erumei maximum60TL bottom habitat','decision':'prune small group24 and retain25/26'},
 {'query':'Northern South China Sea regional fish catch composition stages demersal 30cm pelagic taxon landings','url':'https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.809636/full','material_read':'Primary northern continental slope survey scope2015/17/18 and252fish inventory','access':'retrieved article','applicability':'Local deep-bottom trawl survey differs in gear/period/area/reporting label; cannot supply exact 2019 whole-LME target-label/stanza wet-mass shares','decision':'reject as direct allocation; retain complete modelcatch proxy'},
 {'query':'Eastern Guangdong South China Sea nekton119 species2026 catch composition','url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC13203370/','material_read':'Primary survey scope19 bottom-trawl stations119nekton','access':'retrieved article','applicability':'Local gear-specific survey not exact residual target-label composition for accepted fixed model','decision':'no direct allocation adoption'},
],'weight_hierarchy_outcome':'Complete source reported catch verified for every split, including real zeros. No biomass fallback or W11 needed. No identified-congener catch proxy used.'})

# Snapshot current local evidence; shared alignment roles remain genuinely
# missing here until the coordinator produces and verifies their current state.
artifacts=[]
def present(role,p):
 p=pathlib.Path(p);assert p.is_file(),p
 artifacts.append({'role':role,'path':os.path.relpath(p,HERE).replace('\\','/'),'sha256':sha(p),'availability':'present'})
for role,p in [
 ('source_model',REGION/'models'/MID/'model.json'),('saved_group_sppr',REGION/'models'/MID/'sppr_source.xlsx'),('source_pdf',REGION/'papers/SCS-2007/ubc_2007-317501-87ea9ea0.pdf'),('source_definitions',HERE.parent/'confidence_reassessment_20260930/source_group_definitions.txt'),('source_catch_reconstruction',HERE.parent/'source/reconstruction_2000s/SOURCE_CATCH_TOTALS.json'),('baseline_region',HERE/'baseline_LME_036.xlsx'),('baseline_report',HERE/('baseline_'+docpath.name)),('baseline_appendix',HERE/'baseline_LME036_taxon_mapping_appendix.xlsx'),('adopted_region',bookpath),('report',docpath),('appendix',REGION/'LME036_taxon_mapping_appendix.xlsx'),('guide',ROOT/'tools/templates/Model_validation_template_instructions.md'),('skill',ROOT/'tools/skills/ecopath-model-validation/SKILL.md'),('evidence_contract',ROOT/'tools/skills/original_skill_resources/combined-src/references/evidence-handoff.md'),('mapping_audit',HERE/'taxon_audit_adopted.json'),('weight_audit',HERE/'allocation_audit.json'),('proposal_dispositions',HERE/'proposal_dispositions.json'),('adopted_changes',HERE/'mapping_changes.json'),('summary',HERE/'summary.json'),('adoption_checks',HERE/'adoption_checks.json'),('numeric_checks',HERE/'numeric_verification.json'),('artifact_checks',HERE/'artifact_edit_checks.json'),('report_links',HERE/'report_link_checks.json'),('appendix_links',HERE/'appendix_links.json'),('scientific_limitations',HERE/'scientific_limitations.json'),('search_record',HERE/'search_record.json'),('dependent_effects',HERE/'dependent_result_changes.json'),('prior_full_taxon_audit',HERE.parent/'confidence_reassessment_20260930/taxon_audit_adopted.json'),('geography_evidence',HERE.parent/'coverage_geography_test_note.md')]:present(role,p)
for p in sorted((HERE/'direct_diagnostics').iterdir()):
 if p.is_file():present('direct_diagnostic_evidence',p)
present('visual_checks',HERE/'visual_checks.json')
for p in sorted((HERE/'render').iterdir()):
 if p.is_file():present('visual_render',p)
required=sorted(set(a['role'] for a in artifacts)|set(['project_alignment','map_alignment','trends_alignment','archive_alignment','browser_controls','model_switch_current']))
for role in ['project_alignment','map_alignment','trends_alignment','archive_alignment','browser_controls','model_switch_current']:
 artifacts.append({'role':role,'availability':'missing','reason':'Required current shared integration and visible browser verification belongs to the coordinator after this regional handoff; prior dated evidence cannot prove alignment with the36adopted changes.','acquisition_status':'pending coordinator integration; not inapplicable'})
index={'schema_version':1,'run_id':'selected_regions_review_20260930','region_id':'LME_036','model_id':MID,'variant_id':'accepted selected2000s parameters; supported mapping adoption; default2019landings','source_identity':{'model_sha256':sha(REGION/'models'/MID/'model.json'),'source_pdf_sha256':sha(REGION/'papers/SCS-2007/ubc_2007-317501-87ea9ea0.pdf')},'computational_input_identity':{'region_sha256':sha(bookpath),'input_sha256':input_hash(book),'result_sha256':result_hash(book),'direct_settings_identity':'direct_diagnostics/complete_input_identity.json'},'methods':['all374prior taxonomy review reused and affected evidence revisited','78individual proposal decisions','complete source catch allocation audit','fresh direct GE','fresh direct TE','fresh direct With Egestion','dependent arithmetic from unchanged saved coefficients','manual-preserving report and appendix update'],'required_roles':required,'artifacts':artifacts,'reconciliation':{'all_proposals_disposed':len(disposition)==78,'weakest_confidence_verified':True,'protected_parameters_preserved':load('adoption_checks.json')['protected_tables_preserved'],'independent_arithmetic_verified':True,'portable_styled_links_verified':True},'shared_completion_pending':True,'historical_index_policy':'Original dated confidence-only index and earlier snapshots retained unchanged; current handoff does not claim their stale hashes represent current outputs.'}
save('evidence_index.json',index);complete=check(HERE/'evidence_index.json');save('completeness.json',complete)
assert not complete['errors'] and set(complete['missing_roles'])==set(['project_alignment','map_alignment','trends_alignment','archive_alignment','browser_controls','model_switch_current'])
print(json.dumps({'numeric_cells':annual_cells,'ratio_cells':ratio_cells,'current_index_integrity_errors':complete['errors'],'pending_shared_roles':complete['missing_roles']},ensure_ascii=True))
