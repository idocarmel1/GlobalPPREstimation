"""Serialize reviewed metadata and regional outputs, preserving unrelated records."""
from pathlib import Path
import copy, json, math, shutil, sys, zipfile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'central_sync_20260928'
OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,write_book,records,sha,finite
import update_project
def load(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
path=ROOT/'Project.xlsx'; initial=sha(path)
print('Reading current central workbook',flush=True)
before=read_book(path); after=copy.deepcopy(before)
backup=OUT/f'Project_before_{initial[:12]}.xlsx'
if not backup.exists():shutil.copy2(path,backup)
assert sha(backup)==initial
changes=[]
def upsert(sheet,table,key,patch):
    h,rr=after[sheet][table]
    assert set(patch)<=set(h),set(patch)-set(h)
    matches=[r for r in rr if all(r[h.index(k)]==v for k,v in key.items())]
    assert len(matches)<=1,(sheet,key)
    if matches:r=matches[0]
    else:r=[None]*len(h);rr.append(r)
    old=dict(zip(h,r))
    for k,v in {**key,**patch}.items():r[h.index(k)]=v
    changes.append({'sheet':sheet,'key':key,'fields':{k:{'before':old.get(k),'after':v} for k,v in patch.items() if old.get(k)!=v}})
def paper(uid,aid,patch):upsert('Papers','Papers',{'unit_id':uid,'article_id':aid},patch)
def model(d):upsert('Models & coverage','Models',{'unit_id':d['unit_id'],'model_id':d['model_id']},d)
def known(sheet,table,d):return {k:v for k,v in d.items() if k in after[sheet][table][0]}

p=load('regions/LME_014/models/PAT2024_FalklandShelf_2020_native/selection_20260928/central_registration_proposal.json')
for m in p['models_to_upsert']:model(m)
for x in p['paper_field_updates']:paper('LME_014',x['article_id'],x['fields'])
p=load('regions/LME_050/models/extraction_review_20260928/SELECTED_CENTRAL_REGISTRATION_PROPOSAL.json')
paper('LME_050',p['paper_existing_key']['article_id'],p['paper_fields_to_update'])
for m in p['models_to_append']:model(m)
p=load('regions/LME_003/models/CAL-2016_California_Current_2000-2014/selected_pipeline/central_registration_proposal.json')
aid='CAL-2016__LME_003'
paper('LME_003',aid,{'title':p['title'],'publication_year':2016,'doi':p['doi'],'model_years':p['model_years'],'functional_groups':93,'selected':True,'extraction_readiness':p['extraction_status'],'full_model_loadable':p['diagnostic_status'],'notes':p['notes'],'loadability_evidence':p['regional_report'],'coverage_note':p['coverage_evidence'],'target_coverage_ratio':None})
model({'unit_id':'LME_003','model_id':p['model_id'],'model_path':'regions/LME_003/'+p['selected_runtime_path'],'selected':True,'selection_rationale':p['selection_rationale'],'paper_ids':aid,'model_year':'2000-2014','model_years':'2000-2014','publication_year':2016,'model_area_km2':302000,'doi':p['doi'],'coverage_class':'subregional','target_coverage_ratio':None,'coverage_note':p['coverage_evidence']+'; 2019 mapped-catch support 76.5112%; historical 78.8497%.','availability':p['diagnostic_status']+'; selected mapped-catch partial calculations','variant':'Source-faithful canonical retained; selected audited B/EE runtime completion with GS and detritus assumptions'})
p=load('regions/LME_024/models/extraction_review_20260928/central_registration_proposal.json')
p['paper_updates']['notes']='Authorized normalized-diet/two-pool return experiment separately completed: GE FAIL, With Egestion FAIL, TE unsupported positive return. Printed accumulation retained; source canonical unchanged. See regions/LME_024/models/extraction_review_20260928/authorized_routing_experiment/REPORT.md. No model selected.'
paper('LME_024',p['paper_key']['article_id'],p['paper_updates']);model(p['model_row'])
for uid in ['LME_026','LME_029']:
    p=load(f'regions/{uid}/extraction_review_20260928/central_metadata_proposal.json')
    for r in p.get('paper_patches',p.get('paper_updates',[])):
        fields=known('Papers','Papers',r)
        if 'extraction_status' in r:fields['extraction_readiness']=r['extraction_status']
        if 'report_path' in r:fields['loadability_evidence']=r['report_path']
        if 'coverage_basis' in r:fields['coverage_note']=r['coverage_basis'];fields['target_coverage_ratio']=None
        paper(uid,r['article_id'],fields)
    for r in p['models_to_upsert']:
        d=known('Models & coverage','Models',r)
        d.update(paper_ids=r['article_id'],availability=r.get('sppr_status',r.get('status')),coverage_note=r.get('coverage_basis',r.get('notes')),variant=r.get('notes'),model_years=str(r['model_year']),target_coverage_ratio=None)
        d['model_path']=d['model_path'].replace('\\','/')
        pr=next(x for x in records(after,'Papers','Papers') if x['article_id']==r['article_id'])
        d.update(publication_year=pr.get('publication_year'),doi=pr.get('doi'))
        if uid=='LME_029':d['model_area_km2']=220000
        model(d)

selected='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
spatial=load('original_research_archive/research/warm_pool_candidate_review_20260928/SPATIAL_OVERLAP.json')
for uid in ['HS_071','EEZ_941','EEZ_598']:
    prov=load(f'regions/{uid}/models/{selected}/SELECTION_AND_PROVENANCE.json')
    aid='WCP-2007__'+uid
    candidates=[r for r in records(after,'Papers','Papers') if r['article_id']==aid]
    if not candidates:
        source=next(r for r in records(after,'Papers','Papers') if r['article_id']=='WCP-2007__EEZ_941')
        source=copy.deepcopy(source);source.update(unit_id=uid,article_id=aid,region_dir=f'regions/{uid}',region_name=None,region_rank=None,atlas_region_rank=None)
        paper(uid,aid,source)
    paper(uid,aid,{'selected':True,'recommendation':prov['rationale'],'notes':prov['rationale'],'loadability_evidence':f'regions/{uid}/models/{selected}/SELECTION_REPORT.md'})
    model({'unit_id':uid,'model_id':selected,'model_path':f'regions/{uid}/models/{selected}/model.json','selected':True,'selection_rationale':prov['rationale'],'paper_ids':aid,'model_year':'mixed periods','model_years':'mixed periods; see original WCP-2007 provenance','publication_year':2007,'model_area_km2':26964000,'coverage_class':'basin_proxy','target_coverage_ratio':spatial['domains']['WCP2007']['overlap'][uid]['percent_target_region_covered']/100,'coverage_note':'Study rectangle intersection with regional polygon; pelagic proxy, not catch coverage. Exact source and edited juvenile rows documented in SELECTION_AND_PROVENANCE.json.','availability':'Selected adopted option1 D_fixed_M0; GE/TE/With Egestion WARN; regional calculations pending','variant':'User-adopted juvenile PB/EE adjustment preserving other-mortality flows'})
    meta=load(f'regions/{uid}/papers/Griffiths-2019/metadata.json')
    fields=known('Papers','Papers',meta)
    fields.update(article_dir=f'regions/{uid}/papers/Griffiths-2019',region_dir=f'regions/{uid}',notes=meta['investigation_note'],recommendation='Deferred investigation requested by user; WCP-2007 option1 selected.',loadability_evidence=f'regions/{uid}/papers/Griffiths-2019/LATER_INVESTIGATION.md')
    paper(uid,meta['article_id'],fields)
    for mid,pooled in [('941_201901_Warm_Pool_(2005)',False),('941_20190101_Warm_Pool_Detritus_Pooled_Experiment_(2005)',True)]:
        model({'unit_id':uid,'model_id':mid,'model_path':f'regions/{uid}/models/{mid}/model.json','selected':False,'selection_rationale':'User retained for later failure investigation; not selected.','paper_ids':meta['article_id'],'model_year':2005,'model_years':'2005','publication_year':2019,'doi':meta['doi'],'model_area_km2':11543000,'target_coverage_ratio':meta['target_coverage_ratio'],'coverage_class':'basin_proxy','coverage_note':meta['geographic_applicability'],'availability':'Deferred investigation: GE/TE/With Egestion FAIL' if pooled else 'Deferred investigation: original two-pool routing blocks loading','variant':'45-group authorized detritus-pooled experiment; source unchanged' if pooled else '46-group source-faithful extraction; unresolved routing and production/catch discrepancies'})

# Generate selected regional outputs against the prepared central metadata in memory.
selected_units={'LME_003','LME_014','LME_050','HS_071','EEZ_941','EEZ_598'}
touched=selected_units|{'LME_024','LME_026','LME_029'}
read_real=update_project.read_book
def read_prepared(p):return after if Path(p).resolve()==path.resolve() else read_real(p)
captured=[]
update_project.read_book=read_prepared
update_project.write_book=lambda p,b:captured.append(b)
print('Consolidating six selected regional workbooks',flush=True)
update_project.update(ROOT,[ROOT/f'regions/{u}/{u}.xlsx' for u in sorted(selected_units)])
assert len(captured)==1;after=captured[0]
# Restore untouched rows and existing alternative-model preference notes.
for sheet,blocks in before.items():
    for table,(h,rr) in blocks.items():
        if 'unit_id' not in h:continue
        nh,nr=after[sheet][table]
        nh=list(h)+[k for k in nh if k not in h]
        oldother=[r for r in records(before,sheet,table) if r.get('unit_id') not in touched]
        local=[r for r in records(after,sheet,table) if r.get('unit_id') in touched]
        after[sheet][table]=(nh,[[r.get(k) for k in nh] for r in oldother+local])
for r in records(after,'Models & coverage','Models'):
    if r.get('unit_id')=='LME_050' and r.get('model_id')=='50_501985_Coastal_Kyoto_Inoue_(1985)':
        model({'unit_id':r['unit_id'],'model_id':r['model_id'],'selection_rationale':'User explicitly retains 1985 as a good comparison model; 2013 selected because newer.'})
    if r.get('unit_id') in {'HS_071','EEZ_941','EEZ_598'} and '201901' in str(r.get('model_id')):
        model({'unit_id':r['unit_id'],'model_id':r['model_id'],'selection_rationale':'User retained for later failure investigation; not selected.'})
(OUT/'planned_metadata_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8')
assert sha(path)==initial,'Concurrent central change; refusing stale write'
print('Writing central workbook once',flush=True)
write_book(path,after)
print('Verifying central readback',flush=True)
check=read_book(path)
def same(a,b):return math.isclose(a,b,rel_tol=2e-15,abs_tol=1e-12) if finite(a) and finite(b) else a==b
for sheet,blocks in before.items():
    for table,(h,rr) in blocks.items():
        if 'unit_id' not in h:continue
        a=[r for r in records(before,sheet,table) if r.get('unit_id') not in touched]
        b=[r for r in records(check,sheet,table) if r.get('unit_id') not in touched]
        assert len(a)==len(b),(sheet,table)
        assert all(all(same(v,y.get(k)) for k,v in x.items()) for x,y in zip(a,b)),(sheet,table)
for sheet,table,keys in [('Papers','Papers',['unit_id','article_id']),('Models & coverage','Models',['unit_id','model_id'])]:
    rr=records(check,sheet,table);ids=[tuple(r.get(k) for k in keys) for r in rr];assert len(ids)==len(set(ids))
    expected=records(after,sheet,table)
    assert len(rr)==len(expected)
    assert all(all(same(v,y.get(k)) for k,v in x.items()) for x,y in zip(expected,rr))
with zipfile.ZipFile(path) as z:
    tables=[n for n in z.namelist() if n.startswith('xl/tables/') and n.endswith('.xml')];assert len(tables)==13
    for n in tables:
        e=ET.fromstring(z.read(n));assert e.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}autoFilter').get('ref')==e.get('ref')
regions=[r for r in records(check,'Regions & status','Regions') if r.get('unit_id') in selected_units]
assert len(regions)==6 and all(r.get('selected_model_id') for r in regions)
for r in regions:assert r['sha256']==sha(ROOT/r['workbook'])
result={'status':'PASS','central_sha256':sha(path),'backup':str(backup.relative_to(ROOT)),'selected_regions':regions,'registered_units':sorted(touched),'metadata_operations':len(changes),'unchanged_unrelated_records':True,'native_tables_and_filters':13,'map':'pending refresh'}
(OUT/'VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'status':'PASS','central_sha256':result['central_sha256'],'selected_regions':sorted(selected_units)},indent=2),flush=True)
