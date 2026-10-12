"""Rollback generated coverage and publication together, preserving author races."""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
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


class PublicationBackup:
    def __init__(self, root, extra_region_paths=(), extra_model_dirs=()):
        self.root = Path(root).resolve()
        self.project = self.root / 'Project.xlsx'
        self.authoritative = {self.project, *(self._path(path) for path in extra_region_paths)}
        self.artifacts = set()
        self.generated_directories = [self.root / 'interactive_map']
        with ZipFile(self.project) as archive:
            models = [row for _, row in table_rows(archive, 'Models & coverage', 'Models')[3]
                      if row.get('researcher_review_status') == 'Validated by researcher']
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
def publication_transaction(root, extra_region_paths=(), extra_model_dirs=()):
    backup = PublicationBackup(root, extra_region_paths, extra_model_dirs)
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
