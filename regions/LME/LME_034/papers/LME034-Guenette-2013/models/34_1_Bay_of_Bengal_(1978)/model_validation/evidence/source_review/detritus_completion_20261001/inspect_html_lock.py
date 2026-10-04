"""Read-only Windows Restart Manager inventory of processes using trends.html."""
import ctypes,json
from ctypes import wintypes as w
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
class UNIQUE(ctypes.Structure):
    _fields_=[('pid',w.DWORD),('start',w.FILETIME)]
class INFO(ctypes.Structure):
    _fields_=[('process',UNIQUE),('app',w.WCHAR*256),('service',w.WCHAR*64),
        ('type',ctypes.c_int),('status',w.ULONG),('session',w.DWORD),('restartable',w.BOOL)]
api=ctypes.WinDLL('Rstrtmgr');session=w.DWORD();key=ctypes.create_unicode_buffer(33)
assert api.RmStartSession(ctypes.byref(session),0,key)==0
try:
    paths=(w.LPCWSTR*1)(str(ROOT/'interactive_map/trends.html'))
    assert api.RmRegisterResources(session,1,paths,0,None,0,None)==0
    required=w.UINT();count=w.UINT();reason=w.DWORD()
    status=api.RmGetList(session,ctypes.byref(required),ctypes.byref(count),None,ctypes.byref(reason))
    if status==234:
        entries=(INFO*required.value)();count.value=required.value
        status=api.RmGetList(session,ctypes.byref(required),ctypes.byref(count),entries,ctypes.byref(reason))
        result=[{'pid':entry.process.pid,'app':entry.app,'service':entry.service} for entry in entries[:count.value]]
    else: result=[]
    assert status==0,status
    print(json.dumps({'trends_file_lock_processes':result},ensure_ascii=False),flush=True)
finally:api.RmEndSession(session)
