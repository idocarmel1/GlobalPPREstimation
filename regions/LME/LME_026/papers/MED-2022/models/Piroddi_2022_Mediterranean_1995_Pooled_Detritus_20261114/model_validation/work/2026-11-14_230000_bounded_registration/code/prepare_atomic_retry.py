from pathlib import Path
import difflib
run=Path(__file__).resolve().parents[1];root=next(p for p in run.parents if (p/'Project.xlsx').is_file())
old=(root/'tools/project_core/maps/build_html.py').read_text(encoding='utf-8')
start=old.index('def atomic_bytes(path,data):');end=old.index('\ndef relayout(',start)
helper='''def atomic_bytes(path,data):
    from tools.project_core.registry.publication import publication_write
    import time
    path=Path(path)
    def fingerprint():return sha(path) if path.is_file() else None
    original=fingerprint();expected=hashlib.sha256(data).hexdigest()
    path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent,suffix=path.suffix);os.close(fd)
    try:
        Path(tmp).write_bytes(data)
        for attempt in range(6):
            replaced=False
            try:
                with publication_write(path,fingerprint=expected):
                    if fingerprint()!=original:raise ValueError('Publication target changed during replacement retry: '+str(path))
                    os.replace(tmp,path)
                    replaced=True
                break
            except PermissionError as error:
                # Retry only failed Windows replacements, never a post-write
                # guard failure, a changed target, or another permission error.
                if replaced:raise
                if fingerprint()!=original:raise ValueError('Publication target changed during replacement retry: '+str(path)) from error
                if getattr(error,'winerror',None) not in {5,32,33} or attempt==5:raise
                time.sleep(.2*(2**attempt))
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

'''
new=old[:start]+helper+old[end:];compile(new,'atomic retry proposal','exec')
(run/'outputs/build_html.atomic_retry.proposed.py').write_text(new,encoding='utf-8')
(run/'outputs/atomic_replace_retry.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/tools/project_core/maps/build_html.py',tofile='b/tools/project_core/maps/build_html.py')),encoding='utf-8')
# Compose only the same helper into the existing exact-pair proposal; no other
# source rebasing and no shared installation. Its original diff remains usable.
prior=(run/'outputs/build_html.proposed.py').read_text(encoding='utf-8')
a=prior.index('def atomic_bytes(path,data):');b=prior.index('\ndef relayout(',a)
combined=prior[:a]+helper+prior[b:];compile(combined,'combined proposal','exec')
(run/'outputs/build_html.combined.proposed.py').write_text(combined,encoding='utf-8')
(run/'outputs/build_html.combined.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),combined.splitlines(True),fromfile='a/tools/project_core/maps/build_html.py',tofile='b/tools/project_core/maps/build_html.py')),encoding='utf-8')
