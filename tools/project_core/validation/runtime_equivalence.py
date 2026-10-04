"""Verify retained runtime evidence without replacing historical input hashes."""
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
from tools.project_core.registry.discovery import project_root
from tools.project_core.registry.paths import SourcePaths


# Human-authorized runtime rebalancing may change these fields. ``growth`` is
# PPRCalculator's alias for biomass_accum; unrelated production/consumption,
# mortality, routing and diet values remain part of the comparison.
RUNTIME_IGNORED_FIELDS = frozenset({'biomass_accum', 'biomass_accum_rate', 'growth', 'predation'})


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inside(root, relative):
    if Path(relative).is_absolute():
        raise ValueError('Evidence path must be relative')
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Evidence missing or outside allowed root')
    return path


def _checked(root, record):
    path = _inside(root, record['path'])
    if _sha(path) != record['sha256']:
        raise ValueError('Evidence identity changed')
    return path


def _numeric_equal(a, b, atol):
    try:
        x, y = float(a), float(b)
    except (ValueError, TypeError):
        return a == b
    if math.isnan(x) or math.isnan(y):
        return math.isnan(x) and math.isnan(y)
    return math.isfinite(x) and math.isfinite(y) and abs(x - y) <= atol


def _csv_equal(before, after, atol, ignored_fields=()):
    with before.open(encoding='utf-8', newline='') as f:
        left = list(csv.reader(f))
    with after.open(encoding='utf-8', newline='') as f:
        right = list(csv.reader(f))
    if len(left) < 2 or len(left) != len(right) or left[0] != right[0]:
        return False
    headers = left[0]
    if len(headers) != len(set(headers)):
        return False
    for rows in (left[1:], right[1:]):
        if len({r[0] for r in rows}) != len(rows):
            return False
        if any(len(r) != len(headers) for r in rows):
            return False
    text_columns = {'group_name', 'trophic_info', 'taxon_descr', 'model_name'}
    for a, b in zip(left[1:], right[1:]):
        if a[0] != b[0]:
            return False
        for header, x, y in zip(headers[1:], a[1:], b[1:]):
            if header in ignored_fields:
                continue
            if header in text_columns:
                if x != y:
                    return False
            elif not _numeric_equal(x, y, atol):
                return False
    return True


def _source_state(data):
    """Separate numeric diet/import rows from exact non-diet structure/values."""
    rest = copy.deepcopy(data)
    diets = {}
    for group in rest['group']:
        for field in RUNTIME_IGNORED_FIELDS:
            group.pop(field, None)
        seq = str(group['group_seq'])
        if seq in diets:
            raise ValueError('Duplicate consumer ID')
        row = {'import': float(group.pop('diet_imp', '0'))}
        description = group.get('diet_descr') or {}
        entries = description.get('diet') or []
        entries = entries if isinstance(entries, list) else [entries]
        for entry in entries:
            prey = str(entry['prey_seq'])
            if prey in row:
                raise ValueError('Duplicate prey ID')
            row[prey] = float(entry.pop('proportion'))
        if any(not math.isfinite(v) or v < 0 for v in row.values()):
            raise ValueError('Unresolved or invalid source diet')
        total = sum(row.values())
        diets[seq] = {k: v / total if total else v for k, v in row.items()}
    return rest, diets


def verified_runtime_equivalence(region_folder, model_path, historical_hash):
    """Fail closed unless pinned execution evidence proves a diet-only equivalent.

    The certificate is evidence, not review approval. All files are rehashed on
    every use; source diets are independently compared after normalization, and
    non-diet JSON values, topology and labels must remain exactly unchanged,
    except the human-authorized biomass-accumulation/predation fields.
    """
    try:
        region = Path(region_folder).resolve()
        model = Path(model_path).resolve()
        if not model.is_relative_to(region):
            return False
        cert_path = _inside(region, (model.parent / 'runtime_equivalence.json').relative_to(region))
        certificate = json.loads(cert_path.read_text(encoding='utf-8'))
        if certificate['schema_version'] != 1 or certificate['atol'] != 1e-12 or certificate['rtol'] != 0:
            return False
        if _inside(region, certificate['model_path']) != model:
            return False
        if certificate['before_model']['sha256'] != historical_hash:
            return False
        old = _checked(region, certificate['before_model'])
        if _sha(model) != certificate['after_model_sha256']:
            return False
        if certificate['settings'].get('normalize_DC') is not True:
            return False
        proof_path = _checked(region, certificate['settings_evidence'])
        proof = json.loads(proof_path.read_text(encoding='utf-8'))
        if proof['settings'] != certificate['settings']:
            return False
        if proof['canonical_before_sha256'] != historical_hash or proof['canonical_after_sha256'] != _sha(model):
            return False
        if not certificate['code_files'] or not certificate['evidence_files']:
            return False
        executed = proof['loader_code_hashes']
        declared = {Path(r['path']).name: r['sha256'] for r in certificate['code_files']}
        if len(declared) != len(certificate['code_files']) or declared != executed:
            return False
        project = project_root(region)
        loader_text = proof['actual_loader_path'].replace('\\', '/')
        loader = Path(loader_text)
        # Retained Windows execution logs remain portable: remap only the exact
        # region-first repository suffix, never an arbitrary outside directory.
        if loader.is_absolute() or (len(loader_text) > 2 and loader_text[1] == ':'):
            parts = loader_text.split('/')
            marker = parts.index('regions')
            if region.name not in parts[marker + 1:marker + 3]:
                return False
            loader = Path(*parts[marker:])
        loader = SourcePaths(project).resolve(loader.as_posix())
        if loader is None:return False
        executed_folder = _inside(project, loader).parent
        for record in certificate['code_files']:
            if _checked(project, record).parent != executed_folder:
                return False
        for record in certificate['evidence_files']:
            _checked(region, record)
        left, before_diet = _source_state(json.loads(old.read_text(encoding='utf-8')))
        right, after_diet = _source_state(json.loads(model.read_text(encoding='utf-8')))
        if left != right or before_diet.keys() != after_diet.keys():
            return False
        for consumer in before_diet:
            a, b = before_diet[consumer], after_diet[consumer]
            if a.keys() != b.keys() or any(not _numeric_equal(a[k], b[k], 1e-12) for k in a):
                return False
        if set(certificate['components']) != {'normalized_DC', 'loaded_groups', 'detritus_fate'}:
            return False
        proof_root = (region / certificate['execution_evidence_root']).resolve()
        if proof_root != proof_path.parent:
            return False
        runtime_files = {k.replace('\\', '/'): v for k, v in proof['runtime_files'].items()}
        for name, component in certificate['components'].items():
            for variant in ('before', 'after'):
                expected = f'runtime_{variant}/{name}.csv'
                record = component[variant]
                actual = _checked(region, record)
                if actual != _inside(region, (proof_root / expected).relative_to(region)):
                    return False
                if runtime_files[expected] != record['sha256']:
                    return False
            if not _csv_equal(_checked(region, component['before']),
                              _checked(region, component['after']), 1e-12,
                              RUNTIME_IGNORED_FIELDS if name == 'loaded_groups' else ()):
                return False
        return True
    except (OSError, ValueError, TypeError, KeyError, IndexError, OverflowError, AttributeError):
        return False
