"""Read-only 2019 catch-weighted TL decomposition, not a new SPPR estimate.

Run from repo root with bundled Python. Reads current trends payload plus the
Classic PPR tables to verify taxon TL/coefficient identities. Never writes inputs.
Output is exploratory analysis under this run's outputs directory.
"""
import hashlib,json,math,re,sys
from pathlib import Path

ROOT=Path.cwd()
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book,records

OUT=Path(__file__).resolve().parents[1]/'outputs'
OUT.mkdir(parents=True,exist_ok=True)
HTML=ROOT/'interactive_map/trends.html'
blob=HTML.read_bytes()
db=json.loads(re.search(r'const SERIES_DB=(.*?);</script>',blob.decode('utf-8'),re.S).group(1))
selected=[(uid,u,next((m for m in u['models'] if m['id']==u.get('default_model')),None)) for uid,u in db['units'].items()]
selected=[(uid,u,m) for uid,u,m in selected if m and m.get('researcher_review',{}).get('status')=='Validated by researcher']
finite=lambda v: isinstance(v,(float,int)) and math.isfinite(v)
all_groups=[]; regional=[]; checks=[]; sources={str(HTML.relative_to(ROOT)):hashlib.sha256(blob).hexdigest()}
for uid,u,m in selected:
    inp=u['group_inputs']; gd=m['group_data']; yi=inp['years'].index(2019)
    wb=ROOT/m['workbook']; sources[str(wb.relative_to(ROOT))]=hashlib.sha256(wb.read_bytes()).hexdigest()
    classic={r['taxon']:r for r in records(read_book(wb,sheets=['Classic PPR']),'Classic PPR','Taxa')}
    excluded=set(m['display_ppr_excluded_group_ids'])
    bins=[[] for _ in gd['groups']]; positive=set(); included_taxa=set(); missing=[]
    max_sppr_error=max_tl_error=0.0
    # Explicit catch uses full precision payload catch; no allocation renormalization.
    for ti,taxon in enumerate(inp['taxa']):
        c=inp['full_precision_catch'][ti][yi]
        if not finite(c) or c<=0: continue
        positive.add(taxon); s=inp['simple_sppr'][ti]
        pairs=[(gi,w) for gi,w in gd['mappings'][ti] if gd['groups'][gi]['id'] not in excluded and finite(w) and w>0]
        if not pairs: continue
        if not finite(s) or s<=0:
            missing.append({'taxon':taxon,'catch':c,'reason':'missing/nonpositive simple coefficient'});continue
        cr=classic.get(taxon)
        if cr is None or not finite(cr['tl']) or not finite(cr['sppr']):
            raise ValueError((uid,taxon,'missing saved classic TL/SPPR'))
        max_sppr_error=max(max_sppr_error,abs(s-cr['sppr'])/s)
        tl=1+math.log10(s)
        max_tl_error=max(max_tl_error,abs(tl-cr['tl']))
        if not math.isclose(s,cr['sppr'],rel_tol=1e-12) or not math.isclose(tl,cr['tl'],abs_tol=1e-12):
            raise ValueError((uid,taxon,'classic identity mismatch',s,cr))
        included_taxa.add(taxon)
        for gi,w in pairs: bins[gi].append((taxon,c*w,s,tl))
    sums={'simple':0.,'mean_tl_chain':0.,'saved_group_classic':0.,'catch':0.}
    max_group_tl_error=0.
    for gi,parts in enumerate(bins):
        if not parts: continue
        g=gd['groups'][gi]; C=sum(p[1] for p in parts); mu=sum(p[1]*p[3] for p in parts)/C
        E=sum(p[1]*p[2] for p in parts)/C; mid=10**(mu-1); J=E/mid
        sc=gd['scopes']['all'][gi][gd['methods'].index('SPPR_1995_TE0.1')]
        if not finite(sc): raise ValueError((uid,g['id'],'missing group classic'))
        tl_error=(1+math.log10(sc))-g['tl']
        max_group_tl_error=max(max_group_tl_error,abs(tl_error))
        row={'unit_id':uid,'group':g['id'],'catch_tonnes':C,'positive_taxa':len(parts),'taxon_tl_mean':mu,'taxon_tl_variance':sum(p[1]*(p[3]-mu)**2 for p in parts)/C,'model_tl':g['tl'],'effective_classic_tl':1+math.log10(sc),'simple_sppr_mean':E,'chain_at_mean_tl':mid,'jensen_factor':J,'saved_group_classic_sppr':sc,'new_te':{}}
        for scope in ['all','inner','PP']:
            for method in ['new_TE_EEfix','new_TE_noEEfix']:
                coef=gd['scopes'].get(scope,[[]]*len(bins))[gi][gd['methods'].index(method)]
                row['new_te'][scope+'::'+method]=coef
        all_groups.append(row)
        sums['simple']+=C*E;sums['mean_tl_chain']+=C*mid;sums['saved_group_classic']+=C*sc;sums['catch']+=C
    regional.append({'unit_id':uid,'name':u['name'],'model_id':m['id'],'excluded_groups':list(m['display_ppr_excluded_group_ids']),'positive_taxa':len(positive),'included_taxa':len(included_taxa),'groups_with_positive_catch':sum(bool(x) for x in bins),'missing':missing,**sums,'ratio':sums['simple']/sums['saved_group_classic'],'pure_jensen_ratio':sums['simple']/sums['mean_tl_chain'],'mean_tl_centering_ratio':sums['mean_tl_chain']/sums['saved_group_classic']})
    checks.append({'unit_id':uid,'max_simple_coefficient_relative_error':max_sppr_error,'max_saved_taxon_tl_error':max_tl_error,'max_model_tl_vs_effective_classic_tl_error':max_group_tl_error,'workbook_matches_published_sha256':sources[str(wb.relative_to(ROOT))]==m['workbook_sha256']})

sums={k:sum(r[k] for r in regional) for k in ['simple','mean_tl_chain','saved_group_classic','catch']}
agg={**sums,'ratio':sums['simple']/sums['saved_group_classic'],'pure_jensen_ratio':sums['simple']/sums['mean_tl_chain'],'mean_tl_centering_ratio':sums['mean_tl_chain']/sums['saved_group_classic'],'group_count':len(all_groups),'region_count':len(regional),'region_taxon_count':sum(r['included_taxa'] for r in regional)}
scenarios=[]
for scope in ['all','inner','PP']:
    for method in ['new_TE_EEfix','new_TE_noEEfix']:
        key=scope+'::'+method; good=[g for g in all_groups if finite(g['new_te'][key])]
        base=sum(g['catch_tonnes']*g['new_te'][key] for g in good)
        corrected=sum(g['catch_tonnes']*g['new_te'][key]*g['jensen_factor'] for g in good)
        scenarios.append({'scope':scope,'method':method,'group_count':len(good),'missing_groups':[(g['unit_id'],g['group']) for g in all_groups if not finite(g['new_te'][key])],'negative_groups':[(g['unit_id'],g['group'],g['new_te'][key]) for g in good if g['new_te'][key]<0],'base_tC':base/9,'full_residual_jensen_sensitivity_tC':corrected/9,'factor':corrected/base if base else None,'status':'exploratory full residual TL heterogeneity scenario only; may double-count existing network/path heterogeneity; preserves signed coefficients and is not a corrected scientific estimate'})
result={'definition':{'year':2019,'catch_basis':'catch (landings plus discards), full_precision_catch payload','unidentified':'method','source_scope':'all for classic decomposition; separate scopes for new_TE','model_selection':'default selected models whose published researcher review status is Validated by researcher','group_selection':'published signed-review default exclusions; no user browser overrides','simple':'sum catch_i * original allocation_ig * saved simple_sppr_i','mean_tl_chain':'sum C_g * 10**(weighted_mean_taxon_TL_g-1)','saved_group_classic':'sum C_g * saved group SPPR_1995_TE0.1 coefficient','pure_jensen_ratio':'simple / mean_tl_chain','mean_tl_centering_ratio':'mean_tl_chain / saved_group_classic','new_sensitivity':'sum C_g * new_TE_g * J_g, where J_g=E_g[10**(TL_i-1)]/10**(E_g[TL_i]-1); hypothetical entire residual TL heterogeneity only, not identified correction'},'sources_sha256':sources,'checks':checks,'aggregate':agg,'regional':regional,'new_te_scenarios':scenarios,'groups':all_groups}
for path,digest in sources.items():
    if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:
        raise RuntimeError('Input changed during analysis: '+path)
result['all_consumed_inputs_unchanged']=True
(OUT/'decomposition.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
browser_path=OUT/'browser_compare.json'
if browser_path.exists():
    browser=json.loads(browser_path.read_text(encoding='utf-8-sig'))
    assert browser['sha256']==sources[str(HTML.relative_to(ROOT))]
    p2019=browser['comparisons'][0]['points'][-1]
    # Published group and taxon coefficient precision differ slightly.
    assert math.isclose(agg['simple']/9,p2019['ppr_tC'],rel_tol=1e-8)
    assert math.isclose(agg['saved_group_classic']/9,p2019['baseline_ppr_tC'],rel_tol=1e-8)
    assert math.isclose(agg['catch'],p2019['covered_catch'],rel_tol=1e-12)
    assert math.isclose(agg['catch'],p2019['baseline_covered_catch'],rel_tol=1e-12)
    assert math.isclose(scenarios[0]['base_tC'],browser['new_te'][0]['points'][0]['ppr'],rel_tol=1e-8)
    compact={'source_sha256':browser['sha256'],'all_consumed_inputs_unchanged':True,'state':result['definition'],'aggregate':agg,'2019_browser':p2019,'regional':[{k:r[k] for k in ['unit_id','name','ratio','pure_jensen_ratio','mean_tl_centering_ratio','included_taxa','groups_with_positive_catch']} for r in regional],'te_full_residual_sensitivity':scenarios[0],'te_browser':browser['new_te'][0],'input_checks':checks,'caveat':'Saved raw group TL is not exactly the inverse of the saved SPPR_1995 coefficient; centering factor includes model TL/convention differences, not pure arithmetic mean shift.'}
    (OUT/'summary.json').write_text(json.dumps(compact,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'aggregate':agg,'checks':checks,'regional':regional,'new_te_scenarios':scenarios},indent=2,ensure_ascii=True))
