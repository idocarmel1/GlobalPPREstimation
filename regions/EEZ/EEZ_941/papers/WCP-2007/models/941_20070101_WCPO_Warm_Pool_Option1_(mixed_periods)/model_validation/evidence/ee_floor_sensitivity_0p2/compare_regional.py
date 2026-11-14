"""Read-only regional arithmetic for the three matched EE-floor runs."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import hashlib, json, math, sys

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records, overview, finite

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
path=ROOT/'regions/EEZ/EEZ_941/EEZ_941.xlsx'
input_sha=sha(path)
book=read_book(path,sheets=['Overview','Catch','PPR','Selected model groups'])
settings=overview(book)
model=settings['selected_model_id']
assert model=='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
assert int(settings['taxon_detail_year'])==2019 and settings['catch_basis']=='landings'
run_path=HERE/'comparison.json'
runs=json.loads(run_path.read_text(encoding='utf-8'))
match=defaultdict(list)
for row in records(book,'PPR','Matching'):
    assert row['model_id']==model
    if row.get('group'):
        assert finite(row['weight']) and row['weight']>=0
        match[row['taxon']].append((row['group'],row['weight']))
for taxon,a in match.items():
    assert len(a)==len({g for g,w in a})
    assert math.isclose(math.fsum(w for g,w in a),1,rel_tol=0,abs_tol=1e-9)
catch={}
for row in records(book,'Catch','Catch'):
    if row['catch_basis']=='landings':
        assert row['taxon'] not in catch
        assert finite(row[2019]) and row[2019]>=0
        catch[row['taxon']]=row[2019]
assert len(catch)==63
group_terms=defaultdict(list)
for t,c in catch.items():
    if c>0:assert t in match,t
    for g,w in match.get(t,[]):group_terms[g].append(c*w)
group_catch={g:math.fsum(values) for g,values in group_terms.items()}
catch_total=math.fsum(catch.values())
assert math.isclose(math.fsum(group_catch.values()),catch_total,rel_tol=1e-14)

out={'schema_version':1,'region_id':'EEZ_941','model_id':model,'created_utc':datetime.now(timezone.utc).isoformat(),'reference_year':2019,'catch_basis':'landings','unidentified_treatment':'method','display_scope':'all','units':'tonnes C','conversion':'Wet-weight PPR divided by 9 once','calculation':'Each taxon weighted SPPR is rounded to 6 decimals, matching regional.py; annual totals use all 63 catch labels, including zero-catch labels with unknown coefficients. Unrounded group aggregation is retained as a cross-check.','region_workbook':str(path.relative_to(ROOT)).replace('\\','/'),'region_workbook_sha256':input_sha,'diagnostic_comparison_path':'comparison.json','diagnostic_comparison_sha256':sha(run_path),'taxon_count':63,'positive_catch_taxa':sum(c>0 for c in catch.values()),'catch_total_tonnes':catch_total,'group_catch_tonnes':group_catch,'unresolved_zero_catch_taxa':[t for t in catch if not match.get(t)],'configurations':{},'adoption':'Sensitivity only; no changes to scientific inputs, report, appendix, regional results, Project.xlsx or map/trends.'}
for config in ['OFF','0.1','0.2']:
    config_out={}
    for method in ['GE','TE']:
        source=runs['configurations'][config]['methods'][method]
        data={}
        for scope in ['all','inner','PP']:
            coeff=source['scopes'][scope]
            taxa=[]
            for taxon,c in catch.items():
                a=match.get(taxon,[])
                k=math.fsum(w*coeff[g]for g,w in a) if a and all(finite(coeff.get(g))for g,w in a) else None
                if c>0:assert k is not None,(config,method,scope,taxon)
                value=0.0 if c==0 else c*round(k,6)/9
                taxa.append({'taxon':taxon,'catch_tonnes':c,'sppr_unrounded':k,'sppr_pipeline_6dp':round(k,6)if k is not None else None,'ppr_tC':value})
            total=math.fsum(t['ppr_tC']for t in taxa)
            unrounded=math.fsum(c*coeff[g]/9 for g,c in group_catch.items())
            assert abs(total-unrounded)<=catch_total*0.5e-6/9+1e-6
            data[scope]={'ppr_tC':total,'ppr_group_aggregation_unrounded_tC':unrounded,'pipeline_rounding_difference_tC':total-unrounded,'taxa':taxa}
        diagnostic=source.get('diagnostics',{})
        config_out[method]={'diagnostic_status':diagnostic.get('status',source.get('status')),'scopes':data}
    out['configurations'][config]=config_out
out['changes']=[]
for initial,final in [('OFF','0.1'),('OFF','0.2'),('0.1','0.2')]:
    for method in ['GE','TE']:
        old=out['configurations'][initial][method]['scopes']['all']['ppr_tC'];new=out['configurations'][final][method]['scopes']['all']['ppr_tC']
        out['changes'].append({'from':initial,'to':final,'method':method,'delta_tC':new-old,'percent_change':100*(new-old)/old})
# Compare the floor-OFF case to existing regional annual values, without adopting.
saved={r['method']:r[2019]/9 for r in records(book,'PPR','Annual') if r.get('scope')=='all' and r.get('catch_basis')=='landings' and r.get('unidentified')=='method' and r.get('metric')=='ppr' and r.get('method')in ['new_GE','new_TE_EEfix'] and finite(r.get(2019))}
out['saved_off_comparison']={m:{'saved_tC':saved[key],'new_off_tC':out['configurations']['OFF'][m]['scopes']['all']['ppr_tC'],'difference_tC':out['configurations']['OFF'][m]['scopes']['all']['ppr_tC']-saved[key]}for m,key in [('GE','new_GE'),('TE','new_TE_EEfix')]}
assert sha(path)==input_sha,'Regional workbook changed during comparison'
(HERE/'regional_comparison.json').write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print(json.dumps({'totals_tC':{c:{m:out['configurations'][c][m]['scopes']['all']['ppr_tC']for m in ['GE','TE']}for c in ['OFF','0.1','0.2']},'changes':out['changes'],'saved_off_comparison':out['saved_off_comparison']},indent=2))
