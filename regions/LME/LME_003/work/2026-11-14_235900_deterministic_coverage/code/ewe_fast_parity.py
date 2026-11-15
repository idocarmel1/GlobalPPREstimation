"""Bounded EwE derivative: exact slow-branch numerics without stored path lists.

Only the authenticated archived method body is accepted. No input, constructor,
efficiency definition, path enumeration, safety limit or summation order changes.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import textwrap

ROOT = next(path for path in Path(__file__).resolve().parents if (path/'Project.xlsx').is_file())
WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.scientific_helpers.sppr.ewe_path_optimization import (
    REPAIR, ACCEPTED_METHOD_HASH, digest, method_node, method_hash, repair_ewe_source)

def archived_source(unit):
    from tools.scientific_helpers.sppr import method_coverage as adapter
    inventory = json.loads((WORK/'inputs/validated_inventory.json').read_text(encoding='utf-8'))
    item = next(item for item in inventory['pairs'] if item['unit_id'] == unit)
    model = ROOT/item['model_dir']/'model.json'
    calculation = adapter._calculation_engine_path(item['flags'], model)
    path = calculation or ROOT/item['model_dir']/item['flags']['engine_sources']['PPRCalculator.py']
    expected = item['flags']['calculation_engine_sha256'] if calculation else item['flags']['engine_source_hashes']['PPRCalculator.py']
    if digest(path.read_bytes()) != expected:
        raise ValueError('Archived calculator bytes changed')
    return path.read_bytes().decode('utf-8-sig'), path


def repair_fast_source(source, *, force_fast=False):
    return repair_ewe_source(source, force_fast=force_fast)


def compile_method(source):
    import igraph as ig
    import numpy as np
    import pandas as pd
    from tqdm import tqdm
    namespace = {'ig': ig, 'np': np, 'pd': pd, 'tqdm': tqdm}
    body = textwrap.dedent(ast.get_source_segment(source, method_node(source)))
    exec(compile(body, '<authenticated EwE method>', 'exec'), namespace)
    return namespace['SPPR_EwE']


def check_california_matrix():
    """Read-only A comparison; no path enumeration, rerun, or source mutation."""
    import numpy as np
    from pandas.testing import assert_frame_equal
    from tools.scientific_helpers.sppr import method_coverage as adapter
    from tools.scientific_helpers.sppr.audited_runtime import decode_lossless
    import adopt_completion as adoption
    inventory = adoption.read(WORK/'inputs/validated_inventory.json')
    item = next(item for item in inventory['pairs'] if item['unit_id'] == 'LME_003')
    model = ROOT/item['model_dir']/'model.json'
    directory = model.parent/'results/diagnostics/method_coverage/deterministic_completion_20261114/calculated'
    cache = adoption.read(directory/'calculated.json')
    outcome = cache['methods']['EwE_TE_noEE']
    path = adoption.reference(directory, outcome['evidence'])
    document = adoption.read(path)
    identity = document['identity']
    consumed = adoption.authenticate_identity(identity, model)
    consumed[path] = adoption.sha(path)
    flags = identity['flags']
    constructor = adapter._constructor(flags, model)
    runtime, _, _ = adapter._load(model, constructor, flags)
    dc = runtime.get_DC(DET_as_PP=True)
    te = runtime.get_TE(TE_option='TE', as_matrix=True, DET_values=1)
    slow_a = (dc/te).fillna(0)
    returned = decode_lossless(document['return'])
    saved_a = returned[1]
    assert_frame_equal(slow_a, saved_a, check_exact=True)
    np.testing.assert_array_equal(np.signbit(slow_a.to_numpy()), np.signbit(saved_a.to_numpy()))
    adoption.check_hashes(consumed)
    return {'unit_id': 'LME_003', 'saved_method': 'EwE_TE_noEE', 'matrix_shape': list(slow_a.shape),
            'saved_A_matches_slow_semantics_exactly': True, 'scientific_method_executed': False,
            'model_sha256': adoption.sha(model), 'evidence_sha256': adoption.sha(path),
            'runtime_restoration': 'Authenticated recorded runtime; no constructor/normalization/EE-floor rerun',
            'finite_existing_method_preserved': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-california-matrix', action='store_true')
    parser.add_argument('--write-derivatives', action='store_true', help='Write preparation artifacts only under WORK/outputs')
    args = parser.parse_args()
    result = {}
    if args.check_california_matrix:
        result['california_matrix'] = check_california_matrix()
    if args.write_derivatives:
        for unit in ('LME_003', 'LME_034'):
            source, path = archived_source(unit)
            derived, certificate = repair_fast_source(source, force_fast=True)
            directory = WORK/'outputs/ew_e_optimized'/unit
            directory.mkdir(parents=True, exist_ok=True)
            target = directory/'PPRCalculator.py'
            target.write_bytes(derived.encode('utf-8'))
            certificate['base_path'] = path.relative_to(ROOT).as_posix()
            certificate['base_file_sha256'] = digest(path.read_bytes())
            (directory/'repair_manifest.json').write_text(json.dumps(certificate, indent=2), encoding='utf-8')
            result[unit] = {'derivative': target.relative_to(ROOT).as_posix(), **certificate}
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
