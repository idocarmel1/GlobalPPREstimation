"""Simulate a human write between refresh's read and preflight hashes, in a fixture."""
import sys,json
from pathlib import Path
from unittest.mock import patch
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
from tools.workflow_checks.selection.test_selection_refresh import SelectionTests
from tools.project_core.calculations import selection
from tools.project_core.workbooks.workbooks import read_book,update_book,overview
from tools.project_core.calculations.regional import set_setting
f=SelectionTests();f.setUp();real_read=read_book;edited=False
def human_after_read(path):
    global edited
    b=real_read(path)
    if Path(path)==f.path and not edited:
        edited=True
        latest=real_read(path);set_setting(latest,'researcher_note','new human edit arriving during refresh');update_book(path,latest)
    return b
try:
    with patch.object(selection,'read_book',human_after_read):
        result=selection.refresh_region(f.root,f.path,publisher=f.publish)
    finding={'result':result,'researcher_note_after_refresh':overview(real_read(f.path)).get('researcher_note')}
    Path(__file__).with_name('concurrent_edit_result.json').write_text(json.dumps(finding,indent=2),encoding='utf-8');print(json.dumps(finding,indent=2))
finally:f.tearDown()
