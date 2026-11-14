"""Compare source-resolved retained GE/TE PPR on exact common 2019 catch support."""
from pathlib import Path
import json, hashlib, math, sys

RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
SCOT=ROOT/'regions/LME/LME_022/papers/NS-2025/models/22_20251990_East_Coast_of_Scotland_(1991-1995)'
HASHES={}
def read(p):
    data=p.read_bytes();HASHES[p.relative_to(ROOT).as_posix()]=hashlib.sha256(data).hexdigest()
    return json.loads(data)
ices=read(RUN/'qa/ices_ge_te_comparison.json')
audit=read(SCOT/'model_validation/evidence/source_review/taxon_audit.json')
support={r['taxon'] for r in audit if r['groups']}
catch={r['taxon']:r['catch_tonnes'] for r in audit}
assert len(audit)==len(catch)==384 and len(support)==372
result={'year':2019,'catch_basis':'catch (landings plus discards)', 'unidentified_treatment':'method',
        'units':'tonnes carbon per year','arithmetic_only':True,'selection_changed':False,
        'total_catch_tonnes':math.fsum(catch.values()),
        'common_catch_tonnes':math.fsum(catch[t] for t in support),
        'unresolved_scotland_labels':[r['taxon'] for r in audit if not r['groups']],
        'common_support_taxa':sorted(support),'cases':{},'input_sha256':HASHES}
for method,d in ices['methods'].items():
    for scope,v in d['scopes'].items():
        assert set(catch)=={t['taxon'] for t in v['taxa']}
        assert all(math.isclose(t['catch_tonnes'],catch[t['taxon']],abs_tol=1e-9) for t in v['taxa'])
        common=math.fsum(t['ppr_tC'] for t in v['taxa'] if t['taxon'] in support)
        result['cases'].setdefault('ICES_floor_ON',{}).setdefault(method,{})[scope]={
            'all_mapped_catch_ppr_tC':v['total_tC'],'common_catch_ppr_tC':common,
            'omitted_for_common_support_tC':v['total_tC']-common,
            'very_low_common_ppr_percent':100*math.fsum(t['ppr_tC'] for t in v['taxa'] if t['taxon'] in support and t['confidence']=='Very low')/common}
for method in ['GE','TE']:
    p=SCOT/'results/diagnostics/2026-11-14_171200_seabird_derived_ba/outputs'/f'corrected_{method}.json'
    saved=read(p); matrix=saved['SPPR']; cols=matrix['columns']; assert cols==[26,25,1]
    vectors=dict(zip(matrix['index'],matrix['values']))
    all_by_scope={scope:{g:math.fsum(v[i] for i,c in enumerate(cols) if scope=='all' or scope=='PP' and c==1) for g,v in vectors.items()} for scope in ['all','PP']}
    for scope,coef in all_by_scope.items():
        contributions=[];excluded=0.;level_totals={}
        for row in audit:
            if row['taxon'] not in support: continue
            vals=[]
            for g in row['groups']:
                v=row['catch_tonnes']*g['weight']*coef[g['seq']]/9
                assert math.isfinite(v) and v>=0
                if g['seq'] in {22,23,24}: excluded+=v
                else: vals.append(v)
            v=math.fsum(vals);contributions.append(v)
            level_totals.setdefault(row['overall_confidence'],[]).append(v)
        total=math.fsum(contributions)
        result['cases'].setdefault('Scotland_historical_floor_OFF',{}).setdefault(method,{})[scope]={
            'common_catch_ppr_tC':total,'all_mapped_catch_ppr_tC':total,
            'signed_excluded_ppr_tC':excluded,'diagnostic_status':saved['diagnostic']['status'],
            'very_low_common_ppr_percent':100*math.fsum(level_totals['Very low'])/total}
if '--include-floor-run' in sys.argv:
    fresh=SCOT/'results/diagnostics/2026-11-14_184500_ee_floor_on_control'
    manifest=read(fresh/'run_manifest.json')
    assert manifest['complete'] is True
    assert manifest['ee_floor']==0.1
    result['fresh_scotland_run']=fresh.relative_to(ROOT).as_posix()
    result['fresh_scotland_engine_commit']=manifest['frozen_engine_commit']
    result['fresh_scotland_diagnostics']=manifest['diagnostic_summary']
    result['floor_differences']={}
    for config in ['control_off','ee_floor_on']:
        d=read(fresh/'outputs'/f'{config}_2019_ppr.json')
        assert len(d['rows'])==384 and d['excluded_allocated_catch_tonnes']==0
        assert {r['taxon'] for r in d['rows'] if r['mapping_resolved']}==support
        assert all(math.isclose(r['catch_tonnes'],catch[r['taxon']],abs_tol=1e-9) for r in d['rows'])
        for method,scopes in d['totals_tC'].items():
            for scope,saved_total in scopes.items():
                known=[r for r in d['rows'] if r['taxon'] in support]
                total=math.fsum(r['methods'][method][scope]['ppr_tC'] for r in known)
                assert math.isclose(total,saved_total,rel_tol=1e-12)
                weak=math.fsum(r['methods'][method][scope]['ppr_tC'] for r in known if r['confidence']=='Very low')
                result['cases'].setdefault('Scotland_'+config,{}).setdefault(method,{})[scope]={
                    'common_catch_ppr_tC':total,'all_mapped_catch_ppr_tC':total,
                    'signed_excluded_ppr_tC':0.0,
                    'diagnostic_status':manifest['diagnostic_summary'][config+'_'+method]['status'],
                    'very_low_common_ppr_percent':100*weak/total}
    for method in ['GE','TE']:
        result['floor_differences'][method]={}
        for scope in ['all','PP']:
            before=result['cases']['Scotland_control_off'][method][scope]['common_catch_ppr_tC']
            old=result['cases']['Scotland_historical_floor_OFF'][method][scope]['common_catch_ppr_tC']
            assert math.isclose(before,old,rel_tol=1e-12)
            after=result['cases']['Scotland_ee_floor_on'][method][scope]['common_catch_ppr_tC']
            ice=result['cases']['ICES_floor_ON']['new_GE' if method=='GE' else 'new_TE_EEfix'][scope]['common_catch_ppr_tC']
            result['floor_differences'][method][scope]={'change_tC':after-before,'change_percent':100*(after-before)/before,'ICES_to_Scotland_ON_ratio':ice/after}
for rel,digest in HASHES.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest
out=RUN/'qa/model_comparison_ge_te.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ['input_sha256','common_support_taxa']},ensure_ascii=False,indent=2))
