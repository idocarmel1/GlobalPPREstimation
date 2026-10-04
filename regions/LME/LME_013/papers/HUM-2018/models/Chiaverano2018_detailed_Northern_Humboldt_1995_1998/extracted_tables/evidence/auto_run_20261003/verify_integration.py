"""Reconcile saved scientific values and preserve unrelated records and inputs."""
from pathlib import Path
import sys,json,csv,math,hashlib,zipfile
from xml.etree import ElementTree as E
OUT=Path(__file__).resolve().parent; BASE=OUT.parent; ROOT=BASE.parents[3]; REGION=ROOT/'regions/LME_013'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,overview,digest_tables,sha
from original_atlas_data import embedded,branch
MODEL=BASE.name; METHODS={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}
report={}
def close(a,b,scale=1):
    if a in (None,''): assert b in (None,''),(a,b); return
    assert b not in (None,'') and math.isfinite(float(b))
    assert math.isclose(float(a)*scale,float(b),rel_tol=2e-12,abs_tol=1e-6),(a,b,scale)
def csvrows(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:yield from csv.DictReader(f)
b=read_book(REGION/'LME_013.xlsx'); old=read_book(OUT/'baseline/regions/LME_013/LME_013.xlsx')
assert overview(b)['selected_model_id']==MODEL and overview(b)['det_collapse_mode']=='auto'
assert overview(b)['production_eligible'] is False
assert digest_tables([b[x] for x in ['Catch','Classic PPR','NPP']])==digest_tables([old[x] for x in ['Catch','Classic PPR','NPP']])
tc={(r['taxon'],r['scope'],r['method']):r['sppr'] for r in records(b,'PPR','Taxon SPPR')}
for r in json.loads((OUT/'taxon_scope_coefficients.json').read_text(encoding='utf-8')):close(r['sppr_wet'],tc[r['taxon'],r['scope'],METHODS[r['method']]])
gc={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(b,'Selected model groups','Group SPPR')}
for r in csvrows('group_scope_coefficients.csv'):close(r['sppr_wet'],gc[r['group_name'],r['scope'],METHODS[r['method']]])
annual={(r['scope'],r['method'],r['catch_basis'],r['unidentified'],r['metric']):r for r in records(b,'PPR','Annual')}
count=0
for r in csvrows('candidate_annual_totals.csv'):
    key=(r['scope'],METHODS[r['method']],r['catch_basis'],r['unidentified_treatment']);year=int(r['year'])
    close(r['ppr_tC'],annual[*key,'ppr'][year],9)
    close(r['catch_t_wet'],annual[*key,'catch'][year])
    close(r['covered_catch_t_wet'] if r['contribution_complete']=='True' else None,annual[*key,'covered_catch'][year]);count+=3
ratios={(r['scope'],r['method'],r['catch_basis'],r['unidentified'],r['npp_method']):r for r in records(b,'PPR–NPP','Ratios') if r['model_id']==MODEL}
for r in csvrows('candidate_annual_npp_ratios.csv'):
    key=(r['scope'],METHODS[r['method']],r['catch_basis'],r['unidentified_treatment'],r['npp_method'])
    close(r['ppr_npp_ratio'],ratios[key][int(r['year'])],100);count+=1
report['regional_cells_reconciled']=count;report['taxon_coefficients_reconciled']=len(tc);report['group_coefficients_reconciled']=len(gc)
protected=json.loads((OUT/'protected_before.json').read_text(encoding='utf-8'));fail=[];checked=0
cache_entries=0
mutable={'Project.xlsx','regions/LME_013/LME_013.xlsx','regions/LME_013/Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx','regions/LME_013/LME013_HUM2018_candidate_taxon_mapping_appendix_20261003.xlsx'}
prefix='regions/LME_013/candidate_studies/HUM2018_20261003/'
for p,h in protected.items():
    if '/node_modules/' in p or '/__pycache__/' in p or '/vendor/' in p or Path(p).name.startswith('~$'):cache_entries+=1;continue
    if p in mutable or p.startswith('interactive_map/'):continue
    target=BASE/p[len(prefix):] if p.startswith(prefix) else ROOT/p
    if p==prefix+'README.md':target=OUT/'baseline/candidate_README_before.md'
    if not target.is_file() or sha(target)!=h:fail.append(p)
    checked+=1
report['protected_files_verified']=checked;report['protected_mismatches']=fail
report['external_regenerable_runtime_files_excluded']=cache_entries
assert not fail,fail[:20]
# Stream central workbook XML; compare all unrelated rows despite added metadata columns.
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
def tables(path):
    out={}
    with zipfile.ZipFile(path) as z:
        relationships={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for s in E.fromstring(z.read('xl/workbook.xml')).find(NS+'sheets'):
            target=relationships[s.get(R+'id')];target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            block=None;head=None
            with z.open(target) as f:
                for event,row in E.iterparse(f,events=['end']):
                    if row.tag!=NS+'row':continue
                    values={}
                    for cell in row:
                        col=0
                        for c in cell.get('r'):
                            if not c.isalpha():break
                            col=col*26+ord(c)-64
                        value=cell.find(NS+'v');value=value.text if value is not None else None
                        if cell.get('t')=='inlineStr':value=''.join(t.text or '' for t in cell.iter(NS+'t'))
                        if value is not None:values[col-1]=value
                    if values.get(0)=='@table':block=values.get(1);head=None
                    elif block and values:
                        if head is None:head=[values.get(i) for i in range(max(values)+1)];out[s.get('name'),block]=[]
                        else:out[s.get('name'),block].append({head[i]:v for i,v in values.items() if i<len(head) and v is not None})
                    row.clear()
    return out
previous=tables(OUT/'baseline/Project.xlsx');current=tables(ROOT/'Project.xlsx')
concurrent_dir=ROOT/'regions/LME_052/models/52_GM2019_Fig9_Pelagic_(2000-2014)/research_20261003/completion_integration'
receipt=json.loads((concurrent_dir/'registry_registration.json').read_text(encoding='utf-8'))
concurrent_before=concurrent_dir/'Project.before_registration_82e4ce2bc607.xlsx'
assert sha(concurrent_before)==receipt['project_before_sha256']
prior_registration=tables(concurrent_before)
def concurrent_affected(r):return r.get('unit_id')=='LME_052' or r.get('article_id')=='OKH-GM2019__LME_052' or r.get('key')=='article:OKH-GM2019__LME_052'
for key in set(prior_registration)|set(current):
    assert [r for r in prior_registration.get(key,[]) if not concurrent_affected(r)]==[r for r in current.get(key,[]) if not concurrent_affected(r)],('Unexpected change after concurrent registration',key)
report['concurrent_registration_receipt']=str((concurrent_dir/'registry_registration.json').relative_to(ROOT))
report['concurrent_registration_preserved']=True
def affected(r):return r.get('unit_id')=='LME_013' or any(isinstance(v,str) and ('HUM-2018__LME_013' in v or v=='article:HUM-2018__LME_013') for v in r.values())
def geometries(rr):
    groups={}
    for r in rr:
        k=r.get('key',r.get('geometry_id'));part=r.get('chunk',r.get('part'));value=r.get('json',r.get('geojson'))
        groups.setdefault(k,[]).append((int(part),value))
    return {k:json.loads(''.join(v for _,v in sorted(parts))) for k,parts in groups.items()}
diff=[]
for key in set(previous)|set(current):
    if key==('Map geography','Geometry'):
        a=geometries(previous[key]);c=geometries(current[key])
        changed=[k for k in set(a)|set(c) if a.get(k)!=c.get(k)]
        report['geometry_keys_changed']=changed
        assert set(changed).issubset({'article:HUM-2018__LME_013','article:OKH-GM2019__LME_052'}),changed
        continue
    before=[r for r in previous.get(key,[]) if not affected(r)];after=[r for r in current.get(key,[]) if not affected(r)]
    if before!=after:
        left={json.dumps(r,sort_keys=True) for r in before};right={json.dumps(r,sort_keys=True) for r in after}
        changed_before=[r for r in before if json.dumps(r,sort_keys=True) not in right];changed_after=[r for r in after if json.dumps(r,sort_keys=True) not in left]
        diff.append({'table':list(key),'before_rows':len(before),'after_rows':len(after),'changed_before':changed_before,'changed_after':changed_after})
report['unrelated_project_record_differences']=diff
(OUT/'qa/integration_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
unexpected=[d for d in diff if any(not concurrent_affected(r) for r in d['changed_before']+d['changed_after'])]
assert not unexpected,[(d['table'],len(d['changed_before']),len(d['changed_after'])) for d in unexpected]
print('Regional values, original sources/never evidence, and unrelated Project records verified.',flush=True)
db,_=embedded(ROOT/'interactive_map/index.html','DB');series,_=embedded(ROOT/'interactive_map/trends.html','SERIES_DB')
baseline_db,_=embedded(OUT/'baseline/interactive_map/index.html','DB');baseline_series,_=embedded(OUT/'baseline/interactive_map/trends.html','SERIES_DB')
concurrent_update=json.loads((concurrent_dir/'project_update_execution.json').read_text(encoding='utf-8'))
concurrent_build=json.loads((concurrent_dir/'map_build_execution.json').read_text(encoding='utf-8'))
assert concurrent_update['project_after_sha256']==sha(ROOT/'Project.xlsx')
assert concurrent_build['exit_code']==0
report['concurrent_project_update_receipt']=str((concurrent_dir/'project_update_execution.json').relative_to(ROOT))
report['concurrent_map_build_receipt']=str((concurrent_dir/'map_build_execution.json').relative_to(ROOT))
for label,new_units,old_units in [('map',db['network']['units'],baseline_db['network']['units']),('trends',series['units'],baseline_series['units'])]:
    changed=[k for k in old_units if k!='LME_013' and old_units[k]!=new_units.get(k)]
    report[label+'_unrelated_unit_differences']=changed
    # The other region's independently receipted full rebuild corrects five
    # pre-existing source links; it must leave every scientific value untouched.
    permitted_links={'EEZ_598','EEZ_941','HS_071','LME_003','LME_014'}
    assert set(changed).issubset(permitted_links|{'LME_052'}),changed
    for k in changed:
        if k=='LME_052':continue
        before=json.loads(json.dumps(old_units[k]));after=json.loads(json.dumps(new_units[k]))
        for model in before['models']:model.pop('source',None)
        for model in after['models']:
            source=model.pop('source',None)
            if source:assert (ROOT/source).is_file(),source
        assert before==after,('Unrelated scientific payload changed',label,k)
    report[label+'_unrelated_scientific_payload_preserved_except_receipted_LME052']=True
unit=series['units']['LME_013'];assert unit['default_model']==MODEL
model=next(m for m in unit['models'] if m['id']==MODEL)
map_model=next(m for m in db['network']['units']['LME_013']['models'] if m['id']==MODEL)
assert not map_model.get('researcher_review')
assert map_model['calculation_provenance']['det_collapse_mode']=='auto'
assert map_model['calculation_provenance']['production_eligible'] is False
assert (ROOT/map_model['validation_document']).is_file()
for (scope,method,basis,treatment,metric),r in annual.items():
    values=branch(model['scopes'][scope]['methods'][method],treatment,basis)[metric]
    for y,v in zip(range(1950,2020),values):close(r[y],v)
report['map_trends_regional_annual_reconciled']=True
report['selected_model_id']=MODEL;report['production_eligible']=False;report['researcher_verdict_registered']=False
report['project_sha256']=sha(ROOT/'Project.xlsx');report['regional_sha256']=sha(REGION/'LME_013.xlsx')
report['map_sha256']=sha(ROOT/'interactive_map/index.html');report['trends_sha256']=sha(ROOT/'interactive_map/trends.html')
(OUT/'qa/integration_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
