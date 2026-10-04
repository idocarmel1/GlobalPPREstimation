"""Read Windows Restart Manager locking-process information; never stop apps."""
import ctypes
import json
from ctypes import wintypes
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
rm = ctypes.WinDLL("Rstrtmgr")
session = wintypes.DWORD()
key = ctypes.create_unicode_buffer(33)
started = rm.RmStartSession(ctypes.byref(session), 0, key)
if started:
    raise OSError(started, "RmStartSession")


class UniqueProcess(ctypes.Structure):
    _fields_ = [("dwProcessId", wintypes.DWORD), ("ProcessStartTime", wintypes.FILETIME)]


class ProcessInfo(ctypes.Structure):
    _fields_ = [("Process", UniqueProcess), ("strAppName", wintypes.WCHAR * 256),
                ("strServiceShortName", wintypes.WCHAR * 64), ("ApplicationType", ctypes.c_int),
                ("AppStatus", wintypes.ULONG), ("TSSessionId", wintypes.DWORD), ("bRestartable", wintypes.BOOL)]


try:
    filenames = (wintypes.LPCWSTR * 1)(str(ROOT / "Project.xlsx"))
    error = rm.RmRegisterResources(session, 1, filenames, 0, None, 0, None)
    if error:
        raise OSError(error, "RmRegisterResources")
    needed, count, reasons = wintypes.UINT(), wintypes.UINT(), wintypes.DWORD()
    error = rm.RmGetList(session, ctypes.byref(needed), ctypes.byref(count), None, ctypes.byref(reasons))
    output = {"initial_result": error, "required_process_count": needed.value}
    if error == 234:
        count = wintypes.UINT(needed.value)
        processes = (ProcessInfo * needed.value)()
        error = rm.RmGetList(session, ctypes.byref(needed), ctypes.byref(count), processes, ctypes.byref(reasons))
        output.update(final_result=error, processes=[{"pid": p.Process.dwProcessId, "app": p.strAppName,
                     "service": p.strServiceShortName, "restartable": bool(p.bRestartable)} for p in processes[:count.value]])
    print(json.dumps(output, ensure_ascii=False, indent=2))
    (HERE / "project_lock_inspection.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
finally:
    rm.RmEndSession(session)
