"""Register the actual signed Word review; refresh only its map/trends metadata."""
from pathlib import Path
import copy,datetime,hashlib,json,re,shutil,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from researcher_review import read_report,register_review,approved_review,table_rows
from build_html import refresh_reviews
from workbooks import read_book,overview,records

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def payload(path,var):
    page=path.read_text(encoding='utf-8');start=page.index('const '+var+'=')+len('const '+var+'=')
    return json.JSONDecoder().raw_decode(page,start)[0],page

unit='LME_047';mid='47_2_East_China_Sea_(2018)'
region=ROOT/'regions'/unit;report=region/('Model_validation_'+mid+'.docx');project=ROOT/'Project.xlsx'
name,date,summary=read_report(ROOT,report,mid)
book=read_book(region/(unit+'.xlsx'))
assert overview(book)['selected_model_id']==mid
groups=records(book,'Selected model groups','Groups')
lookup={r['group_name']:int(r['seq']) for r in groups}
assert lookup['Marine mammals']==23 and lookup['Sharks']==22
sppr=summary['sections'][2]['rows'][0]['text']
assert 'Removed groups from calculation:\nMarine mammals (' in sppr
assert 'Kept sharks in PPR calculations' in sppr
excluded=[23]
protected=[region/(unit+'.xlsx'),report,region/'LME047_taxon_mapping_appendix.xlsx',
    region/'models'/mid/'model.json',region/'models'/mid/'sppr_source.xlsx',
    ROOT/'interactive_map/archive/index.html',ROOT/'tools/knowledge_graph/graph.json',
    ROOT/'regions/LME_036/Model_validation_36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s).docx',
    region/'validation_reports/selected_model_validation.ipynb']
protected += list((OUT.parent/'direct_diagnostics').glob('*.json'))
before={p.relative_to(ROOT).as_posix():sha(p) for p in protected}
old_pages={}
for filename,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
    old_pages[filename]=payload(ROOT/'interactive_map'/filename,var)[0]
snapshot=Path(tempfile.mkdtemp(prefix='lme047-signed-review-'))/'Project_before_registration.xlsx'
shutil.copyfile(project,snapshot)
old_hash=sha(project)
print('Registering signed review:',name,date,'excluded group:',excluded,flush=True)
register_review(project,report,unit,mid,excluded)
refresh_reviews(project,snapshot,[unit])
new_hash=sha(project)
with zipfile.ZipFile(project) as z:
    metadata=next(r for _,r in table_rows(z,'Models & coverage','Models')[3] if r['unit_id']==unit and r['model_id']==mid)
review=approved_review(ROOT,metadata,book)
assert review and review['excluded_group_ids']==['Marine mammals']
fresh_name,fresh_date,fresh_summary=read_report(ROOT,report,mid)
registered=json.loads(metadata['researcher_review_summary'])
assert {k:v for k,v in registered.items() if k!='excluded_group_ids'}==fresh_summary
assert (metadata['researcher_name'],metadata['researcher_review_date'])==(fresh_name,fresh_date)
assert metadata['validation_report_sha256']==sha(report)
assert metadata['researcher_review_status']=='Validated by researcher'
page_checks={}
for filename,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
    new,page=payload(ROOT/'interactive_map'/filename,var)
    assert re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',page).group(1)==new_hash
    units=new['network']['units'] if var=='DB' else new['units']
    m=next(m for m in units[unit]['models'] if m['id']==mid)
    assert m['researcher_review']==review
    assert m['display_ppr_excluded_group_ids']==['Marine mammals']
    assert 'Sharks' not in m['display_ppr_excluded_group_ids']
    old=copy.deepcopy(old_pages[filename])
    old_units=old['network']['units'] if var=='DB' else old['units']
    target=next(m for m in old_units[unit]['models'] if m['id']==mid)
    for key in ['researcher_review','display_ppr_excluded_group_ids']:target[key]=copy.deepcopy(m[key])
    assert old==new,'Unrelated embedded data changed: '+filename
    page_checks[filename]={'sha256':sha(ROOT/'interactive_map'/filename),'source_review_equal':True,'unrelated_payload_equal':True}
after={p.relative_to(ROOT).as_posix():sha(p) for p in protected}
assert before==after,'Protected source/scientific files changed'
save('signed_source_summary.json',{'researcher_name':fresh_name,'review_date':fresh_date,'report_sha256':sha(report),'summary':fresh_summary})
save('verification.json',{'schema_version':1,'run_id':OUT.name,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'unit_id':unit,'model_id':mid,'researcher':fresh_name,'review_date':fresh_date,'status':metadata['researcher_review_status'],
    'source_report':'../../../'+report.name,'source_sha256':sha(report),
    'display_exclusions':[{'seq':23,'group':'Marine mammals'}],'explicitly_kept':[{'seq':22,'group':'Sharks'}],
    'project_before_sha256':old_hash,'project_after_sha256':new_hash,'page_checks':page_checks,
    'protected_files_before':before,'protected_files_after':after,'protected_files_unchanged':True,
    'scientific_recalculation':'inapplicable; review metadata and display policy only',
    'catch_sensitivity_adoption':'inapplicable; experiments remain unadopted',
    'archive_and_graph':'unchanged; outside bounded signed-review refresh'})
print('VERIFIED: signed source equals Project/map/trends; Marine mammals excluded; Sharks kept; all other payload and protected science unchanged.',flush=True)
print('Recovery snapshot retained:',snapshot,flush=True)
