"""Isolated S4 catch sensitivity; no adoption or workbook/document/map writes."""
from pathlib import Path
import copy, datetime, hashlib, json, math, sys, warnings, xml.etree.ElementTree as ET, zipfile
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
R = ROOT / 'regions/LME_047'
MID = '47_2_East_China_Sea_(2018)'
OUT = Path(__file__).resolve().parent
FROZEN = OUT.parent / 'direct_diagnostics/engine'
sys.path.insert(0, str(FROZEN))
sys.path.insert(0, str(ROOT / 'tools'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from workbooks import read_book, records, overview
from regional import recalculate

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def serial(x):
    if isinstance(x, pd.DataFrame):
        arr = x.to_numpy()
        return {'index': serial(list(x.index)), 'columns': serial(list(x.columns)),
                'data': serial(arr.tolist()), 'null_mask': x.isna().values.tolist(),
                'nan_mask': [[bool(isinstance(v,(float,np.floating)) and np.isnan(v)) for v in row] for row in arr],
                'positive_infinity_mask': [[bool(isinstance(v,(float,np.floating)) and np.isposinf(v)) for v in row] for row in arr],
                'negative_infinity_mask': [[bool(isinstance(v,(float,np.floating)) and np.isneginf(v)) for v in row] for row in arr]}
    if isinstance(x, pd.Series): return serial(x.to_frame())
    if isinstance(x, dict): return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [serial(v) for v in x]
    if isinstance(x, np.ndarray): return serial(x.tolist())
    if isinstance(x, np.generic): return serial(x.item())
    if isinstance(x, float) and not math.isfinite(x): return None
    return x
def write(name, value):
    (OUT / name).write_text(json.dumps(serial(value), ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

model = R / 'models' / MID / 'model.json'
workbook = R / 'LME_047.xlsx'
supp = R / 'papers/ECS-2022/DataSheet_1_EstimatingtheImpactofaSeasonal-7491f315.docx'
article = R / 'papers/ECS-2022/pdf-e60d0358.pdf'
protected = [model, workbook, R / 'Model_validation_47_2_East_China_Sea_(2018).docx', ROOT / 'Project.xlsx']
protected += list((ROOT / 'tools/knowledge_graph').glob('graph.json'))
protected += list((ROOT / 'tools/global_map').glob('*')) if (ROOT / 'tools/global_map').exists() else []
protected = [p for p in protected if p.is_file()]
before = {str(p.relative_to(ROOT)): sha(p) for p in protected}
assert sha(model) == '31b1f6c360ce1d454db528e050100e5521cbf663cdb9d3001f0f39724a14ed16'
old_exec = json.loads((OUT.parent / 'direct_diagnostics/execution_evidence.json').read_text(encoding='utf-8'))
for n, h in old_exec['engine_hashes'].items(): assert sha(FROZEN / n) == h

# Extract the original S4 table directly from Word XML, preserving printed decimals.
with zipfile.ZipFile(supp) as z:
    doc = ET.fromstring(z.read('word/document.xml'))
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
tables = doc.findall('.//w:tbl', ns)
s4 = tables[6]
cells = [[ ''.join(tc.itertext()) if False else ''.join(t.text or '' for t in tc.findall('.//w:t', ns))
           for tc in tr.findall('w:tc', ns)] for tr in s4.findall('w:tr', ns)]
assert cells[2][0] == 'Type'
year = next(row for row in cells[3:] if row[0].strip() == '2018')
catches = {int(cells[1][i]): float(year[i]) for i in range(1,len(cells[2])) if cells[2][i].strip() == '6'}
assert catches == {8:.22,9:.86,10:.28,11:.16,13:.39,14:.62,16:.24,17:.39,18:.31,19:.62,20:0.,21:.13}, catches
data = json.loads(model.read_text(encoding='utf-8'))
variant = copy.deepcopy(data)
for g in variant['group']:
    seq = int(g['group_seq'])
    if seq in catches and float(g['export']) != catches[seq]: g['export'] = str(catches[seq])
variant_path = OUT / 'model_S4_catch_2018.json'
write(variant_path.name, variant)
changes = [(i,k) for i,(a,b) in enumerate(zip(data['group'],variant['group'])) for k in a if a[k] != b[k]]
assert all(k == 'export' for i,k in changes) and len(changes) == 11
settings = old_exec['constructor_settings']
diag_settings = old_exec['diagnostic_settings']
book = read_book(workbook)
assert overview(book)['selected_model_id'] == MID
annual = records(book,'PPR','Annual')
names = {int(g['group_seq']):g['group_name'] for g in data['group']}
raw = {}; calcs = {}; results = {}
for label,path in [('no_catch',model),('catch_from_S4',variant_path),('catch_from_S4_M0',model)]:
    if label == 'catch_from_S4_M0':
        c = copy.deepcopy(calcs['no_catch'])
        modified = c.get_groups_df().copy()
        for seq,value in catches.items():
            increment = value - modified.loc[seq,'catch']
            modified.loc[seq,'catch'] = value
            modified.loc[seq,'M0'] -= increment
            modified.loc[seq,'ee'] = 1 - modified.loc[seq,'M0']/modified.loc[seq,'p']
        # Living-group BA is held fixed; update derived detritus routing/balance.
        modified['flow_to_det'] = modified['M0'] + modified['egestion']
        modified = c.apply_ecopath_defaults(modified,c._DC,c._det_fate,
                    zero_catch=False,zero_biomass_accum=False,default_gs=False)
        modified['pb'] = modified['p']/modified['biomass']
        modified['qb'] = modified['q']/modified['biomass']
        c._fill_properties(modified)
        c._sort()
        living = modified.index[modified['trophic_info']=='Regular']
        assert np.array_equal(modified.loc[living,'biomass_accum'].values,
                              calcs['no_catch'].get_groups_df().loc[living,'biomass_accum'].values)
    else:
        c = PPRCalculator.from_modeldata(ModelData(str(path)),**settings)
    calcs[label] = c
    g = c.get_groups_df()
    write(label+'_loaded_groups.json',g)
    write(label+'_loaded_state.json',{k:v for k,v in c.__dict__.items() if isinstance(v,(pd.DataFrame,pd.Series,np.ndarray))})
    working = copy.deepcopy(book)
    reports = {}; solutions = {}
    for method,opt in [('new_GE','GE'),('new_TE_EEfix','TE')]:
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            rep,s,A,L = c.diagnose_sppr(TE_option=opt,**diag_settings)
        reports[method] = {'report':rep,'runtime_warnings':[str(w.message) for w in ws]}
        solutions[method] = {'SPPR':s,'A':A,'L':L}
        raw[label,method] = s
        coefficients = s.sum(axis=1)
        for row in working['Selected model groups']['Group SPPR'][1]:
            if row[0] == MID and row[2] == 'all' and row[3] == method:
                seq = next((i for i,n in c.seq2name.items() if n == row[1]),None)
                assert seq is not None, row[1]
                row[4] = float(coefficients.loc[seq])
    recalculate(working,workbook)  # In-memory only: uses accepted mappings and six-decimal taxon rounding.
    results[label] = {}
    for method in ['new_GE','new_TE_EEfix']:
        rr = next(r for r in records(working,'PPR','Annual') if r['method']==method and r['scope']=='all' and r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric']=='ppr')
        accepted = next(r for r in annual if r['method']==method and r['scope']=='all' and r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric']=='ppr')
        results[label][method] = {'diagnostic_status':reports[method]['report']['status'],
            'regional_2019_ppr_wet_tonnes':rr[2019], 'regional_2019_ppr_tonnes_C':rr[2019]/9,
            'regional_2018_ppr_wet_tonnes':rr[2018], 'regional_2018_ppr_tonnes_C':rr[2018]/9,
            'accepted_regional_2019_ppr_wet_tonnes':accepted[2019],
            'model_native_ppr_wet_tonnes_per_km2_per_year':float(c.get_PPR(raw[label,method],only_inner=False).to_numpy().sum())}
        if label == 'no_catch':
            assert math.isclose(rr[2019],accepted[2019],rel_tol=1e-12,abs_tol=1e-5), results[label][method]
    write(label+'_diagnostics.json',reports)
    write(label+'_solutions.json',solutions)

baseline = calcs['no_catch'].get_groups_df()
scenario = calcs['catch_from_S4'].get_groups_df()
loaded_changes = []
for seq in baseline.index:
    for field in baseline.columns:
        a,b=baseline.loc[seq,field],scenario.loc[seq,field]
        if pd.isna(a) and pd.isna(b): continue
        if isinstance(a,(int,float,np.number)) and isinstance(b,(int,float,np.number)):
            if math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-12): continue
        elif a == b: continue
        loaded_changes.append({'seq':int(seq),'group':calcs['no_catch'].seq2name[seq],'field':field,'no_catch':a,'catch_from_S4':b})
delta = {}
for m in ['new_GE','new_TE_EEfix']:
    s0,s1=raw['no_catch',m],raw['catch_from_S4',m]
    assert list(s0.index)==list(s1.index) and list(s0.columns)==list(s1.columns)
    a=results['no_catch'][m]['regional_2019_ppr_tonnes_C']
    b=results['catch_from_S4'][m]['regional_2019_ppr_tonnes_C']
    delta[m]={'max_absolute_SPPR_change':float(np.max(np.abs((s1-s0).to_numpy()))),
              'regional_2019_difference_tonnes_C':b-a,'regional_2019_change_percent':100*(b/a-1)}
    sm0=raw['catch_from_S4_M0',m]
    cm0=results['catch_from_S4_M0'][m]['regional_2019_ppr_tonnes_C']
    delta[m]['M0_scenario']={'max_absolute_SPPR_change':float(np.max(np.abs((sm0-s0).to_numpy()))),
        'regional_2019_difference_tonnes_C':cm0-a,'regional_2019_change_percent':100*(cm0/a-1)}
m0_groups=calcs['catch_from_S4_M0'].get_groups_df()
invalid_m0=[{'seq':int(seq),'group':calcs['no_catch'].seq2name[seq],
    'M0_baseline':float(baseline.loc[seq,'M0']),'M0_scenario':float(m0_groups.loc[seq,'M0']),
    'EE_baseline':float(baseline.loc[seq,'ee']),'EE_scenario':float(m0_groups.loc[seq,'ee'])}
    for seq in m0_groups.index if m0_groups.loc[seq,'M0'] < 0]
write('M0_scenario_physical_validity.json',{'physically_valid':not invalid_m0,
    'negative_M0_groups':invalid_m0,
    'interpretation':'Numeric experiment only. EE>1 is WARN in the frozen diagnostic implementation, not FAIL; physical validity is checked separately.',
    'definition':'M0_new=M0_baseline-(catch_new-catch_baseline); living BA fixed; EE=1-M0/P; derived detritus inflow and BA recomputed.'})
after={str(p.relative_to(ROOT)):sha(p) for p in protected}
assert before==after
evidence = {'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,
    'scope':'Unadopted isolated sensitivity. Regional landings and mappings fixed. BA scenario changes catch only in source JSON; M0 scenario explicitly changes M0/EE in loaded state, with living BA fixed.',
    'source_hashes':{'canonical_model':sha(model),'supplement':sha(supp),'article':sha(article),'regional_workbook':sha(workbook)},
    'engine_directory':'../direct_diagnostics/engine','engine_hashes':old_exec['engine_hashes'],
    'constructor_settings':settings,'diagnostic_settings':diag_settings,
    'S4_locator':'Supplement Table S4; Type 6; 2018 row (M1997 Ecosim time series)',
    'S4_catch_wet_tonnes_per_km2_per_year':catches,'S4_total':math.fsum(catches.values()),
    'assumptions':['S4 2018 time-series catch is used as a sensitivity proxy for M2018, not asserted to be its exact static Ecopath vector.',
        'Groups with no Type 6 series retain the baseline zero placeholders; these are not observed zeros.',
        'Large yellow croakers use the printed 0.00; rounding does not establish an exact zero.',
        'Missing biomass accumulation is recomputed by the existing loader; no source biological parameters are changed.',
        'Regional reference: 2019 SAU landings, scope all, unidentified method; also retain 2018 reference for comparison.',
        'new TE means new_TE_EEfix; wet-weight PPR divided by nine exactly once.'],
    'M0_scenario_definition':'M0_new=M0_baseline-(catch_new-catch_baseline); living BA fixed; EE=1-M0/P; derived detritus inflow and BA recomputed.',
    'M0_scenario_negative_M0_groups':invalid_m0,
    'results':results,'differences':delta,'loaded_field_changes':loaded_changes,
    'protected_file_hashes_before':before,'protected_file_hashes_after':after,'protected_files_unchanged':before==after}
write('comparison.json',evidence)
print(json.dumps(serial({'results':results,'differences':delta,'M0_scenario_negative_M0_groups':invalid_m0,'protected_files_unchanged':True}),indent=2))
