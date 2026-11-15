"""Rollback generated coverage and publication together, preserving author races."""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import json
import os
import time
from pathlib import Path
from zipfile import ZipFile

from tools.project_core.registry.discovery import region_directory, resolve_model
from tools.project_core.validation.researcher_review import table_rows
from tools.project_core.workbooks.workbooks import sha

_ACTIVE = ContextVar('publication_backups', default=())


class PublicationConflictError(ValueError, RuntimeError):
    """An invalidated input and a failed rollback, without losing either cause."""


def _fingerprint(path):
    return sha(path) if path.is_file() else None


def _replacement_access(path):
    """Diagnose current Windows delete permission and this process's readers."""
    result = {'delete_access': False, 'own_open_handles': None, 'pid': os.getpid()}
    if os.name != 'nt' or not path.is_file(): return result
    import ctypes
    from ctypes import wintypes as wt
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.HANDLE]
    kernel.CreateFileW.restype = wt.HANDLE
    kernel.CloseHandle.argtypes = [wt.HANDLE]
    handle = kernel.CreateFileW(str(path), 0x10000, 7, None, 3, 0, None)
    if handle == ctypes.c_void_p(-1).value:
        result['native_error'] = ctypes.get_last_error()
    else:
        kernel.CloseHandle(handle); result['delete_access'] = True
    result['attributes'] = path.stat().st_file_attributes
    try:
        import psutil
        result['own_open_handles'] = [x.path for x in psutil.Process().open_files()
                                      if os.path.normcase(x.path) == os.path.normcase(str(path))]
    except (ImportError, OSError):
        pass
    return result


def guarded_replace(staged, destination, *, expected_sha256):
    """Replace exact bytes and claim them even if replacement raises afterwards.

    A configured publication journal is flushed before the OS call. Recovery
    can recognize only the intended postimage, never an arbitrary current file.
    At most two retries follow a denial, only while native delete access is
    available, no own reader is open, and exact target/staged hashes still match.
    """
    staged, destination = Path(staged).resolve(), Path(destination).resolve()
    after = _fingerprint(staged)
    if after is None or _fingerprint(destination) != expected_sha256:
        raise ValueError('Atomic replacement precondition changed: ' + str(destination))
    backups = _ACTIVE.get()
    for backup in backups:
        backup.before_write(destination)
        journal = getattr(backup, 'journal_path', None)
        if journal:
            record = {'event': 'intent', 'path': destination.relative_to(backup.root).as_posix(),
                      'before_sha256': expected_sha256, 'after_sha256': after}
            with Path(journal).open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(record, sort_keys=True) + '\n')
                stream.flush(); os.fsync(stream.fileno())
    if _fingerprint(destination) != expected_sha256 or _fingerprint(staged) != after:
        raise ValueError('Atomic replacement changed after journaling: ' + str(destination))
    try:
        for attempt in range(3):
            try:
                os.replace(staged, destination)
                break
            except PermissionError as error:
                # Inspect the live condition before unwinding loses its owner.
                state = _replacement_access(destination)
                for backup in backups:
                    journal = getattr(backup, 'journal_path', None)
                    if journal:
                        with Path(journal).open('a', encoding='utf-8') as stream:
                            stream.write(json.dumps({'event': 'replacement_denial',
                                'path': destination.relative_to(backup.root).as_posix(),
                                'attempt': attempt + 1, 'winerror': getattr(error, 'winerror', None),
                                'access': state}, sort_keys=True) + '\n')
                            stream.flush(); os.fsync(stream.fileno())
                if _fingerprint(destination) != expected_sha256 or _fingerprint(staged) != after:
                    raise ValueError('Atomic replacement changed during denial: ' + str(destination)) from error
                if attempt == 2 or not state['delete_access'] or state['own_open_handles'] != []:
                    raise
                time.sleep(0.15 * (attempt + 1))
                if _fingerprint(destination) != expected_sha256 or _fingerprint(staged) != after:
                    raise ValueError('Atomic replacement changed before retry: ' + str(destination)) from error
    finally:
        # An OS replacement may have completed before an exception/interrupt.
        # An external edit after that replacement is deliberately not claimed.
        if _fingerprint(destination) == after:
            for backup in backups:
                backup._claim(destination, after)
    if _fingerprint(destination) != after:
        raise ValueError('Atomic output changed after replacement: ' + str(destination))


class PublicationBackup:
    def __init__(self, root, extra_region_paths=(), extra_model_dirs=(), *,
                 units=None, model_pairs=None, all_validated=False):
        self.root = Path(root).resolve()
        self.project = self.root / 'Project.xlsx'
        self.authoritative = {self.project, *(self._path(path) for path in extra_region_paths)}
        self.artifacts = set()
        self.generated_directories = [self.root / 'interactive_map']
        from tools.project_core.calculations.coverage import scoped_validated_metadata
        units = None if units is None else set(units)
        model_pairs = None if model_pairs is None else {tuple(pair) for pair in model_pairs}
        scope = dict(units=units, model_pairs=model_pairs, all_validated=all_validated)
        scoped_validated_metadata([], **scope)
        models = []
        if all_validated or units or model_pairs:
            with ZipFile(self.project) as archive:
                models = scoped_validated_metadata(
                    [row for _, row in table_rows(archive, 'Models & coverage', 'Models')[3]], **scope)
        self.models = models
        model_dirs = {self._path(path) for path in extra_model_dirs}
        for metadata in models:
            region = region_directory(self.root, metadata['unit_id'])
            model = resolve_model(region, metadata['model_id']).parent
            self.authoritative.add(region / (metadata['unit_id'] + '.xlsx'))
            model_dirs.add(model)
        for model in model_dirs:
            self.artifacts.update([model / 'sppr_source.xlsx', model / 'results/regional_snapshot.xlsx',
                                   model / 'results/result_manifest.json'])
            self.generated_directories.append(model / 'results/diagnostics/method_coverage')
            self.generated_directories.append(model / 'results/diagnostics/ee_floor')
        for directory in self.generated_directories:
            if directory.is_dir():
                self.artifacts.update(path for path in directory.rglob('*') if path.is_file())
        self.before = {path: path.read_bytes() if path.is_file() else None
                       for path in self.authoritative | self.artifacts}
        self.owned = {path: _fingerprint(path) for path in self.before}

    def _path(self, value):
        path = Path(value)
        return (path if path.is_absolute() else self.root / path).resolve()

    def _claim(self, path, fingerprint):
        if path not in self.before:
            if not any(path.is_relative_to(directory) for directory in self.generated_directories):
                raise ValueError('Publication cannot claim an untracked write: ' + str(path))
            # Existing directory contents were captured on entry. A guarded
            # coverage executor may return a newly created evidence file.
            self.before[path] = None
        self.owned[path] = fingerprint

    def checkpoint(self, paths=(), *, fingerprints=None):
        """Claim exact guarded writes, using produced hashes when supplied."""
        supplied = {self._path(path): value for path, value in (fingerprints or {}).items()}
        targets = _ACTIVE.get() if self in _ACTIVE.get() else (self,)
        for value in paths:
            path = self._path(value)
            fingerprint = supplied[path] if path in supplied else _fingerprint(path)
            for backup in targets:
                backup._claim(path, fingerprint)
            if _fingerprint(path) != fingerprint:
                raise ValueError('Publication output changed after its guarded write: ' + str(path))

    def before_write(self, path):
        """Check a page or snapshot immediately before its atomic replacement."""
        if path not in self.before:
            self.before[path] = path.read_bytes() if path.is_file() else None
            self.owned[path] = _fingerprint(path)
        if _fingerprint(path) != self.owned[path]:
            raise ValueError('Publication input changed before replacement: ' + str(path))

    def rollback(self):
        conflicts = []
        for path, prior in self.before.items():
            present = path.read_bytes() if path.is_file() else None
            if present == prior:
                continue
            actual = _fingerprint(path)
            if actual != self.owned[path]:
                conflicts.append(str(path))
                continue
            if prior is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(prior)
            restored = hashlib.sha256(prior).hexdigest() if prior is not None else None
            for backup in _ACTIVE.get():
                if backup is not self and backup.owned.get(path) == actual:
                    backup.owned[path] = restored
        if conflicts:
            raise PublicationConflictError('Publication failed; concurrent author edits were preserved: ' + ', '.join(conflicts))


@contextmanager
def publication_transaction(root, extra_region_paths=(), extra_model_dirs=(), *,
                            units=None, model_pairs=None, all_validated=False):
    backup = PublicationBackup(root, extra_region_paths, extra_model_dirs,
        units=units, model_pairs=model_pairs, all_validated=all_validated)
    token = _ACTIVE.set((*_ACTIVE.get(), backup))
    try:
        yield backup
    except Exception as error:
        try:backup.rollback()
        except PublicationConflictError as conflict:
            raise PublicationConflictError(str(error)+'; '+str(conflict)) from error
        raise
    finally:
        _ACTIVE.reset(token)


@contextmanager
def publication_write(path, *, fingerprint=None):
    """Journal one exact atomic page/snapshot write in every enclosing batch."""
    path = Path(path).resolve()
    backups = _ACTIVE.get()
    for backup in backups:
        backup.before_write(path)
    yield
    fingerprint = fingerprint if fingerprint is not None else _fingerprint(path)
    for backup in backups:
        backup.owned[path] = fingerprint
    if _fingerprint(path) != fingerprint:
        raise ValueError('Publication output changed after replacement: ' + str(path))
