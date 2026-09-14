"""A complete verified export survives Windows destination-open restrictions."""
import errno
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'PPRAtlas'))
import build_time_series
from atlas import render


def test_verified_time_series_replaces_existing_json_without_truncating_it(tmp_path, monkeypatch):
    (tmp_path / 'PPRAtlas/data').mkdir(parents=True)
    (tmp_path / 'data').mkdir()
    target = tmp_path / 'PPRAtlas/data/time_series.json'
    target.write_text('old verified export', encoding='utf-8')
    original_open = Path.open

    def restricted_open(path, mode='r', *args, **kwargs):
        if path == target and 'w' in mode:
            raise OSError(errno.EINVAL, 'existing destination cannot be truncated')
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', restricted_open)
    monkeypatch.setattr(build_time_series, 'ROOT', tmp_path)
    monkeypatch.setattr(build_time_series, 'build', lambda: ({'units': {}, 'name': 'Guénette'}, {
        'counts': {}, 'simple_annual_values_checked': 1, 'model_annual_values_checked': 1,
        'model_hashes_verified': 1, 'flagged_annual_values_excluded': 0, 'missing_catch': []}))
    monkeypatch.setattr(render, 'render_time_series', lambda _root: '<h1>Annual PPR</h1>')
    monkeypatch.setattr(sys, 'argv', ['build_time_series.py'])
    build_time_series.main()
    assert target.read_text(encoding='utf-8') == '{"units":{},"name":"Guénette"}'
    assert (tmp_path / 'PPRAtlas/trends.html').read_text(encoding='utf-8') == '<h1>Annual PPR</h1>'
