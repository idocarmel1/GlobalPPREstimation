"""Apply the explicitly authorized final diet corrections and stage its own evidence."""
import copy,json,shutil,sys
from decimal import Decimal
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
FINAL=OUT.parent/'detritus_completion_20261001'
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from workbooks import sha
from ModelData import ModelData

def main():
    FINAL.mkdir(exist_ok=True);baseline=FINAL/'baseline';baseline.mkdir(exist_ok=True)
    model_path=ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json'
    assert sha(model_path)=='3c938197320d07b04435be65bb9515a7d2b86cec865813591f881f589ddc64a7'
    assert not (baseline/'canonical_raw_model.json').exists(),'Final completion already staged; do not overwrite its baseline'
    for src,name in [(model_path,'canonical_raw_model.json'),(model_path.parent/'sppr_source.xlsx','sppr_source.xlsx'),
                     (ROOT/'regions/LME_034/LME_034.xlsx','LME_034.xlsx'),(ROOT/'Project.xlsx','Project.xlsx')]:
        shutil.copy2(src,baseline/name)
    source=json.loads(model_path.read_text(encoding='utf-8'));final=copy.deepcopy(source)
    groups={int(g['group_seq']):g for g in final['group']}
    corrections={30:'0.0548',32:'0.0095',33:'0.0088',36:'0.0336',38:'0.40',39:'0.55',40:'1',41:'0.10'}
    cells=[]
    for seq,value in corrections.items():
        diets=groups[seq]['diet_descr']['diet'];diets=diets if isinstance(diets,list) else [diets]
        det=next(d for d in diets if int(d['prey_seq'])==49)
        prior=det['proportion'];assert Decimal(prior)==(1 if seq==40 else 0)
        det['proportion']=value
        cells.append({'predator_seq':seq,'predator_name':groups[seq]['group_name'],'prey_seq':49,
            'printed_source_proportion':'0','prior_raw_canonical_proportion':prior,'researcher_final_proportion':value,
            'added_to_prior_canonical':str(Decimal(value)-Decimal(prior)),
            'authorization':'Researcher explicitly requested final detritus completion on2026-10-01',
            'interpretation':'Researcher assumes a detritus-feeding table omission; this is an authorized reconstruction, not a literal published value'})
    # The eight Detritus cells are the only permitted changes.
    comparison=copy.deepcopy(final)
    for seq in corrections:
        g=next(g for g in comparison['group'] if int(g['group_seq'])==seq)
        original=next(g for g in source['group'] if int(g['group_seq'])==seq)
        ds=g['diet_descr']['diet'];ds=ds if isinstance(ds,list) else [ds]
        ods=original['diet_descr']['diet'];ods=ods if isinstance(ods,list) else [ods]
        next(d for d in ds if int(d['prey_seq'])==49)['proportion']=next(d for d in ods if int(d['prey_seq'])==49)['proportion']
    assert comparison==source
    assert groups[40]==next(g for g in source['group'] if int(g['group_seq'])==40)
    model_path.write_text(json.dumps(final,ensure_ascii=False,indent=4)+'\n',encoding='utf-8')
    raw=ModelData(str(baseline/'canonical_raw_model.json'));completed=ModelData(str(model_path))
    for seq in corrections:assert abs(float(completed.DC.loc[seq].sum())-1)<1e-12
    ledger=json.loads((OUT/'table17_source_ledger.json').read_text(encoding='utf-8'))
    ledger['run_id']='LME034_detritus_completion_20261001'
    ledger['raw_canonical_sha256']=ledger['canonical_sha256'];ledger['canonical_sha256']=sha(model_path)
    ledger['raw_modeldata_sums']=ledger.pop('modeldata_sums')
    ledger['final_modeldata_sums']={str(k):float(v) for k,v in completed.DC.sum(axis=1).items()}
    ledger['researcher_overrides']=cells
    ledger['layers']={'printed_source':'Unchanged printed cells and original sums, including Import',
        'raw_reconstruction':'../source_restoration_20261001/table17_source_ledger.json; raw canonical snapshot baseline/canonical_raw_model.json',
        'researcher_final':'Eight explicitly authorized Detritus completions; all other values unchanged',
        'runtime':'Existing normalize_DC=True calculator copy; canonical values remain unnormalized except researcher completion'}
    ledger['runtime_policy']='Final canonical retains printed values plus explicit researcher Detritus completions. Calculator normalization is separate. Missing biological prey cells remain source unknown; no missing biological prey values were recovered.'
    (FINAL/'table17_source_ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    layer={'run_id':ledger['run_id'],'source_sha256':ledger['source_sha256'],'raw_canonical_sha256':ledger['raw_canonical_sha256'],
        'final_canonical_sha256':sha(model_path),'corrections':cells,'all_other_scientific_values_unchanged':True,
        'group40_prior_researcher_edit_unchanged':True,'source_missing_diet_cell_count':45,
        'canonical_unknown_sentinels':42,'unknown_cells_within_researcher_group40':3,
        'final_sums_including_import':ledger['final_modeldata_sums']}
    (FINAL/'researcher_completion_layer.json').write_text(json.dumps(layer,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name in ['meiobenthos_source_justification.json','missing_diet_source_sweep.json','initial_diet_appendix_sweep.json']:
        shutil.copy2(OUT/name,FINAL/name)
    for name in ['refresh_outputs.py','adopt_regional_outputs.py','integrate_central.py','index_current_evidence.py']:
        text=(OUT/name).read_text(encoding='utf-8').replace('LME034_source_restoration_20261001','LME034_detritus_completion_20261001')
        text=text.replace('source_restoration_20261001','detritus_completion_20261001')
        if name=='refresh_outputs.py':
            text=text.replace('canonical_normalized_model.json','canonical_raw_model.json')
            text=text.replace('max_abs_runtime_vs_prior_normalized_diet_delta','max_abs_runtime_vs_prior_raw_diet_delta')
            text=text.replace("'researcher_group40_override': float(md.DC.loc[40, 49]),", "'researcher_final_detritus_cells': {str(s):float(md.DC.loc[s,49]) for s in [30,32,33,36,38,39,40,41]},")
        if name=='adopt_regional_outputs.py':
            start=text.index("NOTE = (");end=text.index('\n\n\n',start)
            text=text[:start]+"""NOTE = ('Final canonical keeps printed Table17 values plus explicit researcher Detritus completions for30,32,33,36,38,39,40,41. '
        'The original published values and raw reconstruction remain separate evidence layers. '
        'The45 absent prey46–48 cells remain source unknowns:42-9999 sentinels and3 within the unchanged researcher group40 override. '
        'Existing runtime normalization acts only on the calculator copy; the completed groups sum to1. '
        'Derived biomass accumulation and detritus EE completion remain computational conventions. '
        'Author-native source fidelity remains unverified; model PPR remains provisional. '
        'Reviewed memberships and pooled1978 catch allocations retain their original assumptions.')"""+text[end:]
            text=text.replace('raw Table17 input; runtime normalization; researcher Meiobenthos override','printed input plus researcher Detritus completions; separate runtime normalization')
            text=text.replace('Recalculated22 methods from raw Table17 diets; runtime normalization and researcher Meiobenthos override; provisional','Recalculated22 methods from final researcher Detritus completions; runtime normalization separate; provisional')
            text=text.replace('Printed Table17 values, unnormalized','Printed values plus eight explicit researcher Detritus completions')
            text=text.replace('3 Meiobenthos→Detritus=1 retained by explicit researcher instruction','DET30=.0548;32=.0095;33=.0088;36=.0336;38=.40;39=.55;40=1 retained;41=.10')
            text=text.replace('normalize_DC=True on calculator copy;8-consumer RuntimeWarning; missing cells numerically zero','normalize_DC=True on separate copy; completed groups total1; remaining warnings captured; missing cells numerically zero')
        if name=='integrate_central.py':
            text=text.replace('98c00aa67a990d5d1e353507c4921c38d26fb07564030e916f7735553bbe5c50','665e870a4f34c6859eeda65efb3ca59c0c4076440c21aa8eddef503402fe98fc')
        (FINAL/name).write_text(text,encoding='utf-8')
    print(json.dumps({'final_model_sha256':sha(model_path),'groups_completed':list(corrections),'other_values_unchanged':True}))

if __name__=='__main__':main()
