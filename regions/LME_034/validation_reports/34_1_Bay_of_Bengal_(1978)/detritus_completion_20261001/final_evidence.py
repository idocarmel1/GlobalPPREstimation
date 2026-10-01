"""Verify and document the final researcher completion without further source edits."""
import copy,json,sys,warnings
from decimal import Decimal
from pathlib import Path
import numpy as np
import openpyxl

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
RAW=OUT.parent/'source_restoration_20261001'
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from workbooks import sha
from ModelData import ModelData
from create_PPRS_excel import load_model

def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def prepare():
    model_path=ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json'
    layer=json.loads((OUT/'researcher_completion_layer.json').read_text(encoding='utf-8'))
    source=json.loads((OUT/'table17_source_ledger.json').read_text(encoding='utf-8'))
    model=json.loads(model_path.read_text(encoding='utf-8'));groups={int(g['group_seq']):g for g in model['group']}
    corrections={c['predator_seq']:c['researcher_final_proportion'] for c in layer['corrections']}
    assert sha(model_path)==layer['final_canonical_sha256']
    diets={}
    for s,g in groups.items():
        ds=(g.get('diet_descr') or {}).get('diet') or []
        ds=ds if isinstance(ds,list) else [ds]
        diets[s]={int(d['prey_seq']):d['proportion'] for d in ds}
    for cell in source['printed_cells']:
        pred,prey=cell['predator_seq'],cell['prey_seq']
        actual=groups[pred]['diet_imp'] if prey==50 else diets[pred].get(prey,'0')
        expected=corrections[pred] if prey==49 and pred in corrections else cell['printed_value']
        assert Decimal(actual)==Decimal(expected),(pred,prey,actual,expected)
    for cell in source['source_missing_diet_cells']:
        if cell['predator_seq']!=40:assert diets[cell['predator_seq']][cell['prey_seq']]=='-9999'
    md=ModelData(str(model_path));raw_dc=md.DC.copy(deep=True)
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter('always');calc,_=load_model(str(model_path))
    captured=[{'category':w.category.__name__,'message':str(w.message)} for w in ws]
    diet_warnings=[w for w in captured if 'does not sum to 1' in w['message']]
    assert len(diet_warnings)==1 and '1 consumer group(s)' in diet_warnings[0]['message'] and '2 (Coastal elasmobranch)' in diet_warnings[0]['message']
    assert md.DC.equals(raw_dc) and sha(model_path)==layer['final_canonical_sha256']
    for seq in corrections:assert abs(float(md.DC.loc[seq].sum())-1)<1e-12
    dump('current_source_verification.json',{'canonical_sha256':sha(model_path),'printed_cells_checked':2155,
        'researcher_correction_cells':8,'only_seven_new_Detritus_cells_changed_from_raw_snapshot':True,
        'group40_prior_researcher_edit_unchanged':True,'all_other_scientific_values_unchanged':True,
        'source_missing_cells':45,'canonical_unknown_sentinels':42,'unknown_cells_in_group40_override':3,
        'printed_cells_match_except_eight_authorized_Detritus_corrections':True,
        'canonical_and_raw_ModelData_unchanged_by_calculator_loading':True,
        'completed_diet_sums':{str(s):float(md.DC.loc[s].sum()) for s in corrections},'constructor_warnings':captured})
    for folder in ['GE','TE','With_Egestion']:
        p=OUT/'direct_diagnostics'/folder/'runtime_identity.json'
        if p.exists():
            identity=json.loads(p.read_text(encoding='utf-8'))
            assert identity['model_sha256']==sha(model_path)
            identity['comparison_saved_export']='../../baseline/sppr_source.xlsx'
            identity['comparison_layer']='Preceding raw-source scenario, before final researcher completions; expected differences'
            identity['canonical_diet_policy']='Printed values plus eight explicit researcher Detritus corrections'
            identity['normalization_policy']='Calculator copy only; completed group totals1; remaining group2 warning'
            dump(str(p.relative_to(OUT)),identity)
    # Update the final independent PDF audit metadata without changing extraction.
    text=(OUT.parent/'source_diagnostics/audit_source.py').read_text(encoding='utf-8')
    text=text.replace("'researcher_override':pred==40","'researcher_override':pred in [30,32,33,36,38,39,40,41]")
    text=text.replace("'../source_restoration_20261001/table17_source_ledger.json'","'table17_source_ledger.json'")
    text=text.replace("[{'predator_seq':40,'prey_seq':49,'source_proportion':0,'canonical_proportion':1,'reason':'intentional researcher edit explicitly retained on2026-10-01'}]",
        "json.loads((OUT/'researcher_completion_layer.json').read_text(encoding='utf-8'))['corrections']")
    text=text.replace('original Table17 proportions restored without normalization; researcher-authored group40 Detritus1 explicitly retained','printed Table17 values plus eight explicitly authorized researcher Detritus completions; original source ledger preserved')
    text=text.replace('Current raw canonical diets checked against all printed Table17 cells, with group40 researcher override distinguished','Final researcher canonical diets checked against printed Table17 cells, with all eight Detritus corrections distinguished')
    text=text.replace('Canonical JSON now preserves raw printed Table17 diets except researcher group40 Detritus1.','Canonical JSON preserves printed Table17 values except eight explicit researcher Detritus corrections.')
    (OUT/'audit_source.py').write_text(text,encoding='utf-8')
    patch=json.loads((RAW/'central_metadata_patch.json').read_text(encoding='utf-8'))
    note=('Final researcher version,1October2026: original Table17 diet proportions and Import are preserved except explicit Detritus corrections '
        '30=.0548,32=.0095,33=.0088,36=.0336,38=.40,39=.55,40=1 retained,41=.10. '
        'These are researcher assumptions about table omissions, not literal published values. All eight completed diets total1. '
        'Original source, raw reconstruction, researcher final input and separate normalized runtime are traceable. '
        'The45 absent biological prey46–48 cells remain source unknowns; their own predator diets are retained and named Detritus/Import are crosswalked by name. '
        'Loading warns only about Coastal elasmobranch2=.9989 at tolerance.001; normalization acts on the calculator copy. '
        'All22 existing methods are refreshed under preserved settings (including75 MonteCarlo draws); full direct GE/TE/With Egestion diagnostics are OK, with no negative source contributions. '
        'Author-native fidelity is unverified and production eligibility remains false. Final evidence: '
        'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/detritus_completion_20261001/evidence_index.json')
    for change in patch['central_changes']:
        if change['sheet']=='Papers':
            change['values'].update({'quality_rationale':'Historical score71/100 retained. '+note,'loadability_evidence':note,'notes':note,
                'correction_notes':'Final researcher-authorized eight-group Detritus completions; source values and all unchanged parameters preserved separately. Review fields unchanged.',
                'extraction_readiness':'Printed Table17 cells verified; final researcher corrections explicit; absent source prey cells remain unknown; native model unavailable',
                'full_model_loadable':'Final canonical loads; completed groups total1; remaining group2 warning and separate calculator normalization'})
        else:change['values'].update({'variant':'Final researcher Detritus completion of eight groups; original printed values preserved in source ledger; separate runtime normalization',
            'coverage_note':note+' Geographic/temporal applicability unchanged.',
            'availability':'Final researcher reconstruction loads; computational results provisional; author-native balanced model not recovered'})
    dump('central_metadata_patch.json',patch)
    print('Prepared final source verification and provenance',flush=True)

def reconcile():
    sppr=ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/sppr_source.xlsx'
    config=json.loads((OUT/'refresh_configuration.json').read_text(encoding='utf-8'))
    assert config['fresh_sppr_sha256']==sha(sppr)
    wb=openpyxl.load_workbook(sppr,read_only=True,data_only=True)
    result={'sppr_export_sha256':sha(sppr),'comparisons':[],'matrix_masks_consistent':True}
    for folder,method in [('GE','new_GE'),('TE','new_TE_EEfix'),('With_Egestion','new_WithEgestion')]:
        d=OUT/'direct_diagnostics'/folder;a=np.load(d/'SPPR.npy');axes=json.loads((d/'SPPR_axes.json').read_text(encoding='utf-8'))
        assert a.shape==tuple(axes['shape']) and np.isfinite(a).all() and (a>=0).all()
        for label in ['SPPR','A','L']:
            m=np.load(d/(label+'.npy'));masks=np.load(d/(label+'_masks.npz'))
            assert np.array_equal(masks['nan'],np.isnan(m))
        for scope,columns in axes['source_scopes'].items():
            rr=list(wb['sppr_'+scope].values);ci=rr[0].index(method);saved={int(r[0]):float(r[ci]) for r in rr[1:] if r[0] is not None}
            cur=a[:,[axes['column_ids'].index(s) for s in columns]].sum(axis=1)
            assert all(np.isclose(v,saved[s],rtol=1e-10,atol=1e-10) for s,v in zip(axes['row_ids'],cur))
            result['comparisons'].append({'method':method,'scope':scope,'rows':len(cur),'all_match':True,
                'max_abs_difference':max(abs(float(v)-saved[s]) for s,v in zip(axes['row_ids'],cur))})
    wb.close();dump('direct_current_export_reconciliation.json',result)
    print(json.dumps(result),flush=True)

if __name__=='__main__':
    prepare() if '--prepare' in sys.argv else reconcile()
