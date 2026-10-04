"""Operation-local workbook reuse checked against content, never timestamps."""
import copy
from pathlib import Path
from tools.project_core.workbooks.workbooks import read_book, sha


class ReadSession:
    """Return independent table dictionaries and recheck consumed bytes before use."""

    def __init__(self):
        self._cache = {}
        self._hashes = {}
        self._changed_inputs = set()
        self.read_count = 0
        self.parse_count = 0

    def read(self, path, *, sheets=None):
        path = Path(path).resolve()
        if isinstance(sheets, str):
            raise TypeError('sheets must be an iterable of worksheet names, not a string')
        selected = None if sheets is None else tuple(sorted(set(sheets)))
        key = (path, selected)
        self.read_count += 1
        fingerprint = sha(path)
        if self._hashes.get(path) != fingerprint:
            if path in self._hashes:
                self._changed_inputs.add(path)
            self._cache = {k: v for k, v in self._cache.items() if k[0] != path}
        if key not in self._cache:
            self.parse_count += 1
            value = read_book(path, sheets=selected)
            if sha(path) != fingerprint:
                self._changed_inputs.add(path)
                raise ValueError('Workbook changed while reading: ' + str(path))
            self._cache[key] = value
        self._hashes[path] = fingerprint
        return copy.deepcopy(self._cache[key])

    def assert_unchanged(self):
        """This guard supplements existing publication guards; it cannot replace them."""
        if self._changed_inputs:
            raise ValueError('Consumed workbook changed during this operation; start a new read session: '
                             + ', '.join(str(path) for path in sorted(self._changed_inputs)))
        for path, fingerprint in self._hashes.items():
            if not path.is_file() or sha(path) != fingerprint:
                self._changed_inputs.add(path)
                raise ValueError('Consumed workbook changed: ' + str(path))
