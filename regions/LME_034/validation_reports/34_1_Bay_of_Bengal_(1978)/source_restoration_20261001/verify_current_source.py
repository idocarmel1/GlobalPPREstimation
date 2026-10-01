"""Verify restored canonical source cells and loading behavior, without recalculation."""
import copy,json,sys,warnings
from decimal import Decimal
from pathlib import Path
import numpy as np

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from workbooks import sha
from ModelData import ModelData
from create_PPRS_excel import load_model

def nondiet(m):
    m=copy.deepcopy(m)
    for g in m['group']:g.pop('diet_descr',None);g.pop('diet_imp',None)
    return m

def main():
    path=ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json'
    model=json.loads(path.read_text(encoding='utf-8'));old=json.loads((OUT/'baseline/canonical_normalized_model.json').read_text(encoding='utf-8'))
    ledger=json.loads((OUT/'table17_source_ledger.json').read_text(encoding='utf-8'))
    groups={int(g['group_seq']):g for g in model['group']}
    diets={}
    for s,g in groups.items():
        entries=(g.get('diet_descr') or {}).get('diet') or []
        if isinstance(entries,dict):entries=[entries]
        diets[s]={int(d['prey_seq']):d['proportion'] for d in entries}
    matched=0;overridden=0
    for cell in ledger['printed_cells']:
        pred,prey=cell['predator_seq'],cell['prey_seq'];value=cell['printed_value']
        actual=groups[pred]['diet_imp'] if prey==50 else diets[pred].get(prey,'0')
        if pred==40 and prey==49:
            assert Decimal(actual)==1 and Decimal(value)==0;overridden+=1
        else:assert Decimal(actual)==Decimal(value),(pred,prey,actual,value)
        matched+=1
    assert matched==2155 and overridden==1
    assert groups[40]==next(g for g in old['group'] if int(g['group_seq'])==40)
    assert nondiet(model)==nondiet(old)
    for c in ledger['source_missing_diet_cells']:
        if c['predator_seq']!=40:assert diets[c['predator_seq']][c['prey_seq']]=='-9999'
    before_hash=sha(path)
    md=ModelData(str(path));before_dc=md.DC.copy(deep=True)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always');calculator,_=load_model(str(path))
    observed=[{'category':w.category.__name__,'message':str(w.message)} for w in caught]
    assert any('does not sum to 1' in w['message'] for w in observed)
    assert md.DC.equals(before_dc) and sha(path)==before_hash
    sums=md.DC.sum(axis=1)
    for seq,source in ledger['source_sums_exact_decimal_including_import'].items():
        expected=1 if seq=='40' else float(source)
        assert abs(float(sums.loc[int(seq)])-expected)<1e-12
    legacy=ModelData(str(OUT/'baseline/canonical_normalized_model.json'))
    assert np.allclose(calculator._DC,legacy.DC,rtol=0,atol=1e-12)
    result={'canonical_sha256':before_hash,'printed_cells_checked':matched,'explicit_researcher_override_cells':overridden,
        'source_missing_cells':45,'unknown_sentinel_cells':42,'override_row_unknown_cells':3,
        'printed_cell_values_match_except_authorized_override':True,'non_diet_parameters_unchanged':True,
        'researcher_group40_unchanged':True,'raw_loading_sums_match_source_except_override':True,
        'canonical_and_raw_ModelData_unchanged_after_loading_calculator':True,
        'normalized_calculator_matches_prior_computational_diet':True,'constructor_warnings':observed,
        'selected_raw_sums':{str(s):float(sums.loc[s]) for s in [30,32,33,36,38,39,40,41,46,47,48]}}
    (OUT/'current_source_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
