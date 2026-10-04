"""Regional adapter: supported SPPR stage, audited native completion and three methods.

The shared exporter expects a numeric legacy filename and silently normalizes diets.
This adapter changes only that I/O/loading boundary; all solver and workbook code is
the project's supported implementation. Each method/diagnostic retains its 180 s limit.
"""
from pathlib import Path
import sys, json, shutil, hashlib
MODEL = Path(__file__).resolve().parent
REGION = MODEL.parents[1]
ROOT = REGION.parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'tools/scientific_code/PPREstimation')]
import create_PPRS_excel as cpe
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from workbooks import read_book, write_book, overview, sha
import run_region

MID = 'PAT2024_FalklandShelf_2020_native'
METHODS = ['new_GE', 'new_TE_EEfix', 'new_WithEgestion']
COMPUTATIONAL = MODEL/'computational_input'/f'14_140001_{MID}_(2020).json'
EVIDENCE = MODEL/'selection_20260928'
ORIGINAL_RUN = cpe.run_directory

def audited_load(model_path):
    # The wrapper's temporary filename cannot represent this exact selected ID in
    # the legacy parser. Verify identical bytes before using the explicit input.
    assert sha(Path(model_path)) == sha(COMPUTATIONAL)
    data = ModelData(str(COMPUTATIONAL))
    calculator = PPRCalculator.from_modeldata(
        data, underdetermined=False, zero_catch=True, zero_biomass_accum=True,
        default_gs=True, normalize_DC=False, DC_tol=0.001)
    assert calculator.is_model_balanced()[0]
    return calculator, MID

def bounded_three_methods(json_dir, out_dir, **kwargs):
    summary = ORIGINAL_RUN(json_dir, out_dir, method_keys=METHODS, silent=True, **kwargs)
    shutil.copy2(summary['report'], EVIDENCE/'selected_sppr_run_report.txt')
    (EVIDENCE/'selected_sppr_run.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    assert summary['n_written'] == 1 and summary['n_failed'] == 0 and summary['n_timeout'] == 0
    assert summary['entries'][0]['n_ok'] == 3
    return summary

def main():
    bookpath = REGION/'LME_014.xlsx'
    book = read_book(bookpath)
    settings = overview(book)
    assert settings['selected_model_id'] == MID
    assert (REGION/settings['model_path']).resolve() == COMPUTATIONAL.resolve()
    before = EVIDENCE/f'LME_014_before_sppr_{sha(bookpath)[:12]}.xlsx'
    if not before.exists(): shutil.copy2(bookpath, before)
    cpe.load_model = audited_load
    cpe.run_directory = bounded_three_methods
    # Reuse the supported stage, including exact configuration health gates and
    # group/annual-result identity handling. No shared file is modified.
    run_region.sppr(book, bookpath, 180)
    write_book(bookpath, book)
    print('Selected SPPR complete:', MID, METHODS)

if __name__ == '__main__': main()
