"""Display traceable selected-model GE results under explicit provisional authorization."""
from pathlib import Path
import sys,json,csv,copy
import pandas as pd
HERE=Path(__file__).resolve().parent;REGION=HERE.parents[1];ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate,set_setting,set_result_hash
def main():
    path=REGION/'HS_077.xlsx';backup=HERE/'HS_077_before_audit.xlsx'
    book=read_book(backup);original=copy.deepcopy(book);o=overview(book);model=o['selected_model_id']
    manifest=json.loads((HERE/'manifest.json').read_text(encoding='utf-8'));assert sha(REGION/o['model_path'])==manifest['model_sha256']
    coefficient_records=json.loads((HERE/'historical_runtime_coefficients_NOT_ADOPTED.json').read_text(encoding='utf-8'))
    reports=json.loads((HERE/'direct_diagnostics.json').read_text(encoding='utf-8'))
    methods={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}
    groups=records(book,'Selected model groups','Groups');names={r['seq']:r['group_name'] for r in groups};types={r['seq']:r['trophic_info'] for r in groups}
    ge=[]
    for option,method in methods.items():
        raw=coefficient_records[option]['sppr'];sppr=pd.DataFrame(raw['data'],index=raw['index'],columns=raw['columns'])
        for seq,row in sppr.iterrows():
            for scope,cols in [('all',sppr.columns),('inner',[i for i in sppr.columns if types[i]!='Import']),('PP',[i for i in sppr.columns if types[i]=='PP'])]:
                ge.append([model,names[seq],scope,method,float(row.loc[cols].sum())])
    original_group_sppr=copy.deepcopy(book['Selected model groups']['Group SPPR'])
    book['Selected model groups']['Group SPPR']=(original_group_sppr[0],ge)
    with (HERE/'matching_review_NOT_ADOPTED.csv').open(encoding='utf-8',newline='') as f:review=list(csv.DictReader(f))
    matching=[[model,r['taxon'],r['group'] or None,float(r['weight']) if r['weight'] else None,'high' if r['group'] else 'unresolved',r['evidence'],r['explanation']] for r in review]
    book['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],matching)
    book['PPR']['Annual']=(ANNUAL_HEADER,[[model,s,method,'landings','method','ppr','provisional: direct '+reports[option]['status']+'; source diet normalization and inferred BA; validation pending',*[None]*70] for s in ['all','inner','PP'] for option,method in methods.items()])
    book['Diagnostics']['provisional_integration_review']=(['field','value'],[['authorization','User requested numeric SPPR mapping/display before later model validation; retain problems visibly.'],['classification','PROVISIONAL RESEARCH OUTPUT; source admission unresolved, supported-catch subtotal only.'],['source_problem','Nine materially inconsistent published diet sums; historical selected runtime normalized ten columns at 0.001 tolerance and inferred BA. No new repair or canonical changes.'],['direct_GE','OK in historical normalized runtime; not a source-fidelity validation.'],['direct_TE','FAIL; provisional numeric trace integrated; negative source-group contributions and failed PP budget.'],['direct_With_Egestion','OK; provisional numeric trace integrated; source validation pending.'],['mapping','Four supported labels only; other species and size-split catches unresolved.'],['geography','Broad ETP pelagic model not identical to HS_077 high seas.'],['evidence','regions/HS_077/evidence/2026-09-28_integration_audit/PROVISIONAL_INTEGRATION.md']])
    write_book(path,book);book=read_book(path);recalculate(book,path)
    # Preserve unrelated legacy coefficients and independent scientific blocks.
    oldh,oldrows=original_group_sppr
    book['Selected model groups']['Group SPPR']=(oldh,[r for r in oldrows if r[3] not in methods.values()]+book['Selected model groups']['Group SPPR'][1])
    for sheet in ['Catch','Classic PPR','NPP']:book[sheet]=original[sheet]
    h,ratios=book['PPR–NPP']['Ratios'];book['PPR–NPP']['Ratios']=(h,[r for r in original['PPR–NPP']['Ratios'][1] if not r[0]]+[r for r in ratios if r[0]])
    flag='provisional: source diet normalization and inferred BA; validation pending'
    for r in book['PPR']['Annual'][1]:
        if r[6]=='ok':r[6]=flag
    set_setting(book,'production_eligible',True)
    set_setting(book,'source_note','PROVISIONAL partial GE: historical selected runtime normalizes inconsistent source diets and infers BA. GE direct OK; TE FAIL. Source/ecological validation pending; four mapped labels only, 48.2954% of 2019 catch.')
    set_setting(book,'calculation_status',flag)
    set_setting(book,'calculation_input_sha256',input_hash(book));set_result_hash(book)
    write_book(path,book);book=read_book(path);validate_region(book,path)
    assert all(book[s]==original[s] for s in ['Catch','Classic PPR','NPP'])
    assert overview(book)['selection_rationale']==o['selection_rationale']
    a={r['metric']:r[2019] for r in records(book,'PPR','Annual') if r['scope']=='all' and r['method']=='new_GE' and r['catch_basis']=='catch' and r['unidentified']=='method'}
    summary={'region':'HS_077','status':flag,'GE_2019_all_source_total_catch_tC':a['ppr']/9,'covered_catch_2019_tonnes':a['covered_catch'],'total_catch_2019_tonnes':a['catch'],'coverage_percent':100*a['covered_catch']/a['catch'],'resolved_labels':4,'total_labels':len(matching),'source_admission':'unresolved; numeric display explicitly authorized','GE_direct_status':reports['GE']['status'],'TE_direct_status':reports['TE']['status'],'canonical_unchanged':sha(REGION/o['model_path'])==manifest['model_sha256'],'catch_classic_npp_unchanged':True,'validation_passed':True,'original_workbook_sha256':sha(backup)}
    summary['methods_2019_tC']={r['method']:r[2019]/9 for r in records(book,'PPR','Annual') if r['scope']=='all' and r['catch_basis']=='catch' and r['unidentified']=='method' and r['metric']=='ppr'}
    summary['method_status']={r['method']:r['status'] for r in records(book,'PPR','Annual') if r['scope']=='all' and r['catch_basis']=='catch' and r['unidentified']=='method' and r['metric']=='ppr'}
    (HERE/'provisional_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
