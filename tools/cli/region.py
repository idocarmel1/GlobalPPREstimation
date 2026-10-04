"""Refresh a workbook selection, or run a specifically requested regional stage."""
import argparse,sys,runpy,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.project_core.registry.discovery import project_root
from tools.project_core.calculations.selection import refresh_region
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='refresh':
        parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('operation',choices=['refresh']);parser.add_argument('--region',type=Path,required=True);a=parser.parse_args()
        print(json.dumps(refresh_region(project_root(a.region),a.region),ensure_ascii=False,indent=2))
    else:runpy.run_module('tools.project_core.calculations.run_region',run_name='__main__')
