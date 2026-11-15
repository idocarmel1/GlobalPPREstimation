"""Authenticated EwE derivative preserving slow numerical semantics without path lists."""
from __future__ import annotations

import ast
import hashlib

REPAIR = 'ewe_slow_numeric_fast_v1'
ACCEPTED_METHOD_HASH = '25bc7b30b7e0f1720e8c60e588807c05de66cf5b50856ffa8a9ec26f2651bb7d'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def method_node(source):
    matches = [node for node in ast.walk(ast.parse(source))
               if isinstance(node, ast.FunctionDef) and node.name == 'SPPR_EwE']
    if len(matches) != 1:
        raise ValueError('Expected one authenticated SPPR_EwE body')
    return matches[0]


def method_hash(source):
    return digest(ast.dump(method_node(source), include_attributes=False).encode())


def repair_ewe_source(source, *, force_fast=True):
    """Return derived full source and its bounded numerical/output contract."""
    if method_hash(source) != ACCEPTED_METHOD_HASH:
        raise ValueError('Unauthenticated EwE scientific method body hash')
    node = method_node(source)
    before = ast.get_source_segment(source, node)
    after = before
    substitutions = [
        ('TE = TE.replace(0, np.nan).fillna(1.0)\n            A = (DC / TE).replace([np.inf, -np.inf], 0).fillna(0)',
         'A = (DC / TE).fillna(0)'),
        ('for start_idx in tqdm(range(num_nodes), disable=silent, desc="fetching paths"):\n',
         'for start_idx in tqdm(range(num_nodes), disable=silent, desc="fetching paths"):\n'
         '                if start_idx in terminal_indices:\n'
         '                    all_paths.append([start_idx])\n'
         '                    continue\n'),
        ('return pd.DataFrame(0.0, index=DC.index, columns=terminal_nodes), A',
         'empty = pd.DataFrame(0.0, index=DC.index, columns=terminal_nodes)\n'
         '                if use_EE:\n'
         "                    empty = empty.mul(self.EE, axis='index')\n"
         '                return empty, A, {}'),
        ('edge_starts = np.array(edge_starts)', 'edge_starts = np.array(edge_starts, dtype=int)'),
        ('edge_ends = np.array(edge_ends)', 'edge_ends = np.array(edge_ends, dtype=int)'),
    ]
    if force_fast:
        substitutions.append((
            'return _slow_EwE_with_paths(TE_option=TE_option, use_EE=use_EE, silent=silent, max_paths=max_paths)',
            'return _fast_EwE_no_paths(TE_option=TE_option, use_EE=use_EE, silent=silent, max_paths=max_paths)'))
    for old, new in substitutions:
        variants = list(dict.fromkeys((old, old.replace('\n', '\r\n'))))
        matches = [value for value in variants if value in after]
        if len(matches) != 1 or after.count(matches[0]) != 1:
            raise ValueError('Authenticated EwE replacement anchor changed')
        matched = matches[0]
        position = after.index(matched)
        end = after.find('\n', position)
        newline = '\r\n' if end > 0 and after[end - 1] == '\r' else '\n'
        after = after.replace(matched, new.replace('\n', newline), 1)
    derived = source.replace(before, after, 1)
    original_helpers = {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(method_node(source))
                        if isinstance(node, ast.FunctionDef) and node.name in ('_get_paths_with_safety_valve', '_slow_EwE_with_paths')}
    derived_helpers = {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(method_node(derived))
                       if isinstance(node, ast.FunctionDef) and node.name in original_helpers}
    if original_helpers != derived_helpers:
        raise ValueError('Derivative unexpectedly changed reference/enumeration helpers')
    certificate = {'repair': REPAIR, 'base_source_sha256': digest(source.encode('utf-8')),
        'derived_source_sha256': digest(derived.encode('utf-8')), 'base_method_ast_sha256': ACCEPTED_METHOD_HASH,
        'derived_method_ast_sha256': method_hash(derived), 'force_fast_for_original_call': force_fast,
        'numerical_contract': ['A = (DC / TE).fillna(0), including original zero/nonfinite semantics',
            'terminal self contribution is exactly 1 before unchanged EE multiplication',
            'original graph, terminal axes, path safety valve, max_paths and traversal order',
            'original vectorized segmented products and path-order scatter-add',
            'empty results preserve the original three-part return contract'],
        'omitted_evidence': 'Explicit named path lists are omitted; third return is {}. SPPR and A remain available.',
        'retained_methods': 'No existing finite EwE/noEE method result is replaced by preparing this derivative.'}
    return derived, certificate
