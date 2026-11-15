"""Read-only handle diagnosis plus an explicitly owned sibling replacement probe."""
import ctypes
from ctypes import wintypes as wt
import hashlib
import json
import os
from pathlib import Path
import sys

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
TARGET = ROOT / 'regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014/results/regional_snapshot.xlsx'
k = ctypes.WinDLL('kernel32', use_last_error=True)
k.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.HANDLE]
k.CreateFileW.restype = wt.HANDLE
k.CloseHandle.argtypes = [wt.HANDLE]

def probe():
    handle = k.CreateFileW(str(TARGET), 0x10000, 7, None, 3, 0, None)
    if handle == ctypes.c_void_p(-1).value:
        return {'delete_access': False, 'error': ctypes.get_last_error()}
    k.CloseHandle(handle)
    return {'delete_access': True}

class UniqueProcess(ctypes.Structure):
    _fields_ = [('pid', wt.DWORD), ('start', wt.FILETIME)]

class ProcessInfo(ctypes.Structure):
    _fields_ = [('process', UniqueProcess), ('app', wt.WCHAR * 256),
                ('service', wt.WCHAR * 64), ('type', ctypes.c_int),
                ('status', wt.ULONG), ('session', wt.DWORD), ('restartable', wt.BOOL)]

def holders():
    rm = ctypes.WinDLL('rstrtmgr')
    session = wt.DWORD(); key = ctypes.create_unicode_buffer(33)
    code = rm.RmStartSession(ctypes.byref(session), 0, key)
    if code: return {'start_error': code}
    try:
        files = (wt.LPCWSTR * 1)(str(TARGET))
        code = rm.RmRegisterResources(session, 1, files, 0, None, 0, None)
        if code: return {'register_error': code}
        needed = wt.UINT(); count = wt.UINT(); reasons = wt.DWORD()
        code = rm.RmGetList(session, ctypes.byref(needed), ctypes.byref(count), None, ctypes.byref(reasons))
        if code not in (0, 234): return {'list_error': code}
        if not needed.value: return []
        items = (ProcessInfo * needed.value)(); count.value = needed.value
        code = rm.RmGetList(session, ctypes.byref(needed), ctypes.byref(count), items, ctypes.byref(reasons))
        if code: return {'list_error': code}
        return [{'pid': x.process.pid, 'app': x.app, 'service': x.service} for x in items[:count.value]]
    finally:
        rm.RmEndSession(session)

report = {'before': probe(), 'holders_before': holders(), 'attributes': TARGET.stat().st_file_attributes, 'pid': os.getpid()}
print(json.dumps(report), flush=True)
if '--handles-only' in sys.argv:
    (WORK / 'qa/windows_handles_unsandboxed.json').write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0)
from tools.project_core.workbooks.workbooks import read_book
for i in range(2):
    read_book(TARGET)
    report['after_read_' + str(i)] = probe()
    print('read completed ' + str(i), flush=True)
report['holders_after'] = holders()
q = TARGET.parent / 'checkpoint_atomic_probe_owned.tmp'
t = TARGET.parent / 'checkpoint_atomic_probe_owned.new'
assert not q.exists() and not t.exists()
q.write_bytes(b'before'); t.write_bytes(b'after'); os.replace(t, q)
report['sibling_replace_passed'] = q.read_bytes() == b'after'
report['fixture'] = {'path': q.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(q.read_bytes()).hexdigest()}
(WORK / 'qa/windows_replace_diagnosis.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2), flush=True)
