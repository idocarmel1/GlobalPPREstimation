"""Independent saved-value/arithmetic/link verification; no scientific writes."""
import hashlib,json,math,re,shutil,sys,urllib.parse,zipfile
from collections import Counter,defaultdict
from pathlib import Path
from lxml import etree as E
Q=Path(__file__).resolve().parent; OUT=Q.parent; REG=OUT.parents[1]; ROOT=REG.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,rows,overview,sha,digest_tables,YEARS,SIMPLE,finite,numeric_status,input_hash,validate_region
from regional import result_hash
MID=OUT.name; BASE=ROOT/'original_research_archive/research/selected_regions_validation_20260930/baseline/HS_071'
SCRATCH=ROOT/'original_research_archive/research/selected_regions_validation_20260930/work/HS_071'
a=json.loads((OUT/'taxon_audit.json').read_text(encoding='utf-8'))
book=read_book(REG/'HS_071.xlsx'); old=read_book(BASE/'HS_071.xlsx'); o=validate_region(book,REG/'HS_071.xlsx')
model=REG/o['model_path']; raw=json.loads(model.read_text(encoding='utf-8'))
assert sha(model)==sha(BASE/'accepted_model.json')==a['model_sha256']
assert sha(REG/'HS_071.xlsx')==a['final_workbook_sha256']
assert input_hash(book)==o['calculation_input_sha256'];assert result_hash(book)==o['calculation_result_sha256']
protected=[]
for spec in json.loads((BASE/'protected_table_fingerprints.json').read_text(encoding='utf-8'))['tables']:
    s,t=spec['sheet'],spec['table'];same=digest_tables(list(book[s][t]))==digest_tables(list(old[s][t]));assert same,(s,t)
    protected.append({'sheet':s,'table':t,'unchanged':same})
assert [r for r in rows(book,'PPR–NPP','Ratios') if not r[0]]==[r for r in rows(old,'PPR–NPP','Ratios') if not r[0]]
catches={(r['taxon'],r['catch_basis']):r for r in records(book,'Catch','Catch')}
taxa=sorted({t for t,b in catches});classic={r['taxon']:r['sppr'] for r in records(book,'Classic PPR','Taxa')}
assert set(taxa)=={r['taxon'] for r in a['rows']} and len(taxa)==23
unidentified={r['taxon']:bool(r.get('unidentified')) for r in records(book,'Catch','Catch')}
mapping=defaultdict(list)
for r in records(book,'PPR','Matching'):assert r['model_id']==MID;mapping[r['taxon']].append(r)
groups={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(book,'Selected model groups','Group SPPR')}
rawg={int(g['group_seq']):g for g in raw['group']};levels=['High','Medium','Low','Very low','Unresolved']
allocation_count=0
for d in a['rows']:
    mm=mapping[d['taxon']];assert len(mm)==len(d['candidates'])
    assert math.isclose(math.fsum(r['weight'] for r in mm),1,abs_tol=1e-12)
    assert d['confidence']==levels[max(levels.index(d['membership_confidence']),levels.index(d['allocation_confidence']))]
    expected=[]
    for cand in d['candidates']:
        g=rawg[cand['id']];v=float(g['export']);bi=float(g['biomass'])
        assert cand['raw_catch']==(v if v>=0 else None) and cand['biomass']==bi
        actual=next(r for r in mm if r['group']==cand['name'])
        assert math.isclose(actual['weight'],cand['weight'],abs_tol=1e-14)
        assert actual['confidence']==d['confidence'].lower()
        expected.append(v if d['allocation_rule']=='Source-model catch proportions' else bi)
    if d['allocation_rule']=='Source-model catch proportions':
        if d['taxon']=='Katsuwonus pelamis':expected=[v if v>=0 else 0 for v in expected]
        else:assert all(v>=0 for v in expected)
    elif d['allocation_rule']=='Approved model-biomass fallback':
        assert any(c['raw_catch'] is None for c in d['candidates'])
        assert all(v>=0 and math.isfinite(v) for v in expected)
    if len(mm)>1:
        total=math.fsum(expected);assert total>0
        for r,v in zip(mm,expected):assert math.isclose(r['weight'],v/total,abs_tol=1e-14)
        allocation_count+=len(mm)
assert len(records(book,'PPR','Allocation assumptions'))==allocation_count
coeff={(r['taxon'],r['scope'],r['method']):r['sppr'] for r in records(book,'PPR','Taxon SPPR')}
max_coeff_rounding=0
for (t,s,m),v in coeff.items():
    direct=math.fsum(r['weight']*groups[r['group'],s,m] for r in mapping[t])
    assert math.isclose(v,round(direct,6),rel_tol=1e-13,abs_tol=1e-8)
    max_coeff_rounding=max(max_coeff_rounding,abs(v-direct))
checked_annual=0; checked_ratio=0; max_abs_annual=0; max_rel_annual=0; browser=[]
def close(actual,expected,key):
    global max_abs_annual,max_rel_annual
    if expected is None:assert actual is None,key;return
    assert finite(actual) and math.isclose(actual,expected,rel_tol=2e-12,abs_tol=1e-6),(key,actual,expected)
    max_abs_annual=max(max_abs_annual,abs(actual-expected));max_rel_annual=max(max_rel_annual,abs(actual-expected)/max(1,abs(expected)))
for sheet in ['Classic PPR','PPR']:
    for r in records(book,sheet,'Annual'):
        for y in YEARS:
            pairs=[];allcatch=[]
            for t in taxa:
                c=catches[t,r['catch_basis']][y];v=classic[t] if sheet=='Classic PPR' else coeff[t,r['scope'],r['method']]
                if unidentified[t] and r['unidentified']=='zero':v=0.
                if unidentified[t] and r['unidentified']=='simple':v=classic[t]
                allcatch.append(c)
                if finite(c) and finite(v):pairs.append((c,v))
            expected=math.fsum(allcatch) if r['metric']=='catch' and all(finite(c) for c in allcatch) else math.fsum(c*v for c,v in pairs) if r['metric']=='ppr' and pairs and numeric_status(r['status']) else math.fsum(c for c,v in pairs) if r['metric']=='covered_catch' and pairs and numeric_status(r['status']) else None
            close(r[y],expected,(sheet,r['scope'],r['method'],r['catch_basis'],r['unidentified'],r['metric'],y));checked_annual+=1
        if r['metric']=='ppr' and r['catch_basis']=='landings' and r['unidentified']=='method':
            browser.append({'unit_id':'HS_071','model_id':MID if sheet=='PPR' else '', 'year':2019,'catch_basis':'landings','unit':'tonnes C','scope':r['scope'],'method':r['method'],'unidentified':'method','taxon_filter':None,'group_filter':None,'status':r['status'],'ppr_tC':r[2019]/9 if finite(r[2019]) else None})
annual={(r['model_id'],r['scope'],r['method'],r['catch_basis'],r['unidentified']):r for s in ['Classic PPR','PPR'] for r in records(book,s,'Annual') if r['metric']=='ppr'}
npp={r['method']:r for r in records(book,'NPP','NPP')}
for r in records(book,'PPR–NPP','Ratios'):
    pp=annual[r['model_id'],r['scope'],r['method'],r['catch_basis'],r['unidentified']];nn=npp[r['npp_method']]
    for y in YEARS:
        expected=100*pp[y]/9/nn[y] if finite(pp[y]) and finite(nn[y]) and nn[y]>0 else None
        close(r[y],expected,('ratio',r['method'],r['npp_method'],y));checked_ratio+=1
ct=math.fsum(catches[t,'landings'][2019] for t in taxa);pt=math.fsum(catches[t,'landings'][2019]*classic[t]/9 for t in taxa)
assert math.isclose(ct,a['total_catch_tonnes'],abs_tol=1e-8) and math.isclose(pt,a['simple_chain_ppr_tC'],rel_tol=1e-14)
assert a['rows']==sorted(a['rows'],key=lambda d:(d['simple_chain_ppr_tC'] is None,-d['simple_chain_ppr_tC'] if d['simple_chain_ppr_tC'] is not None else 0,d['taxon']))
for field in ['confidence_summary','membership_summary','allocation_summary']:
    assert sum(r['taxa'] for r in a[field])==23
    assert math.isclose(math.fsum(r['catch_tonnes'] for r in a[field]),ct,abs_tol=1e-8)
    assert math.isclose(math.fsum(r['ppr_tC'] for r in a[field]),pt,rel_tol=1e-14)
    assert math.isclose(math.fsum(r['ppr_percentage'] for r in a[field]),100,abs_tol=1e-10)
art=json.loads((Q/'artifact_verification.json').read_text(encoding='utf-8'))
relocated=SCRATCH/'relocated_project';movedreg=relocated/REG.relative_to(ROOT);movedreg.mkdir(parents=True,exist_ok=True)
relocation=[]
for d in art['link_details']:
    if d['kind']!='local':continue
    target=ROOT/d['resolved_repository_path'];dest=relocated/target.relative_to(ROOT)
    dest.parent.mkdir(parents=True,exist_ok=True)
    if target.is_dir():shutil.copytree(target,dest,dirs_exist_ok=True)
    else:shutil.copy2(target,dest);assert sha(target)==sha(dest)
    link=urllib.parse.unquote(d['target']).split('#',1)[0];actual=(movedreg/link).resolve()
    assert actual.exists() and actual==dest.resolve()
    relocation.append({'target':d['target'],'relocated_target_exists':True,'byte_identical_file':target.is_file()})
for p in [REG/f'Model_validation_{MID}.docx',REG/'HS071_taxon_mapping_appendix.xlsx']:
    shutil.copy2(p,movedreg/p.name);assert sha(p)==sha(movedreg/p.name)
# Every Markdown evidence link is resolved from its own source file, never artifact origin.
mdlinks=[]
def markdown_targets(text):
    start=0
    while True:
        pos=text.find('](',start)
        if pos<0:return
        depth=1;end=pos+2
        while end<len(text) and depth:
            if text[end]=='(':depth+=1
            elif text[end]==')':depth-=1
            end+=1
        assert depth==0,'Unclosed Markdown target'
        yield text[pos+2:end-1]
        start=end
for p in [OUT/'source_review.md',OUT/'reports_index.md']:
    for t in markdown_targets(p.read_text(encoding='utf-8')):
        if t.startswith(('https:','http:','#')):continue
        target=(p.parent/urllib.parse.unquote(t.split('#',1)[0])).resolve();assert target.exists() or target==(OUT/'verification.json').resolve(),(p.name,t)
        mdlinks.append({'source':p.name,'target':t,'exists':True})
visual={'report_page_count':6,'report_page_images':[str((SCRATCH/f'page-{i}.png').relative_to(ROOT)).replace('\\','/') for i in range(1,7)],'all_report_pages_visually_inspected':True,'appendix_sheets':['Taxon mapping','Sources'],'all_appendix_rows_visually_inspected':True,'appendix_images':[p.name for p in sorted(Q.glob('appendix_*.png'))],'finding':'Readable headings, table columns, figures, hyperlinks and long reasons; no clipped content or blank report pages. Full-sheet Sources render confirms rows13–18 after segmented-render display ambiguity.','renderer':'DOCX: owned hidden read-only Word COM PDF export then PyMuPDF rasterization; packaged render_docx could not find soffice.exe. XLSX: final file reimported and artifact-tool rendered.','manual_fields_and_template_geometry_preserved':True}
for i in range(1,7):assert (SCRATCH/f'page-{i}.png').exists()
(Q/'visual_qa.json').write_text(json.dumps(visual,indent=2,ensure_ascii=False),encoding='utf-8')
result={'unit_id':'HS_071','selected_model_id':MID,'date':'2026-09-30','model_sha256':sha(model),'baseline_workbook_sha256':sha(BASE/'HS_071.xlsx'),'final_workbook_sha256':sha(REG/'HS_071.xlsx'),'input_sha256':o['calculation_input_sha256'],'result_sha256':o['calculation_result_sha256'],'selected_identity_and_freshness_validated':True,'protected_checks':protected,'classic_ratios_exactly_preserved':True,'taxa_reviewed':23,'mapping_candidates_weights_and_component_confidence_verified':True,'allocation_candidate_rows_checked':allocation_count,'taxon_sppr_entries_checked':len(coeff),'max_taxon_coefficient_rounding_difference':max_coeff_rounding,'annual_numeric_or_unknown_cells_checked':checked_annual,'ratio_numeric_or_unknown_cells_checked':checked_ratio,'arithmetic_tolerance':{'relative':2e-12,'absolute':1e-6},'max_absolute_saved_arithmetic_difference':max_abs_annual,'max_relative_saved_arithmetic_difference':max_rel_annual,'reference_year_total_catch_tonnes':ct,'reference_year_independent_ppr_tC':pt,'confidence_counts':dict(Counter(r['confidence'] for r in a['rows'])),'all_reference_taxa_classic_inputs_available':True,'confidence_and_both_rule_partitions_reconcile':True,'artifact_verification':'qa/artifact_verification.json','actual_relocated_file_copy_check':{'all_existing':True,'root':str(relocated.relative_to(ROOT)).replace('\\','/'),'checks':relocation},'markdown_evidence_links':mdlinks,'visual_qa':'qa/visual_qa.json','expected_browser_values':browser,'shared_integration_and_actual_browser_pending_coordinator':True}
(OUT/'verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
assert (OUT/'verification.json').exists()
print(json.dumps({k:v for k,v in result.items() if k not in ['markdown_evidence_links','actual_relocated_file_copy_check','protected_checks','expected_browser_values']},ensure_ascii=False))
