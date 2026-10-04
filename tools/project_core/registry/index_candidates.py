"""Derive registered paths from canonical discovery without copying extractions."""
import argparse
from pathlib import Path
from tools.project_core.registry.discovery import discover_regions,discover_models
from tools.project_core.workbooks.workbooks import read_book,records,update_book
from tools.project_core.registry.writes import central_lock

def index(root):
    with central_lock(root):return _index(root)

def _index(root):
    root=Path(root);book=read_book(root/'Project.xlsx');h,rows=book['Models & coverage']['Models']
    registered={(r['unit_id'],r['model_id']) for r in records(book,'Models & coverage','Models')}
    current={(unit,mid):path for unit,workbook in discover_regions(root).items() for mid,path in discover_models(workbook.parent).items()}
    missing=set(current)-registered
    if missing:raise ValueError('Scientific registration required; no metadata guessed: '+str(sorted(missing)))
    for row in rows:
        record=dict(zip(h,row));key=(record['unit_id'],record['model_id'])
        if key not in current:raise ValueError('Registered model is unavailable: '+str(key))
        row[h.index('model_path')]=current[key].relative_to(root).as_posix()
    update_book(root/'Project.xlsx',book)
    return len(current)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True)
    print('Canonical registered models:',index(parser.parse_args().root))
