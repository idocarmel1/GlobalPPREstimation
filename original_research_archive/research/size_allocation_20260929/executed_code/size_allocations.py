"""Apply reviewed size/stage assumptions to one selected model-region pair.

This module does not infer membership, perform online research or run an SPPR solver.
The plan must contain those review decisions and their evidence.
"""
import argparse,copy,json,math,shutil
from pathlib import Path
from workbooks import *
from regional import recalculate,set_setting,set_result_hash,inputs

RULES={'observed_catch_size','model_catch_proxy','adult_only_assumption','preserved_stage_assumption'}

def apply_allocations(book,path,plan):
    o=overview(book);proposals=plan.get('proposals',[])
    if plan.get('unit_id')!=o.get('unit_id') or plan.get('model_id')!=o.get('selected_model_id'):
        raise ValueError('Allocation plan does not identify the selected model-region pair')
    taxa,catch,_,_=inputs(book)
    groups={r['group_name']:r for r in records(book,'Selected model groups','Groups')}
    seen=set()
    for p in proposals:
        t=p['taxon'];candidates=p.get('candidates',[])
        if t not in taxa or t in seen:raise ValueError('Unknown or duplicate allocation taxon: '+t)
        seen.add(t)
        if p.get('rule') not in RULES:raise ValueError('Unknown allocation rule')
        if not all(p.get(k) for k in ['evidence','definition','limitations']):raise ValueError('Allocation definition, evidence and limitations required')
        if p['rule']!='observed_catch_size' and not p.get('online_search'):raise ValueError('Record online search before adopting a size/stage proxy')
        if not candidates or len({c['group'] for c in candidates})!=len(candidates):raise ValueError('Missing or duplicate candidate groups')
        for c in candidates:
            if c['group'] not in groups:raise ValueError('Unknown group: '+c['group'])
            group_seq=groups[c['group']].get('seq',groups[c['group']].get('group_seq'))
            if c.get('seq') is not None and str(c['seq'])!=str(group_seq):raise ValueError('Group sequence mismatch')
            if not finite(c.get('weight')) or c['weight']<0:raise ValueError('Invalid allocation weight')
        if not math.isclose(math.fsum(c['weight'] for c in candidates),1,abs_tol=1e-9,rel_tol=0):raise ValueError('Allocation weights must sum to one')
        if p['rule']=='model_catch_proxy':
            vals=[c.get('effective_source_catch',c.get('source_catch')) for c in candidates]
            for c in candidates:
                if c.get('effective_source_catch') is not None and c.get('effective_source_catch')!=c.get('source_catch') and not c.get('catch_assumption'):
                    raise ValueError('Effective catch differs from source: explicit catch assumption required')
            if any(not finite(v) or v<0 for v in vals):raise ValueError('Proxy requires nonnegative source catches; explicit zero assumptions must be recorded separately from missing raw values')
            total=math.fsum(vals)
            if total<=0:raise ValueError('Zero model catch cannot define catch shares')
            if any(not math.isclose(c['weight'],v/total,rel_tol=1e-8,abs_tol=1e-9) for c,v in zip(candidates,vals)):raise ValueError('Weights do not match recorded model catches')
        if p['rule']=='preserved_stage_assumption':
            previous={r['group']:r['weight'] for r in records(book,'PPR','Matching') if r['taxon']==t and r.get('group') and r.get('weight',0)>0}
            proposed={c['group']:c['weight'] for c in candidates if c['weight']>0}
            if previous!=proposed:raise ValueError('Documentation-only allocation must preserve existing positive weights exactly')
    if not proposals:return []
    original=copy.deepcopy(book)
    # Work on a copy so validation/recalculation failures cannot partly mutate the caller.
    working=copy.deepcopy(book)
    matching=records(working,'PPR','Matching')
    ledger=[r for r in records(working,'PPR','Allocation assumptions') if r['taxon'] not in seen]
    for p in proposals:
        t=p['taxon'];previous=[r for r in matching if r['taxon']==t]
        matching=[r for r in matching if r['taxon']!=t]
        for c in p['candidates']:
            base={'unit_id':o['unit_id'],'model_id':o['selected_model_id'],'taxon':t,'rule':p['rule'],'confidence':'assumed',
                  'weight_evidence':'observed size composition' if p['rule']=='observed_catch_size' else p['rule'],
                  'definition':p['definition'],'evidence':p['evidence'],'limitations':p['limitations'],'source_period':p.get('source_period'),
                  'online_search':clean(p.get('online_search')),'previous_mapping':clean(previous),'years_applied':'1950-2019','catch_bases_applied':'landings;catch;discards',
                  'rule_details':p.get('original_rule',p.get('rule_details')),'source_catch_basis':p.get('source_catch_basis'),
                  'temporal_and_basis_assumption':'One fixed model-region mapping; historical and basis-specific size changes not represented.',**c}
            ledger.append(base)
            if c['weight']>0:matching.append({'model_id':o['selected_model_id'],'taxon':t,'group':c['group'],'weight':c['weight'],'confidence':base['confidence'],
                'evidence':p['evidence'],'explanation':f"{p['rule']}: {p['definition']}. {p['limitations']}. See PPR / Allocation assumptions."})
    working['PPR']['Matching']=table_dict(matching)
    working['PPR']['Allocation assumptions']=table_dict(ledger)
    marker='assumed size/stage allocations; see allocation ledger'
    for row in working['PPR']['Annual'][1]:
        if numeric_status(row[6]) and marker not in row[6]:row[6]=('provisional: '+marker if row[6]=='ok' else row[6]+'; '+marker)
    recalculate(working,path)
    # Independent catch, classic estimates and NPP are not part of a size-mapping change.
    for sheet in ['Catch','Classic PPR','NPP']:working[sheet]=original[sheet]
    h,rr=working['PPR–NPP']['Ratios']
    working['PPR–NPP']['Ratios']=(h,[r for r in original['PPR–NPP']['Ratios'][1] if not r[0]]+[r for r in rr if r[0]])
    key=lambda r:(r['scope'],r['method'],r['catch_basis'],r['unidentified'],r['metric'])
    old={key(r):r for r in records(original,'PPR','Annual')};new={key(r):r for r in records(working,'PPR','Annual')}
    coeff={(r['taxon'],r['scope'],r['method']):r['sppr'] for r in records(working,'PPR','Taxon SPPR')}
    assumed={r['taxon'] for r in ledger if r['confidence']=='assumed'}
    impacts=[]
    for k,r in new.items():
        scope,method,basis,treatment,metric=k
        if metric!='ppr' or treatment!='method':continue
        for i,year in enumerate(YEARS):
            cov=new[scope,method,basis,treatment,'covered_catch'][year]
            total=new[scope,method,basis,treatment,'catch'][year]
            amount=math.fsum(catch[t,basis][i] for t in assumed if finite(catch.get((t,basis),[None]*70)[i]) and finite(coeff.get((t,scope,method)))) if finite(cov) else None
            impacts.append({'unit_id':o['unit_id'],'model_id':o['selected_model_id'],'scope':scope,'method':method,'catch_basis':basis,'year':year,'status':r['status'],
                'total_catch':total,'baseline_covered_catch':old.get((scope,method,basis,treatment,'covered_catch'),{}).get(year),
                'covered_catch':cov,'assumed_covered_catch':amount,'covered_without_size_assumptions':cov-amount if finite(cov) else None,
                'baseline_ppr_wet':old.get(k,{}).get(year),'ppr_wet':r[year]})
    working['Diagnostics']['Size allocation impact']=table_dict(impacts)
    working['Diagnostics']['Size allocation review']=table_dict([{'unit_id':o['unit_id'],'model_id':o['selected_model_id'],'assumed_taxa':len(assumed),'reviewed_taxa':len(seen),
        'authorization':plan.get('authorization','User explicitly requested assumed allocations for selected model-region pairs.'),'previous_source_note':o.get('source_note'),'plan_evidence':plan.get('evidence_path')}])
    ge=next((r for r in impacts if r['method']=='new_GE' and r['scope']=='all' and r['catch_basis']=='catch' and r['year']==2019),None)
    current=f"Current 2019 GE catch coverage {100*ge['covered_catch']/ge['total_catch']:.4f}%; {100*ge['assumed_covered_catch']/ge['total_catch']:.4f}% of total catch depends on assumed allocations. " if ge and finite(ge['covered_catch']) and ge['total_catch'] else ''
    set_setting(working,'source_note',f"PROVISIONAL: assumed size/stage allocations for {len(assumed)} taxa. {current}Weights, online search and limitations: PPR / Allocation assumptions. Prior integration note (before these allocations): {o.get('source_note') or ''}")
    set_setting(working,'calculation_status','provisional: recorded size/stage allocation assumptions; original method diagnosis retained')
    set_setting(working,'production_eligible',False)
    set_setting(working,'calculation_input_sha256',input_hash(working));set_result_hash(working)
    validate_region(working,path)
    book.clear();book.update(working)
    return impacts

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--region',type=Path,required=True);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--backup',type=Path,required=True)
    a=ap.parse_args();plan=json.loads(a.plan.read_text(encoding='utf-8'));path=a.region.resolve()
    if plan.get('workbook_sha256')!=sha(path):raise ValueError('Regional workbook differs from reviewed plan')
    b=read_book(path);validate_region(b,path)
    if a.backup.exists():raise ValueError('Backup already exists; retain the previous run and choose a new run location')
    a.backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,a.backup)
    apply_allocations(b,path,plan);write_book(path,b);validate_region(read_book(path),path)
    print('Applied reviewed size allocations:',path.stem)

if __name__=='__main__':main()
