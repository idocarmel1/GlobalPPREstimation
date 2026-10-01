from pathlib import Path
import json,sys,hashlib,zipfile,re,copy,collections,os
from lxml import etree
ROOT=Path.cwd();Q=Path(__file__).parent;R=ROOT/'regions/LME_047';MID='47_2_East_China_Sea_(2018)';O=R/'validation_reports'/MID
sys.path.insert(0,str(ROOT/'tools'));from workbooks import *
from regional import result_hash,set_setting
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def j(n):return json.loads((O/n).read_text(encoding='utf-8'))
b=read_book(R/'LME_047.xlsx');validate_region(b,R/'LME_047.xlsx',require_fresh=True);assert result_hash(b)==overview(b)['calculation_result_sha256']
a=j('coverage_summary.json');geo=j('geography/geographic_assessment.json');snap=Q.parent.parent/'central_source_metadata_current.json';s=json.loads(snap.read_text(encoding='utf-8'));assert s['project_sha256']==sha(ROOT/'Project.xlsx')
proposals=[]
def propose(table,key,field,value,reason):
 rows=s['tables'][table];r=next(x for x in rows if all(x.get(k)==v for k,v in key.items()));old=r.get(field)
 if old!=value:proposals.append({'sheet':table,'table':table,'key':key,'field':field,'expected_old':old,'proposed':value,'reason':reason})
mk={'unit_id':'LME_047','model_id':MID};pk={'article_id':'ECS-2022__LME_047','unit_id':'LME_047'}
reason='Exact selected M2018 source/mapping/diagnostic/geography review; retains scores/retrieval history/selection/production eligibility and all accepted parameters. Approximate study footprint is not an exact native model boundary or PPR multiplier.'
coverage=f"Figure1study/survey footprint reconstructed from native graticule: A≈{geo['A_percent']:.8f}%target, B≈100%study (descriptive10–15%/90–100%). Source joint autumn2018/spring2019survey; exact native model boundary/area not supplied. Whole-LME transfer is unverified. See regions/LME_047/validation_reports/{MID}/geography/geographic_assessment.json."
availability=f"Selected accepted M2018 reconstruction; all276catchlabels reviewed,0unresolved;12complete positive2018S4catch proxies and15complete source-biomass fallback splits, allocationMedium. GE/TE/WithEgestionWARN, strict input/budget balance true, EE0Sharks22/Mammals23 and unverified canonicalexport0catch retained. Production eligibility preserved; no scientific approval. Evidence regions/LME_047/validation_reports/{MID}/coordination_handoff.json"
for field,val in {'model_year':2018,'publication_year':2022,'model_years':'2018–2019 survey; static M2018','variant':'static M2018 accepted reconstruction','availability':availability,'coverage_class':'localized_study','target_coverage_ratio':geo['A_percent']/100,'coverage_note':coverage,'doi':'10.3389/fmars.2022.865645'}.items():propose('Models & coverage',mk,field,val,reason)
for field,val in {'functionalgroups':24,'model_years':'Static M1997 (1997–2000 survey), M2018 (2018–2019 survey); M1997 Ecosim2000–2018','coverage_class':'localized_study','target_coverage_ratio':geo['A_percent']/100,'geometry_method':'Approximate native Figure1study hatch traced with original graticule, preserved offshore coastal gap/ordered bends, NaturalEarth1:50million consistent land mask, WGS84areas and8water controls; exact native model boundary unstated','geometry_confidence':'low','geometry_note':coverage,'full_model_loadable':'Accepted reconstructed M2018 JSON load-tested at exact settings; no native EwE export; source catch placeholders/defaults and accounting assumptions remain','extraction_readiness':'Core B/PB/QB/EE and normalized S3diet verified; native catch/GS/migration/accumulation/routing export incomplete. Source reconstruction and qualified sourcecatch/biomass allocation proxies documented','loadability_class':'C — accepted reconstruction load-tested; native full model inputs/export unavailable','recommendation':'Recent selected M2018 source with explicit supplementary composition; localized study transfer and source/default limits remain. Reviewed conditional PPR available, not scientific model approval.'}.items():
 # Source table uses functional_groups, not a prose alias.
 actual='functional_groups'if field=='functionalgroups'else field;propose('Papers',pk,actual,val,reason)
foot=j('geography/study_area_reconstructed.geojson');oldfoot=R/'papers/ECS-2022/footprint.geojson';rootproof=ROOT/'original_research_archive/research/selected_regions_validation_20260930/verification/LME_047_geography_coordinator_review.json'
save('shared_metadata_proposals.json',{'authenticated_project_sha256':s['project_sha256'],'authenticated_snapshot_sha256':sha(snap),'source_proposals':proposals,'geometry_proposals':[{'operation':'replace_article_footprint','article_id':'ECS-2022__LME_047','unit_id':'LME_047','footprint_key':'ECS-2022_a5fc1cd8c9ce','expected_old_footprint_file':oldfoot.relative_to(ROOT).as_posix(),'expected_old_file_sha256':sha(oldfoot),'expected_old_geometry':json.loads(oldfoot.read_text(encoding='utf-8'))['geometry'],'proposed_feature':foot,'proposed_file':(O/'geography/study_area_reconstructed.geojson').relative_to(ROOT).as_posix(),'root_independent_geography_proof':rootproof.relative_to(ROOT).as_posix(),'reason':reason}],'protected_historical_fields':['all scores/caps','downloaded_file_count','download_attempt_count','download_attempt_summary','scientific selection/canonical/runtime/coefficients','production_eligible'],'shared_integration':'pending root; authenticate latest Project and keyed fields before apply'})
# Fresh-process canonical reader/validator proof plus ascending unique XML addresses.
ordering=[]
for p in [R/'LME_047.xlsx',R/'LME047_taxon_mapping_appendix.xlsx']:
 with zipfile.ZipFile(p)as z:
  for n in z.namelist():
   if not re.fullmatch(r'xl/worksheets/sheet\d+\.xml',n):continue
   d=etree.fromstring(z.read(n));ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};last=0;count=0
   for row in d.findall('s:sheetData/s:row',ns):
    y=int(row.get('r'));assert y>last;last=y;cols=[]
    for c in row.findall('s:c',ns):
     ref=c.get('r');m=re.fullmatch(r'([A-Z]+)(\d+)',ref);assert int(m[2])==y;v=0
     for ch in m[1]:v=v*26+ord(ch)-64
     cols.append(v);count+=1
    assert cols==sorted(set(cols)),(p.name,n,y)
   ordering.append({'file':p.name,'worksheet_xml':n,'cell_count':count,'ascending_unique':True})
save('canonical_final_verification.json',{'fresh_unmodified_reader':True,'validate_region_passed':True,'workbook_sha256':sha(R/'LME_047.xlsx'),'input_hash':input_hash(b),'result_hash':result_hash(b),'stored_result_hash':overview(b)['calculation_result_sha256'],'stored_input_hash':overview(b)['calculation_input_sha256'],'selected_model_sha256':sha(R/overview(b)['model_path']),'ascending_unique_xml':ordering})
methods=j('method_contribution_exposure.json')['methods'];control={'region_id':'LME_047','year':2019,'catch_basis':'landings','units':'tonnes C','scope':'all','unidentified':'method','taxon_filter':'all276labels','group_filter':'allreviewedgroups','missing_policy':'positive catch missing coefficient unknown; missing coefficient at zero catch contributes0'}
save('expected_integrated_ui.json',{'shared_integration':'pending root; workbook arithmetic is not browser verification','controls':control,'classic_PPR_unrounded_tC':a['total_simple_chain_ppr_tC'],'classic_PPR_visible_2decimals':f"{a['total_simple_chain_ppr_tC']:,.2f}",'reference_catch_t':a['total_landings_t'],'method_unrounded_tC':{x['method']:x['total_tC']for x in methods if x['scope']=='all'},'production_eligible':overview(b)['production_eligible'],'diagnostic_grades':{'GE':'WARN','TE':'WARN','With Egestion':'WARN'},'report_coverage_ranges':{'A':'10–15%','B':'90–100%'},'exact_approximate_study_coverage_A_percent':geo['A_percent'],'model_boundary_unverified':True})
lines=['# East China Sea retained evidence','',f'Selected model `{MID}`. Shared metadata/global payload/browser/graph/Git integration remains pending root.','']
for p in sorted(O.rglob('*')):
 if p.is_file()and p.name not in ['reports_index.md','coordination_handoff.json']:lines.append(f'- [{p.relative_to(O).as_posix()}](<{p.relative_to(O).as_posix()}>)')
(O/'reports_index.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('FINAL CANONICAL',sha(R/'LME_047.xlsx'),len(proposals))
