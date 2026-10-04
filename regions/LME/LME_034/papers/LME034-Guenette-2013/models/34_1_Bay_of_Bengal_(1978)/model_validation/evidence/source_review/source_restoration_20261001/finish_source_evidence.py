"""Reconcile current printed-source, runtime and exported evidence without recalculation."""
import json, sys
from pathlib import Path
import numpy as np
import openpyxl

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
sys.path.insert(0, str(ROOT / 'tools'))
from workbooks import sha

def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    ledger = json.loads((OUT / 'table17_source_ledger.json').read_text(encoding='utf-8'))
    justification = {
        'interpretation': 'Explicit researcher reconstruction by analogy to the two other regional meiobenthos groups; not a reported group40 diet value',
        'consumer_classification': {'pdf_page': 19, 'section': 'Benthic invertebrates', 'evidence': 'Benthic animals are divided into crustaceans, macrobenthos and meiobenthos; meiobenthos PB9 and PQ0.15 are specified.'},
        'consumer_parameters': {'pdf_page': 24, 'table': '16', 'groups': [16,27,40], 'TL':2,'PB':9,'QB':60,'PQ':0.15},
        'regional_analogy': {'pdf_page':26,'table':'17','predators':[16,27],'prey_seq':49,'printed_detritus_proportion':'1'},
        'group40_printed_counterevidence': {'pdf_pages':[27,56], 'tables':['17','Appendix A3.2'], 'printed_detritus_proportion':'0', 'known_printed_diet_sum':'0', 'absent_prey_cells':[46,47,48]},
        'primary_producer_reclassification_supported':False,
        'specific_group40_100_percent_detritus_explicitly_reported':False,
        'limitation':'TL2 supports consumption at the basal level but does not uniquely specify detritus; the source does not provide a nonzero complete diet for group40.'}
    ledger['researcher_overrides'][0]['source_based_justification'] = justification
    dump('table17_source_ledger.json', ledger)
    dump('meiobenthos_source_justification.json', justification)
    # Keep the reproducible extraction script's generated provenance aligned.
    p = OUT / 'restore_table17.py'
    text = p.read_text(encoding='utf-8')
    text = text.replace("'unchanged_from_prior_canonical': True}]", "'unchanged_from_prior_canonical': True,\n                                       'source_based_justification': json.loads((OUT / 'meiobenthos_source_justification.json').read_text(encoding='utf-8'))}]")
    p.write_text(text, encoding='utf-8')
    for p in [ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/MODEL_PROFILE.md', OUT.parent/'source_review.md', OUT.parent/'source_diagnostics/source_findings.txt']:
        text = p.read_text(encoding='utf-8')
        text += '\nSource justification for the retained Meiobenthos edit: Table16 p24 identifies all three regional meiobenthos groups as consumers (TL2, PB9, QB60, PQ0.15). Table17 p26 gives the other two meiobenthos groups (16 and27) Detritus=1. The group40 value is an explicit researcher reconstruction by this regional analogy; Table17 p27 and AppendixA3.2 p56 print its known diet entries, including Detritus, as zero. The PDF does not explicitly report a complete nonzero group40 diet or support reclassifying it as a primary producer. See source_restoration_20261001/meiobenthos_source_justification.json.\n'
        p.write_text(text, encoding='utf-8')
    patch = json.loads((OUT/'central_metadata_patch.json').read_text(encoding='utf-8'))
    for change in patch['central_changes']:
        for key, value in change['values'].items():
            if 'researcher' in value.casefold():
                change['values'][key] = value + ' Meiobenthos Detritus=1 is a researcher inference supported by the other two regional meiobenthos diets (Table17 p26); group40 is a consumer (Table16 p24), but its published diet is incomplete.'
    patch['central_write_owner']='LME034 responsible agent, coordinated with parent'
    dump('central_metadata_patch.json', patch)
    sppr_path = ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/sppr_source.xlsx'
    wb = openpyxl.load_workbook(sppr_path, read_only=True, data_only=True)
    result = {'sppr_export_sha256':sha(sppr_path),'comparisons':[], 'matrix_masks_consistent':True}
    for folder, method in [('GE','new_GE'),('TE','new_TE_EEfix'),('With_Egestion','new_WithEgestion')]:
        directory = OUT/'direct_diagnostics'/folder
        axes=json.loads((directory/'SPPR_axes.json').read_text())
        a=np.load(directory/'SPPR.npy')
        assert a.shape==tuple(axes['shape']) and np.isfinite(a).all() and (a>=0).all()
        for label in ['SPPR','A','L']:
            matrix=np.load(directory/(label+'.npy'))
            mask=np.load(directory/(label+'_masks.npz'))
            assert mask['nan'].shape==matrix.shape
            assert np.array_equal(mask['nan'],np.isnan(matrix))
        for scope, columns in axes['source_scopes'].items():
            values=list(wb['sppr_'+scope].values); ci=values[0].index(method)
            saved={int(row[0]):float(row[ci]) for row in values[1:] if row[0] is not None}
            idx=[axes['column_ids'].index(seq) for seq in columns]
            current=a[:,idx].sum(axis=1)
            delta=max(abs(float(value)-saved[seq]) for seq,value in zip(axes['row_ids'],current))
            assert all(np.isclose(value,saved[seq],rtol=1e-10,atol=1e-10) for seq,value in zip(axes['row_ids'],current))
            result['comparisons'].append({'method':method,'scope':scope,'rows':len(current),'max_abs_difference':delta,'all_match':True})
    wb.close()
    dump('direct_current_export_reconciliation.json',result)
    print(json.dumps(result))

if __name__=='__main__':main()
