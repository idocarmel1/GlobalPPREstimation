"""Full raw JSON/loader/initializer parameter and fate audit; no source writes."""
from pathlib import Path
import json,warnings,contextlib,io
import numpy as np
import pandas as pd
from baseline import ROOT,model_paths,load_baseline
from run_study import write_json

def run():
    rows=[];summaries=[]
    aliases={'biomass':'biomass','pb':'pb','qb':'qb','ee':'ee','gs':'gs','ge':'ge','respiration':'respiration','biomass_accum':'biomass_accum',
        'immigration':'immigration','emigration':'emigration','detritus_import':'detritus_import','export':'catch','diet_imp':'diet_import'}
    for path in model_paths():
        with warnings.catch_warnings(),contextlib.redirect_stdout(io.StringIO()):
            warnings.simplefilter('ignore');c,meta=load_baseline(path)
        raw=json.loads(path.read_text(encoding='utf-8'));mid=meta['model_id'];solved=c._groups_df
        for g in raw['group']:
            seq=int(g['group_seq'])
            for rawfield,target in aliases.items():
                if rawfield not in g or target not in solved:continue
                text=g[rawfield]
                try:value=float(text)
                except (ValueError,TypeError):value=np.nan
                if value==-9999:value=np.nan
                loaded=c._model.groups_data.at[seq,target] if target in c._model.groups_data else np.nan
                final=solved.at[seq,target]
                changed=not (pd.isna(value) and pd.isna(final)) and not np.isclose(value,final,rtol=1e-10,atol=1e-12,equal_nan=True)
                rows.append(dict(model_id=mid,group_id=seq,group_name=g['group_name'],source_field=rawfield,engine_field=target,source_text=text,source_numeric=value,
                    loader_value=loaded,initialized_value=final,changed=bool(changed),rule='-9999 is source missing sentinel; export aliases catch; DET catches zeroed; p/q and fractions initialized by unchanged frozen engine'))
        _,rawf=c._model.get_DC(raw);f=c._det_fate
        rawf=rawf.reindex(index=f.index,columns=f.columns).fillna(0)
        for donor in f.index:
            for det in f.columns:
                a=rawf.at[donor,det];b=f.at[donor,det]
                if not np.isclose(a,b,rtol=1e-12,atol=1e-12):
                    rows.append(dict(model_id=mid,group_id=int(donor),group_name=c.seq2name[donor],source_field=f'detritus_fate_to_{det}',engine_field=f'detritus_fate_to_{det}',source_text=str(a),source_numeric=a,loader_value=b,initialized_value=b,changed=True,rule='Unchanged loader forces DET-to-DET identity; Import row zero; fully missing single-DET living fates default closed. Added models reject wholly undocumented living fates.'))
        realids={int(g['group_seq']) for g in raw['group']}
        summaries.append(dict(model_id=mid,source_json_sha256=meta['source_json_sha256'],synthetic_groups=[dict(group_id=int(i),name=c.seq2name[i],type=solved.at[i,'trophic_info']) for i in c.p.index if i not in realids],
            raw_living_export=sum(float(g.get('export',0)) for g in raw['group'] if str(g.get('pp'))!='2' and g.get('export') not in [None,'-9999']),
            raw_detritus_export=sum(float(g.get('export',0)) for g in raw['group'] if str(g.get('pp'))=='2' and g.get('export') not in [None,'-9999']),native_harvest=float(c.catch.sum()),
            notes='Artificial import group represents existing diet imports, not invented migration. Source DET export is not living modeled fishery H. Derived detritus accumulation is audited in flow ledgers.'))
        print('AUDITED',mid,flush=True)
    pd.DataFrame(rows).to_csv(ROOT/'results/raw_to_initialized_parameters.csv',index=False)
    write_json(ROOT/'results/loader_transformations.json',summaries)
if __name__=='__main__':run()
