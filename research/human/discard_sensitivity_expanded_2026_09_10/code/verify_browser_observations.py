"""Match manually captured actual-browser observations to independent numerical CSV."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def run():
    evidence=json.loads((ROOT/'verification/browser_observations.json').read_text(encoding='utf-8'))
    df=pd.read_csv(ROOT/'results/ecosystem_ppr.csv');checks=[]
    def fmt(v,percent=False):
        if pd.isna(v):return 'Unavailable'
        s=f'{v:,.5f}'.rstrip('0').rstrip('.')
        return ('+' if percent and v>0 else '')+s+('%' if percent else '')
    for case in evidence['cases']:
        sub=df[(df.model_id==case['model_id'])&(df.method==case['method'])&(df.scope==case['scope'])&(df.route==case['route'])&np.isclose(df.fraction,case['fraction'])]
        assert len(sub)==1
        r=sub.iloc[0];fields={'ppr':('ppr_fixed_H_tC' if case['basis']=='H' else 'ppr_retained_L_tC',False),'coefficient_change':('coefficient_change_pct',True),'standard_excess':('standard_relative_excess_pct',True),'pp_ratio':('ppr_to_native_pp_pct',False)}
        for observed,(field,percent) in fields.items():
            if observed not in case:continue
            expected=fmt(r[field],percent)
            assert case[observed]==expected,(case['label'],observed,case[observed],expected)
            checks.append(dict(case=case['label'],field=observed,observed=case[observed],expected=expected,passed=True))
    aggregate=evidence['aggregate'];rows=json.loads((ROOT/'results/aggregate_distributions.json').read_text(encoding='utf-8'))
    a=next(x for x in rows if all(x[k]==aggregate[k] for k in ['method','scope','route','fraction']))
    assert a['n_paired']==aggregate['pointwise_n'] and a['n_all_grid_fixed_support']==aggregate['fixed_n']
    assert fmt(a['coefficient_change_pct']['median'],True)==aggregate['pointwise_median']
    assert fmt(a['fixed_support_coefficient_change_pct']['median'],True)==aggregate['fixed_median']
    runtime=json.loads((ROOT/'verification/report_runtime_checks.json').read_text(encoding='utf-8'))
    assert runtime['passed'] and runtime['cases'][0]['download_csv_characters']==evidence['csv_characters'] and runtime['cases'][0]['download_json_characters']==evidence['json_characters']
    digest=hashlib.sha256((ROOT/'results/report_data.v2.json').read_bytes()).hexdigest()
    assert digest==evidence['embedded_data_sha256_displayed']
    report_digest=hashlib.sha256((ROOT/'report.html').read_bytes()).hexdigest()
    assert report_digest==runtime['report_sha256']
    assert evidence['screening_rows']==252 and not evidence['console_errors_or_warnings']
    out=dict(passed=True,report_sha256=report_digest,embedded_data_sha256=digest,display_checks=checks,aggregate_counts_and_medians_match=True,
        download_character_counts_match_runtime=True,actual_browser=evidence)
    (ROOT/'verification/browser_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Actual-browser numerical checks passed:',len(checks),'displayed values, support counts, hashes and export lengths')
if __name__=='__main__':run()
