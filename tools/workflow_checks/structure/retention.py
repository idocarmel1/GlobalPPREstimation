"""Verify retained full bytes and require reasons for all explicit removals."""
import csv,hashlib
from pathlib import Path

def verify_retention(root):
    root=Path(root).resolve();kept=removed=0
    with (root/'common_reference_data/provenance/source_paths.csv').open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            if row.get('action')=='directory_navigation':continue
            relative=row['retained_path']
            if not relative:
                if not row.get('reason') or 'removed' not in row.get('action',''):raise AssertionError('Retention mismatch: removal requires explicit disposition')
                removed+=1;continue
            path=(root/relative).resolve()
            if not path.is_relative_to(root) or not path.is_file():raise AssertionError('Retention mismatch: '+relative)
            expected=row.get('retained_sha256') or row.get('sha256')
            if expected and hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise AssertionError('Retention mismatch: '+relative)
            kept+=1
    return kept,removed
