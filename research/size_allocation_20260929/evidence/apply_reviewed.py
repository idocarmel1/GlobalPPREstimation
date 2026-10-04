"""Reviewed one-off adoption; source proposals and baseline are immutable evidence."""
from pathlib import Path
import sys,json,copy,math
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(HERE.parent/'regional_ge_integration_20260928'))
from workbooks import *
from xml_audit_reader import read_book
from size_allocations import apply_allocations
from regional import result_hash

def plans():
    out=[]
    aliases={'model_catch_proportions_proxy':'model_catch_proxy','assumed_model_catch_share':'model_catch_proxy','assumed_adult_only_no_catch_basis':'adult_only_assumption'}
    for folder in ['pacific','lme_west','lme_east']:
        source=HERE/folder/'proposals.json';audit=json.loads((HERE/folder/'online_search_audit.json').read_text(encoding='utf-8'))
        for pair in json.loads(source.read_text(encoding='utf-8'))['pairs']:
            pair=copy.deepcopy(pair);pair['evidence_path']=source.relative_to(ROOT).as_posix()
            search=pair.get('online_search_audit')
            if not isinstance(search,dict):
                search=next((r for r in audit.get('records',[]) if r.get('unit_id')==pair['unit_id']),audit)
            for p in pair.get('proposals',[]):
                p['original_rule']=p['rule'];p['rule']='preserved_stage_assumption' if p.get('action')=='document_preserve_exact_weights' else aliases.get(p['rule'],p['rule'])
                p['online_search']=[search]
                for c in p['candidates']:
                    if c['group']=='baby SKJ' and c.get('source_catch') is None and c['weight']==0:
                        c['effective_source_catch']=0
                        c['catch_assumption']='Explicit assumed uncaught infant stage; raw source is missing (-9999), not observed zero.'
                for k in ['evidence','definition','limitations']:
                    if isinstance(p.get(k),list):p[k]='; '.join(v if isinstance(v,str) else clean(v) for v in p[k])
            if pair['unit_id']=='LME_026':
                pair['blocked_proposals']=pair['proposals'];pair['proposals']=[]
            out.append(pair)
    assert len(out)==23 and len({p['unit_id'] for p in out})==23
    return out

def stat(b):
    rr=records(b,'PPR','Annual')
    def val(metric):return next((r.get(2019) for r in rr if r['method']=='new_GE' and r['scope']=='all' and r['catch_basis']=='catch' and r['unidentified']=='method' and r['metric']==metric),None)
    t,c,p=val('catch'),val('covered_catch'),val('ppr')
    return {'total_catch':t,'covered_catch':c,'coverage_pct':100*c/t if finite(c) and t else None,'ppr_tC':p/9 if finite(p) else None}

def verify_arithmetic(b):
    mm={}
    for r in records(b,'PPR','Matching'):
        if r.get('group'):mm.setdefault(r['taxon'],[]).append((r['group'],r['weight']))
    coeff={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(b,'Selected model groups','Group SPPR')}
    tc={}
    for r in records(b,'PPR','Taxon SPPR'):
        vals=[(w,coeff.get((g,r['scope'],r['method']))) for g,w in mm.get(r['taxon'],[])]
        expect=round(math.fsum(w*v for w,v in vals),6) if vals and all(finite(v) for _,v in vals) else None
        assert r['sppr']==expect,(r,expect)
        tc[r['taxon'],r['scope'],r['method']]=expect
    cc=records(b,'Catch','Catch');checks=0
    for r in records(b,'PPR','Annual'):
        if r['unidentified']!='method' or r['metric'] not in ['ppr','covered_catch']:continue
        for year in YEARS:
            vals=[(c[year],tc.get((c['taxon'],r['scope'],r['method']))) for c in cc if c['catch_basis']==r['catch_basis']]
            vals=[(c,v) for c,v in vals if finite(c) and finite(v)]
            expect=math.fsum(c*v if r['metric']=='ppr' else c for c,v in vals) if vals and numeric_status(r['status']) else None
            assert (expect is None and r[year] is None) or (finite(expect) and finite(r[year]) and math.isclose(expect,r[year],rel_tol=1e-12,abs_tol=1e-6)),(r['method'],year,expect,r[year])
            checks+=1
    return checks

def main():
    adopt='--apply' in sys.argv;out=[];pp=plans()
    (HERE/'reviewed_plans.json').write_text(json.dumps({'pairs':pp},ensure_ascii=False,indent=2),encoding='utf-8')
    for p in pp:
        unit=p['unit_id'];path=ROOT/'regions'/unit/(unit+'.xlsx')
        assert sha(path)==p['workbook_sha256'],unit+' changed since review'
        before=read_book(path);validate_region(before,path);b=copy.deepcopy(before)
        impacts=apply_allocations(b,path,p)
        review={k:p.get(k) for k in ['unit_id','model_id','workbook_sha256','review_status','evidence_path']}
        review.update(reviewed_taxa=len(p['proposals']),adopted_taxa=len(p['proposals']),review_date='2026-09-29')
        b['Diagnostics']['Size allocation scope review']=table_dict([review])
        b['Diagnostics']['Size allocation unresolved']=table_dict(p.get('unresolved',[]))
        if p.get('blocked_proposals'):
            b['Diagnostics']['Blocked size allocation proposals']=table_dict(p['blocked_proposals'])
        for s in ['Catch','Classic PPR','NPP','Selected model groups']:assert b[s]==before[s],(unit,s)
        for key in ['selected_model_id','selection_rationale','results_model_sha256']:
            assert overview(b).get(key)==overview(before).get(key),(unit,key)
        for table,content in before['Diagnostics'].items():assert b['Diagnostics'][table]==content,(unit,table)
        assert overview(b)['calculation_result_sha256']==result_hash(b)
        checks=verify_arithmetic(b) if p['proposals'] else 0
        old_numeric={(r['scope'],r['method'],r['catch_basis'],r['unidentified'],r['metric'],y) for r in records(before,'PPR','Annual') for y in YEARS if finite(r[y])}
        new_numeric={(r['scope'],r['method'],r['catch_basis'],r['unidentified'],r['metric'],y) for r in records(b,'PPR','Annual') for y in YEARS if finite(r[y])}
        assert old_numeric<=new_numeric,(unit,'previously numeric cells lost')
        prepared=HERE/'prepared'/unit/(unit+'.xlsx');write_book(prepared,b)
        saved=read_book(prepared);validate_region(saved,path)
        assert overview(saved)['calculation_result_sha256']==result_hash(saved)
        for s in ['Catch','Classic PPR','NPP','Selected model groups']:assert digest_tables(list(saved[s].items()))==digest_tables(list(before[s].items())),(unit,s,'saved')
        before_stat,after_stat=stat(before),stat(saved)
        assumed=next((x['assumed_covered_catch'] for x in impacts if x['scope']=='all' and x['method']=='new_GE' and x['catch_basis']=='catch' and x['year']==2019),0)
        entry={'unit_id':unit,'model_id':p['model_id'],'review_status':p['review_status'],'adopted_taxa':len(p['proposals']),'before':before_stat,'after':after_stat,'assumed_catch':assumed,'verified_annual_cells':checks,'prepared_sha256':sha(prepared),'baseline_sha256':p['workbook_sha256']}
        out.append(entry)
        print(unit,len(p['proposals']),before_stat['coverage_pct'],'->',after_stat['coverage_pct'],flush=True)
    (HERE/'APPLICATION_VERIFICATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    if adopt:
        import shutil
        # All files have passed review, calculation and saved-byte checks before adoption.
        for p in pp:
            unit=p['unit_id'];path=ROOT/'regions'/unit/(unit+'.xlsx')
            assert sha(path)==p['workbook_sha256']
            shutil.copyfile(HERE/'prepared'/unit/(unit+'.xlsx'),path)
        print('Adopted all23 selected-pair reviews; no alternative model changed.',flush=True)

if __name__=='__main__':main()
