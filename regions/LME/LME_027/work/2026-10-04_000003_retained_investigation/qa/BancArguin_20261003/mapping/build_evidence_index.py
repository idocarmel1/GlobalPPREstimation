"""Independent source-cell/allocation checks and portable mapping-stage inventory."""
from pathlib import Path
import json,hashlib,math,os,re,html
P=Path(__file__).resolve().parent;R=P.parents[2]
def load(n):return json.loads((P/n).read_text(encoding='utf8'))
def save(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def num(x):
    try:return float(re.sub('<[^>]*>','',html.unescape(str(x))).strip())
    except (ValueError,TypeError):return None
raw=load('../extraction/Table_1-f0424c0e.xls.cells.json')
cells={(c['row'],c['column']):c['value'] for c in raw['sheets'][0]['cells']}
rows={int(v):r for (r,c),v in cells.items() if c==1 and str(v).isdigit() and 1<=int(v)<=51}
s8={int(row[0]):row for row in load('source_supplement_tables.json')[9]['rows'][3:] if row[0].strip().isdigit()}
sources={s['id'] for s in load('sources.json')};diffs={};weights={};candidate_n={}
for variant in ['Base','M30','P30']:
    ds=load(f'{variant}_mapping_evidence.json')['mapping'];weights[variant]={};candidate_n[variant]=0
    for d in ds:
        cs=d['candidates'];candidate_n[variant]+=len(cs)
        assert all(ref in sources for ref in d['membership_references']+d['allocation_references'])
        for c in cs:
            i=c['seq'];assert c['source_catch']==num(cells[rows[i],14])
            expected_biomass=num(cells[rows[i],4] if variant=='Base' else s8[i][5 if variant=='M30' else 9])
            assert c['source_biomass']==expected_biomass,(variant,i,c['source_biomass_raw'],expected_biomass,s8.get(i))
            assert c['catch_genuine_reported_zero']==(c['source_catch']==0)
            assert not c['catch_missing'] and not c['biomass_missing']
            assert c['source_catch_inherited_from_Base']==(variant!='Base')
        raw_values=[c['source_catch'] for c in cs]
        if len(cs)==1:expected=[1];assert d['allocation_rule']=='W1'
        elif sum(raw_values)>0:
            expected=[x/sum(raw_values) for x in raw_values];assert d['allocation_rule']=='W4'
        else:
            raw_values=[c['source_biomass'] for c in cs]
            expected=[x/sum(raw_values) for x in raw_values];assert d['allocation_rule']=='W9'
        assert all(math.isclose(c['weight'],w,rel_tol=1e-14,abs_tol=1e-15) for c,w in zip(cs,expected))
        weights[variant][d['taxon']]=[(c['seq'],c['weight']) for c in cs]
    if variant!='Base':diffs[variant]=[t for t,w in weights[variant].items() if w!=weights['Base'][t]]
qa={'original_source_catch_N_cells_checked':True,'original_source_biomass_D_or_S8_cells_checked':True,'candidate_rows_checked':candidate_n,'weights_independently_recomputed':True,'every_source_reference_resolves':True,'source_zeros_vs_unknowns_distinguished':True,'variant_inheritance_checked':True,'different_weight_labels_from_Base':diffs}
save('independent_source_weight_qa.json',qa)
art=[]
def add(role,p):
    p=Path(p);p=p if p.is_absolute() else P/p
    assert p.is_file(),p
    art.append({'role':role,'path':Path(os.path.relpath(p,P)).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'availability':'present'})
for role,name in [('original_pdf','file-e30dfe50.pdf'),('original_xls','Table_1-f0424c0e.xls'),('original_supplement','pone.0094742.s001-eb18ca66.docx')]:add(role,R/'papers/CAN-2014'/name)
add('source_region_workbook',R/'LME_027.xlsx')
for name in ['frozen_workbook_evidence.json','universe_identity.json','catch_labels.json','taxonomy_evidence.json','Taxonomy.xlsx','taxonomy.csv','membership_decisions.json','sources.json','online_search_evidence.json','reference_summaries.json','coverage_all_years_bases.json','classic_reconciliation.json','mapping_verification.json','appendix_qa.json','independent_source_weight_qa.json','report_mapping_text.json','MODEL_PROFILE.md','source_supplement_tables.json','source_article.txt','source_supplement.txt','build_membership.py','build_mapping.py','build_sources.py','build_appendices.mjs','finalize_appendices.py','read_sources.py']:
    add(name,name)
for name in ['candidate_arithmetic_qa.json','verify_candidate_arithmetic.py','skill_independent_test/independent_results.json','skill_independent_test/independent_results_a381157_initial.json','skill_independent_test/run_independent_tests.py','skill_independent_test/core.json']:
    if (P/name).is_file():add(name,name)
for variant in ['Base','M30','P30']:
    for suffix in ['mapping_evidence.json','matching.csv','reference_taxa.csv','catch_2019_taxa.json','landings_2019_taxa.json','discards_2019_taxa.json','appendix_rows.json','appendix_hyperlinks.json']:
        add(variant+'_'+suffix,variant+'_'+suffix)
    add(variant+'_source_vectors',P.parent/f'extraction/{variant}_vectors.json')
    add(variant+'_appendix',R/f'LME027_Guenette2014_{variant}_taxon_mapping_appendix.xlsx')
art.append({'role':'compatible_observed_stage_or_geography_caught_mass_vector','availability':'missing','reason':'No complete matching observed age0–1 mass split or exact Banc/shelf caught-mass vector recovered in the bounded source search. Not required for explicitly assumed W4/W9 mapping.','acquisition_status':'Queries/results and attempted-access limits retained in online_search_evidence.json; numerical model proxy used with Medium allocation confidence.'})
required=[a['role'] for a in art if a['availability']=='present']
ident=load('universe_identity.json')
index={'schema_version':1,'run_id':'BancArguin_20261003_mapping','region_id':'LME_027','model_id':'Guenette2014_BancArguin_Base_1991;Guenette2014_BancArguin_M30_1991;Guenette2014_BancArguin_P30_1991','variant_id':'Base;M30;P30','source_identity':{'publication':'Guenette et al2014 e94742','original_files_roles':['original_pdf','original_xls','original_supplement']},'computational_input_identity':ident,'methods':['Source membership review M1/M2/M3/M4/M5/M6/M9/M10/M11','Allocation W1/W4/W9','Simple trophic chain from frozen Classic PPR taxon coefficients; wet carbon divisor9'],'scope':'Mapping and supporting appendix stage only. Root evidence index covers model coefficient/regional calculation and report stages. No selected-model adoption.','required_roles':required,'artifacts':art,'reconciliation':{'all512labels_all3bases_all70years':True,'source_ID_name_identity':True,'raw_source_values_and_weights_independent':True,'rule_and_confidence_partition':True,'all210classic_annual_sums':load('mapping_verification.json')['classic_annual_reconciliation_all_210'],'source_workbook_unchanged':load('appendix_qa.json')['source_workbook_unchanged'],'appendix512_numeric_sorted_portable_links':True}}
save('evidence_index.json',index)
print(json.dumps(qa,ensure_ascii=False,indent=2));print('Inventory artifacts',len(art))
