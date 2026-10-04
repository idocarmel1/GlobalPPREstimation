"""Read-only SHA-256 verification of the relocated original NPP inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def contained(base: Path, relative: str) -> Path:
    candidate = (base / relative).resolve()
    if not candidate.is_relative_to(base.resolve()):
        raise ValueError(f'Path escapes source directory: {relative}')
    return candidate


def verify(root: Path, manifest: Path) -> dict:
    """Verify every manifest entry against bytes, not timestamps or filenames."""
    root = root.resolve()
    data = json.loads(manifest.read_text(encoding='utf-8'))
    raw = contained(root, data['raw_directory'])
    total = 0
    seen = set()
    for entry in data['files']:
        path = contained(raw, entry['path'])
        if path in seen:
            raise ValueError(f'Duplicate manifest path: {entry["path"]}')
        seen.add(path)
        if not path.is_file():
            raise ValueError(f'Missing source: {entry["path"]}')
        if path.stat().st_size != entry['bytes']:
            raise ValueError(f'Size mismatch: {entry["path"]}')
        with path.open('rb') as handle:
            actual = hashlib.file_digest(handle, 'sha256').hexdigest()
        if actual != entry['sha256']:
            raise ValueError(f'SHA-256 mismatch: {entry["path"]}')
        total += entry['bytes']
    return {'verified_files': len(seen), 'verified_bytes': total,
            'manifest': str(manifest.resolve()), 'raw_directory': str(raw)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args(argv)
    manifest = args.manifest or args.root / 'common_reference_data/npp/source_manifest.json'
    print(json.dumps(verify(args.root, manifest), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
