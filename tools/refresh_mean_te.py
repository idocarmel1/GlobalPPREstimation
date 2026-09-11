"""Refresh only mean-TE workbook cells from saved model parameters.

No LIM, balancing, Monte-Carlo, or unrelated SPPR methods are rerun. The fixed
TE=0.1 result is checked against the workbook to validate reconstructed diets.
Writes a provenance audit and an independently certified live copy of discard
responses; the original scientific study remains untouched.
"""
from pathlib import Path
import argparse
from copy import deepcopy
import hashlib
import json
import shutil
import sys
import warnings

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'PPREstimation'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
import create_PPRS_excel as exporter
from build_model_workbook import save_workbook_atomic
from atomic_output import write_text_atomic

METHODS = ('SPPR_1995_TEmean', 'SPPR_1995_TEmean_catch',
           'Ulanowicz_globalTEmean', 'Ulanowicz_globalTEmean_catch')
AUDIT = ROOT/'data/mean_te_refresh_2026_09_11.json'
BACKUP = ROOT/'tmp/mean_te_refresh_2026_09_11'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    patterns = ['PPREstimation/output/top10/*.xlsx', 'data/*/models/*.xlsx',
                'data/*/mapping/*.resolved.csv', 'data/*/LME_*.xlsx', 'data/*/HS_*.xlsx',
                'PPRAtlas/data/network_ppr.json', 'PPRAtlas/data/time_series.json',
                'PPRAtlas/index.html', 'PPRAtlas/trends.html']
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            target = BACKUP/path.relative_to(ROOT)
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path,target)


def restore_saved(path):
    g = pd.read_excel(path, sheet_name='groups_df').set_index('seq').sort_index(ascending=False)
    g = g.drop(columns=['group_type'])
    source = ROOT/'PPREstimation/real_models/global_cover_jsons'/(path.stem+'.json')
    md = ModelData(str(source))
    with warnings.catch_warnings(record=True) as caught:
        dc = ModelData.validate_DC(md.DC, md.groups_data, normalize=True)
    pc = PPRCalculator.__new__(PPRCalculator)
    pc._groups_df, pc._model = g.copy(), md
    pc._DC = dc.reindex(index=g.index, columns=g.index).fillna(0)
    pc._det_fate = md.det_fate.copy()
    pc.seq2name = g.group_name.to_dict()
    pc.name2seq = {v:k for k,v in pc.seq2name.items()}
    pc.n_groups = len(g)
    for attr, col in {'p':'p','q':'q','catch':'catch','predation':'predation',
                      'growth':'biomass_accum','immigration':'immigration','emigration':'emigration',
                      'M0':'M0','respiration':'respiration','egestion':'egestion','det_export':'det_export',
                      'EE':'ee','GE':'ge','GS':'gs','TL':'tl'}.items():
        setattr(pc,attr,g[col].fillna(0).copy())
    pc.net_migration = (g.net_migration-g.detritus_import).fillna(0).copy()
    pc.is_balanced,_,_ = pc.is_model_balanced()
    assert pc.is_balanced, f'Saved model is not balanced: {path.stem}'
    fixed = pc.SPPR_1995(global_TE=.1)['sppr']
    old = pd.read_excel(path,sheet_name='sppr_all').set_index('seq')['SPPR_1995_TE0.1']
    assert np.allclose(fixed.reindex(old.index),old,rtol=1e-9,atol=1e-8), f'Fixed-TE reconstruction differs: {path.stem}'
    return pc, source, [str(w.message) for w in caught]


def cells(wb):
    return {(s,c.coordinate):c.value for s in wb.sheetnames for row in wb[s] for c in row if c.value is not None}


def update_workbook(path, changes):
    wb = openpyxl.load_workbook(path)
    before = cells(wb)
    for (sheet,address),value in changes.items():
        wb[sheet][address] = value
    after = cells(wb)
    protected_before = {k:v for k,v in before.items() if k not in changes}
    protected_after = {k:v for k,v in after.items() if k not in changes}
    assert protected_before == protected_after
    save_workbook_atomic(wb,path)
    wb.close()
    check = openpyxl.load_workbook(path,read_only=True,data_only=False)
    persisted = cells(check);check.close()
    assert {k:v for k,v in persisted.items() if k not in changes} == protected_before, f'Unrelated cell changed: {path}'
    return len([k for k in changes if before.get(k)!=after.get(k)])


def numeric(value):
    return float(value) if pd.notna(value) and np.isfinite(value) else None


def method_columns(header, sheet, row, changes):
    header = list(header)
    for method in METHODS:
        if method not in header:
            header.append(method)
            changes[(sheet, f'{openpyxl.utils.get_column_letter(len(header))}{row}')] = method
    return {m: openpyxl.utils.get_column_letter(header.index(m)+1) for m in METHODS}


def protected_source_cells(path):
    """Compare to the immutable original snapshot, excluding only four mean methods."""
    wb = openpyxl.load_workbook(path, read_only=True)
    excluded = set()
    for sheet in ('sppr_PP', 'sppr_inner', 'sppr_all'):
        for col in wb[sheet].iter_cols() if not wb.read_only else zip(*list(wb[sheet].rows)):
            if col[0].value in METHODS:
                excluded.update((sheet,c.coordinate) for c in col if c.value is not None)
    for sheet, names in [('footprint', METHODS), ('run_notes', ['method: '+m for m in METHODS])]:
        for row in wb[sheet]:
            if row[0].value in names:
                excluded.update((sheet,c.coordinate) for c in row if c.value is not None)
    result = {k:v for k,v in cells(wb).items() if k not in excluded}
    wb.close()
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    if args.apply: snapshot()
    plans=[]
    audit={'weights':{m:('catch' if m.endswith('_catch') else 'consumption') for m in METHODS},
           'averaging':'arithmetic','cohort':'Regular consumers, including TE=0',
           'methods':list(METHODS),'models':[], 'backup':BACKUP.relative_to(ROOT).as_posix()}
    for path in sorted((ROOT/'PPREstimation/output/top10').glob('*.xlsx')):
        health=pd.read_excel(path,sheet_name='model_health').iloc[0]
        row={'model':path.stem,'path':path.relative_to(ROOT).as_posix(),'before_sha256':digest(path)}
        original_path=BACKUP/path.relative_to(ROOT)
        if original_path.exists():row['original_before_sha256']=digest(original_path)
        audit['models'].append(row)
        if not bool(health.model_input_is_model_balanced):
            row['status']='excluded_unbalanced';print('Excluded unbalanced:',path.stem,flush=True);continue
        pc, source, notes=restore_saved(path)
        row.update(status='ready',source_json_sha256=digest(source),diet_warnings=notes,
                   mean_te={w:float(pc.get_TE('global',as_matrix=False,weights=w).loc[pc.get_Regular_seq()[0]])
                            for w in ('consumption','catch')},
                   catch_weight_basis=('catch' if pc.catch.reindex(pc.get_Regular_seq()).sum()>0 else 'consumer biomass fallback'))
        raw={m:exporter.SPEC_BY_KEY[m].run(pc,0)[0] for m in METHODS}
        raw={k:exporter._to_seq_frame(pc,v) for k,v in raw.items()}
        tables=exporter.build_sppr_tables(pc,raw,METHODS)
        footprint=exporter.build_footprint_table(pc,raw,METHODS)
        wb=openpyxl.load_workbook(path,read_only=True,data_only=False)
        changes={}
        for scope, table in tables.items():
            sheet='sppr_'+('PP' if scope=='pp' else scope)
            rows=list(wb[sheet].values);header=rows[0]
            columns=method_columns(header,sheet,1,changes)
            for i,record in enumerate(rows[1:],2):
                for method in METHODS:
                    address=f'{columns[method]}{i}'
                    changes[(sheet,address)]=numeric(table.loc[record[0],method])
        rows=list(wb['footprint'].values)
        for method in METHODS:
            if method not in [r[0] for r in rows[1:]]:
                rows.append((method,))
                changes[('footprint',f'A{len(rows)}')]=method
        for i,record in enumerate(rows[1:],2):
            if record[0] in METHODS:
                for j,col in enumerate(rows[0][1:],2):
                    changes[('footprint',f'{openpyxl.utils.get_column_letter(j)}{i}')]=numeric(footprint.loc[record[0],col])
        rows=list(wb['run_notes'].values)
        for method in METHODS:
            if 'method: '+method not in [r[0] for r in rows[1:]]:
                rows.append(('method: '+method,))
                changes[('run_notes',f'A{len(rows)}')]='method: '+method
        for i,record in enumerate(rows[1:],2):
            if record[0] in ['method: '+m for m in METHODS]:
                method=record[0][8:]
                changes[('run_notes',f'B{i}')]=exporter.SPEC_BY_KEY[method].description
                changes[('run_notes',f'C{i}')]='ok'
        wb.close();plans.append((path,changes,row))
        print('Prepared:',path.stem,row['mean_te'],row['catch_weight_basis'],flush=True)
    if not args.apply:
        print('Dry run: all calculations validated; no files changed.');return
    for path,changes,row in plans:
        row['changed_cells']=update_workbook(path,changes)
        assert protected_source_cells(path)==protected_source_cells(BACKUP/path.relative_to(ROOT)), f'Original non-mean cells changed: {path}'
        row['after_sha256']=digest(path);row['status']='updated'
        row['unrelated_cells_unchanged']=True
    # Existing central workbooks contain group-scope copies used in downloads.
    audit['central_workbooks']=[]
    for path in sorted((ROOT/'data').glob('*/*.xlsx')):
        if path.stem!=path.parent.name:continue
        wb=openpyxl.load_workbook(path,read_only=True,data_only=False);changes={}
        for scope in ['all','inner','PP']:
            sheet='sppr_'+scope
            if sheet not in wb.sheetnames:continue
            rows=list(wb[sheet].values);header=rows[3]
            if not any(r[0] in {p['model'] for _,_,p in plans} for r in rows[4:]):continue
            columns=method_columns(header,sheet,4,changes)
            cache={}
            for i,record in enumerate(rows[4:],5):
                if record[0] not in {r['model'] for _,_,r in plans}:continue
                if record[0] not in cache:
                    cache[record[0]]=pd.read_excel(ROOT/'PPREstimation/output/top10'/(record[0]+'.xlsx'),sheet_name=sheet).set_index('group_name')
                for method in METHODS:
                    changes[(sheet,f'{columns[method]}{i}')]=numeric(cache[record[0]].loc[record[1],method])
        wb.close()
        if changes:
            audit['central_workbooks'].append({'path':path.relative_to(ROOT).as_posix(),'changed_cells':update_workbook(path,changes)})
    # Re-certify ONLY unchanged response methods against the new workbook hash.
    # No frozen study files or response coefficients are modified.
    original=ROOT/'research/discard_sensitivity_2026_09_10/results/discard_responses.v1.json'
    package=json.loads(original.read_text(encoding='utf-8'))
    package['refresh_provenance']={'original_package':original.relative_to(ROOT).as_posix(),
        'original_package_sha256':digest(original),'audit':AUDIT.relative_to(ROOT).as_posix(),
        'policy':'Unchanged model parameters and non-mean-method cells verified exactly; changed mean methods excluded.'}
    bymodel={r['model']:r for _,_,r in plans}
    for response in package['response_models']:
        if response['model_id'] not in bymodel:continue
        row=bymodel[response['model_id']]
        assert response['source_workbook_sha256']==row['original_before_sha256']
        assert response['source_json_sha256']==row['source_json_sha256']
        response['original_tested_workbook_sha256']=response['source_workbook_sha256']
        response['source_workbook_sha256']=row['after_sha256']
        for method in METHODS:response['methods'].pop(method,None)
    write_text_atomic(ROOT/'data/discard_responses.current.json',json.dumps(package,ensure_ascii=False,separators=(',',':'),allow_nan=False))
    audit['code_sha256']=digest(ROOT/'PPREstimation/PPRCalculator.py')
    write_text_atomic(AUDIT,json.dumps(audit,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(f'Updated {len(plans)} balanced model workbooks; protected all unrelated cells.',flush=True)


if __name__=='__main__':
    main()
