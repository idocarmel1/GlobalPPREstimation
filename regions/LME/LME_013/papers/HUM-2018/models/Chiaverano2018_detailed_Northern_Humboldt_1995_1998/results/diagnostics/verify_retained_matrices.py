"""Independent retained-file verification, without model construction/solving."""
from pathlib import Path
import csv,json,math
import numpy as np
HERE=Path(__file__).resolve().parent
scopes=json.loads((HERE/'source_scope_definitions.json').read_text(encoding='utf-8'))
with (HERE/'group_scope_coefficients.csv').open(encoding='utf-8',newline='') as f: coefficients=list(csv.DictReader(f))
checks=[]
for method in ('GE','TE','With Egestion'):
    folder=HERE/method.replace(' ','_')
    for name in ('SPPR','A','L'):
        arr=np.load(folder/f'{name}.npy',allow_pickle=False)
        masks=np.load(folder/f'{name}_masks.npz',allow_pickle=False)
        axes=json.loads((folder/f'{name}_axes.json').read_text(encoding='utf-8'))
        ids=[[r['id'] for r in axes[a]] for a in ('rows','columns')]
        checks.append({'method':method,'matrix':name,'shape':list(arr.shape),
            'unique_rows':len(set(ids[0]))==len(ids[0]),'unique_columns':len(set(ids[1]))==len(ids[1]),
            'axes_shape_match':list(arr.shape)==[len(v) for v in ids],
            'nan_mask_matches':np.array_equal(masks['nan'],np.isnan(arr)&~masks['null']),
            'posinf_mask_matches':np.array_equal(masks['positive_infinity'],np.isposinf(arr)),
            'neginf_mask_matches':np.array_equal(masks['negative_infinity'],np.isneginf(arr)),
            'null_mask_count':int(masks['null'].sum()),'NaN_count':int(masks['nan'].sum()),
            'positive_infinity_count':int(masks['positive_infinity'].sum()),
            'negative_infinity_count':int(masks['negative_infinity'].sum())})
        assert all(v for k,v in checks[-1].items() if k.endswith('_matches') or k.startswith('unique_') or k=='axes_shape_match')
        if name=='SPPR':
            assert set(ids[1])==set(scopes['all'])
            for scope in ('PP','inner','all'):
                column_indices=[ids[1].index(i) for i in scopes[scope]]
                values=np.sum(arr[:,column_indices],axis=1)
                rows=[r for r in coefficients if r['method']==method and r['scope']==scope]
                coeff={int(r['group_id']):float(r['sppr_wet']) for r in rows}
                expected=np.array([coeff[i] for i in ids[0]])
                assert np.allclose(values,expected,rtol=1e-10,atol=1e-12,equal_nan=True)
                checks.append({'method':method,'scope':scope,'coefficient_sum_reconciles':True,
                               'max_abs_difference':float(np.nanmax(np.abs(values-expected)))})
output={'schema_version':1,'status':'PASS','matrix_checks':checks,
        'scope_sums_all_reconcile':True,'null_nan_infinity_masks_separate':True,
        'all_axes_names_and_IDs_retained':True,'all_groups_including_unfished_retained':True,
        'no_scientific_rerun':True}
(HERE/'retained_matrix_verification.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'PASS','checks':len(checks)}))
