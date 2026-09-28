"""Adopt only audited direct coefficients and explicitly supported North Sea taxa."""
from pathlib import Path
import sys,csv,json,copy,math,shutil,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate,set_setting,set_result_hash,inputs
MODEL=HERE.parent/'22_20251990_East_Coast_of_Scotland_(1991-1995)'
REGION=HERE.parent.parent;PATH=REGION/'LME_022.xlsx'
OLD=HERE.parent/'validation/source_evidence/validation/NS-2025_ECS-1990s'
MAP=OLD/'evaluation/data/LME_022/mapping'/f'{MODEL.name}.csv'

def main():
    verification=json.loads((HERE/'runtime_verification.json').read_text(encoding='utf-8'))
    assert verification['canonical_sha256']==sha(MODEL/'model.json')
    assert verification['coefficients_match_retained_export']
    original=read_book(PATH);b=copy.deepcopy(original);assert overview(b)['selected_model_id']==MODEL.name
    backup=HERE/'before_LME_022.xlsx'
    if not backup.exists():shutil.copy2(PATH,backup)
    else:assert sha(PATH)==sha(backup),'Already integrated; do not overwrite newer changes'
    source=next((REGION/'papers/NS-2025').glob('*.xlsx'))
    w=openpyxl.load_workbook(source,read_only=True,data_only=True)
    crosswalk={'Large Demersal fish':'Large Dem. fish'}
    source_groups={crosswalk.get(str(r[1]).strip(),str(r[1]).strip()):{'row':i,'description':r[2]} for i,r in enumerate(w['Table S2'].values,1) if i>=3 and r[1]}
    w.close()
    source_model=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))
    assert set(source_groups)=={r['group_name'] for r in source_model['group']}
    for g in source_model['group']:
        desc=source_groups[g['group_name']]['description']
        if desc!='-':assert desc in g['taxon_descr'],g['group_name']
    legacy=list(csv.DictReader(MAP.open(encoding='utf-8-sig')))
    taxa,catch,unidentified,_=inputs(b);assert set(taxa)=={r['taxon'] for r in legacy}
    reviewed=[];mapping=[]
    extra={
      'Argentina':('Small pelagics','Table S2 explicitly defines Argentines as Argentina sp.; no within-pool allocation is needed.'),
      'Polychaeta':('Infauna','Table S2 explicitly names Polychaeta as the infaunal polychaete category.'),
      'Cerastoderma edule':('Epifauna','Table S2 explicitly includes cockles; WoRMS AphiaID 138998 identifies this taxon as common cockle. https://www.marinespecies.org/introduced/aphia.php?id=138998&p=taxdetails'),
      'Buccinum undatum':('Epifauna','Table S2 explicitly includes whelks (source spelling Bussinum undatum retained). WoRMS AphiaID 138878 supports the catch identity common whelk. https://marinespecies.org/berms/aphia.php?id=138878&p=taxdetails')}
    for r in legacy:
        t=r['taxon'];group=None;confidence='unresolved';evidence='not_adopted';explanation=''
        if r['evidence']=='explicit_member':
            group=r['group'];assert t in source_groups[group]['description'],(t,group)
            confidence='high';evidence='explicit_source_member'
            explanation='Exact catch taxon named in selected-model Table S2 Main Species. Representative list supports this inclusion, not unlisted taxa or exhaustive composition.'
        elif t in extra:
            group,explanation=extra[t];confidence='medium';evidence='explicit_source_category'
        elif '|' in r['group']:
            explanation='Historical split not adopted: source does not establish regional constituent proportions. Identified-catch-derived historical weights are not observed composition of this catch label.'
        elif r['group']=='Unresolved':explanation=r['explanation']
        else:explanation='Historical taxonomic/guild extension not adopted as explicit membership. Retained as unresolved in this conservative supported-catch subtotal; absence from a representative list is not proof of exclusion. '+r['explanation']
        provenance=f'{source.relative_to(ROOT).as_posix()} / Table S2'
        if group:provenance+=f' row {source_groups[group]["row"]}'
        mapping.append([MODEL.name,t,group,1.0 if group else None,confidence,provenance+'; '+evidence,explanation])
        reviewed.append({**r,'adopted_group':group,'adopted_weight':1 if group else None,'decision':evidence,'review':explanation})
    b['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],mapping)
    with (HERE/'mapping_review.csv').open('w',encoding='utf-8',newline='') as f:
        cw=csv.DictWriter(f,fieldnames=list(reviewed[0]));cw.writeheader();cw.writerows(reviewed)
    with (HERE/'loaded_groups.csv').open(encoding='utf-8') as f:
        rr=list(csv.reader(f));headers=rr[0]
    # Use retained native workbook for typed group fields, verified against reloaded runtime.
    w=openpyxl.load_workbook(MODEL/'sppr_source.xlsx',read_only=True,data_only=True)
    rr=list(w['groups_df'].values);b['Selected model groups']['Groups']=(list(rr[0]),[list(r) for r in rr[1:]])
    w.close()
    coeff=[]
    for scope,file_scope in [('all','all'),('inner','inner'),('PP','pp')]:
        for r in csv.DictReader((HERE/f'group_sppr_{file_scope}.csv').open(encoding='utf-8')):
            for method in ['new_GE','new_WithEgestion','new_TE_EEfix']:
                # Failed TE coefficients remain only in diagnostic evidence, not taxon calculations.
                value=None if method=='new_TE_EEfix' else float(r[method])
                coeff.append([MODEL.name,r['group_name'],scope,method,value])
    b['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],coeff)
    health=json.loads((HERE/'health.json').read_text(encoding='utf-8'))
    b['Diagnostics']['model_health']=table_dict(health)
    b['Diagnostics']['regional_integration_review']=table_dict([{'evidence':str(HERE.relative_to(ROOT).as_posix()),'finding':'GE and With Egestion accepted conditionally for the audited completed runtime; TE FAIL and unavailable. Source-normalization, default GS, derived BA and Scotland-to-North-Sea transfer retained. Conservative mapped-catch subtotal only.'}])
    b['PPR']['Annual']=(ANNUAL_HEADER,[[MODEL.name,s,m,'landings','method','ppr','FAIL: configuration diagnostic' if m=='new_TE_EEfix' else 'ok',*[None]*70] for s in ['all','inner','PP'] for m in ['new_GE','new_WithEgestion','new_TE_EEfix']])
    set_setting(b,'catch_basis','catch');set_setting(b,'taxon_detail_year',2019)
    recalculate(b,PATH)
    # Classic inputs did not change. Preserve their historical rows/sensitivity and ratios exactly.
    b['Classic PPR']=copy.deepcopy(original['Classic PPR'])
    h,rr=b['PPR–NPP']['Ratios'];oldrat=rows(original,'PPR–NPP','Ratios')
    b['PPR–NPP']['Ratios']=(h,[r for r in rr if r[0]]+[r for r in oldrat if not r[0]])
    mapped={r[1] for r in mapping if r[2]};coverage=[]
    for basis in ['landings','discards','catch']:
        for year in YEARS:
            vals=[catch[t,basis][year-1950] for t in taxa];supported=[catch[t,basis][year-1950] for t in mapped]
            total=math.fsum(vals) if all(finite(x) for x in vals) else None
            covered=math.fsum(supported) if all(finite(x) for x in supported) else None
            coverage.append({'year':year,'basis':basis,'total_catch_tonnes':total,'supported_catch_tonnes':covered,'coverage_pct':100*covered/total if total else None})
    with (HERE/'coverage_by_year_basis.csv').open('w',encoding='utf-8',newline='') as f:
        cw=csv.DictWriter(f,fieldnames=list(coverage[0]));cw.writeheader();cw.writerows(coverage)
    c2019=next(r for r in coverage if r['year']==2019 and r['basis']=='catch')
    status=f'Conditional supported-catch subtotal; GE/Egestion OK for audited normalized/completed runtime; TE FAIL unavailable; {c2019["coverage_pct"]:.2f}% of 2019 total catch; Scotland spatial transfer; evidence models/regional_ge_integration_20260928'
    set_setting(b,'calculation_status',status)
    set_setting(b,'source_note','Partial results only. East-coast Scotland 1991–1995 coefficients applied to North Sea 1950–2019 catch, including discards although source model excludes them. Not a whole-region ecosystem reconstruction. Canonical source preserved; runtime diet normalization, GS defaults and residual BA completion documented. Unsupported catch stays missing.')
    # Keep full-region production_eligible=False; method eligibility derives from real audit/status rows.
    set_result_hash(b)
    write_book(PATH,b)
    saved=read_book(PATH);validate_region(saved,PATH)
    for sheet in ['Catch','Classic PPR','NPP']:assert saved[sheet]==original[sheet],sheet
    assert overview(saved)['selected_model_id']==overview(original)['selected_model_id']
    assert overview(saved)['model_path']==overview(original)['model_path']
    coeffs={(r['taxon'],r['scope'],r['method']):r['sppr'] for r in records(saved,'PPR','Taxon SPPR')}
    checks=0
    for r in records(saved,'PPR','Annual'):
        if r['metric']!='ppr' or r['unidentified']!='method':continue
        for y in YEARS:
            if r['method']=='new_TE_EEfix':assert r[y] is None;continue
            expected=math.fsum(catch[t,r['catch_basis']][y-1950]*coeffs[t,r['scope'],r['method']] for t in mapped)
            assert math.isclose(r[y],expected,rel_tol=2e-14,abs_tol=1e-6),(r,y)
            checks+=1
    annual=records(saved,'PPR','Annual')
    for scope in ['all','inner','PP']:
        for method in ['new_GE','new_WithEgestion']:
            basis_values={r['catch_basis']:r for r in annual if r['scope']==scope and r['method']==method and r['metric']=='ppr' and r['unidentified']=='method'}
            for y in YEARS:assert math.isclose(basis_values['catch'][y],basis_values['landings'][y]+basis_values['discards'][y],rel_tol=1e-12,abs_tol=1e-6)
    result=next(r for r in annual if r['scope']=='all' and r['method']=='new_GE' and r['catch_basis']=='catch' and r['unidentified']=='method' and r['metric']=='ppr')[2019]
    summary={'model_id':MODEL.name,'year':2019,'basis':'catch (landings + discards)','scope':'all','unidentified':'method','ge_ppr_wet_tonnes':result,'ge_ppr_tC':result/9,'mapped_taxa':len(mapped),'total_taxa':len(taxa),'coverage_2019':c2019,'annual_independent_sums_checked':checks,'preserved':['Catch','Classic PPR','NPP','model selection','canonical model'],'canonical_sha256':sha(MODEL/'model.json'),'workbook_sha256':sha(PATH),'source_supplement_sha256':sha(source),'legacy_mapping_sha256':sha(MAP),'largest_unsupported_2019':[{'taxon':t,'catch_tonnes':catch[t,'catch'][-1]} for t in sorted(set(taxa)-mapped,key=lambda t:catch[t,'catch'][-1],reverse=True)[:20]]}
    (HERE/'integration_verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
