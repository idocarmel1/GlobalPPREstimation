"""Refresh a workbook selection, or run a specifically requested regional stage."""
import argparse,sys,runpy,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.project_core.registry.discovery import project_root
from tools.project_core.calculations.selection import refresh_region
from tools.project_core.workbooks.read_session import ReadSession
from tools.project_core.workbooks.workbooks import sha
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='inspect':
        parser=argparse.ArgumentParser(description='Read one saved table; no full readiness or scientific review claim')
        parser.add_argument('operation',choices=['inspect']);parser.add_argument('--region',type=Path,required=True)
        parser.add_argument('--sheet',required=True);parser.add_argument('--table',required=True);a=parser.parse_args()
        path=a.region.resolve()
        if path.is_dir():path=path/(path.name+'.xlsx')
        fingerprint=sha(path);session=ReadSession();book=session.read(path,sheets=[a.sheet])
        if a.table not in book[a.sheet]:raise ValueError('Requested table is absent: '+a.table)
        session.assert_unchanged()
        if sha(path)!=fingerprint:raise ValueError('Workbook changed during scoped inspection')
        print(json.dumps({'scope':'saved table only; readiness not assessed','sha256':fingerprint,
                          'sheet':a.sheet,'table':a.table,'headers':book[a.sheet][a.table][0],
                          'rows':book[a.sheet][a.table][1]},ensure_ascii=False,indent=2,allow_nan=False))
    elif len(sys.argv)>1 and sys.argv[1]=='refresh':
        parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('operation',choices=['refresh']);parser.add_argument('--region',type=Path,required=True);a=parser.parse_args()
        print(json.dumps(refresh_region(project_root(a.region),a.region),ensure_ascii=False,indent=2))
    else:runpy.run_module('tools.project_core.calculations.run_region',run_name='__main__')
