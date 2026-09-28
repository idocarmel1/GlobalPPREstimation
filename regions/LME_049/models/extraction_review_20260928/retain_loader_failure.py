"""Bounded single-candidate API reproducer retaining the wrapper's load failure."""
from pathlib import Path
import sys,json,shutil,traceback
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
import create_PPRS_excel as cpe
if __name__=='__main__':
    dest=ROOT/'regions/LME_049/models/49_20192013_Western_North_Pacific_Watari_(2013)'
    inp=dest/'bounded_diagnostic_input';out=dest/'bounded_diagnostic_output';inp.mkdir(exist_ok=True);out.mkdir(exist_ok=True)
    model=inp/'49_20192013_Western_North_Pacific_Watari_(2013).json';shutil.copy2(dest/'model.json',model)
    try:cpe.load_model(str(model))
    except Exception:(out/'load_traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
    summary=cpe.run_directory(str(inp),str(out),mc_samples=100,method_timeout=180)
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=False))
