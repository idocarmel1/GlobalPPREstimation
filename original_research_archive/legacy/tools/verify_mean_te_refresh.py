"""Verify the mean-TE refresh against its immutable pre-refresh snapshots."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT/'tmp/mean_te_refresh_2026_09_11'
MEANS = {'SPPR_1995_TEmean', 'SPPR_1995_TEmean_catch',
         'Ulanowicz_globalTEmean', 'Ulanowicz_globalTEmean_catch'}
PROVENANCE = {'source_sha256', 'workbook_sha256', 'source_hash', 'source_response',
              'discard_response_source'}


def protected(value):
    """Remove mean-method values and only the metadata changed by their refresh."""
    if isinstance(value, list):
        return [protected(v) for v in value
                if not (isinstance(v, dict) and v.get('id') in MEANS)]
    if not isinstance(value, dict):
        return value
    value = dict(value)
    if value.get('path') == 'PPRAtlas/data/network_ppr.json':
        value.pop('sha256', None)  # The regenerated network hash is checked separately.
    methods = value.get('methods')
    if isinstance(methods, list):
        indices = [i for i,m in enumerate(methods) if m not in MEANS]
        value['methods'] = [methods[i] for i in indices]
        if 'values' in value:
            value['values'] = [[row[i] for i in indices] for row in value['values']]
        if 'groups' in value and 'scopes' in value:
            value['scopes'] = {s:[[row[i] for i in indices] for row in rows]
                               for s,rows in value['scopes'].items()}
    return {k:protected(v) for k,v in value.items() if k not in MEANS | PROVENANCE}


def first_difference(a, b, path=''):
    if type(a) is not type(b): return path
    if isinstance(a, dict):
        if a.keys()!=b.keys():return path+' keys '+str(a.keys()^b.keys())
        for k in a:
            diff=first_difference(a[k],b[k],path+'/'+str(k))
            if diff:return diff
    elif isinstance(a,list):
        if len(a)!=len(b):return path+' length'
        for i,(x,y) in enumerate(zip(a,b)):
            diff=first_difference(x,y,path+'/'+str(i))
            if diff:return diff
    elif a!=b:return path+f': {a!r} != {b!r}'
    return None


def main():
    report = {'scope':'All non-mean model coefficients, annual values, catch, NPP and unaffected discard responses',
              'comparisons':{}}
    for name in ('network_ppr','time_series'):
        print(f'Comparing {name}...', flush=True)
        relative=Path('PPRAtlas/data')/(name+'.json')
        before=json.loads((BACKUP/relative).read_text(encoding='utf-8'))
        after=json.loads((ROOT/relative).read_text(encoding='utf-8'))
        # Labels, the explanation and validation counts legitimately change.
        for d in (before,after):
            for k in ('method_labels','model_note','validation'):d.pop(k,None)
        diff=first_difference(protected(before),protected(after))
        assert diff is None, f'{name}: unrelated value changed at {diff}'
        models=[m for u in after['units'].values() for m in u.get('models',[]) if m['verified']]
        for model in models:
            assert MEANS <= set(model['scopes']['all']['methods']), model['id']
        report['comparisons'][name]={'unrelated_values_exactly_unchanged':True,
            'verified_models_with_four_variants':len(models),
            'before_sha256':hashlib.sha256((BACKUP/relative).read_bytes()).hexdigest(),
            'after_sha256':hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()}
    path=ROOT/'data/mean_te_graph_verification_2026_09_11.json'
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
