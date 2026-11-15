"""Checked, pure source transformation for separately pinned engine derivatives.

The caller preserves the original source, authenticates it, writes the returned
derivative separately and records both hashes. This module never executes or
writes an engine and does not change scientific inputs or runtime settings.
"""
from __future__ import annotations

import ast
import hashlib


HELPERS = '''    def _group_sppr_symbols(self, seq, prefix):
        """Create one literal symbol per group; punctuation is part of its name."""
        names = [f'{prefix}_{self.seq2name[s]}'.replace(' ', '_') for s in seq]
        if len(names) != len(set(names)):
            raise ValueError('Symbolic group labels must remain distinct after space replacement')
        return [sm.Symbol(name) for name in names]

    @staticmethod
    def _eval_symbolic_substitutions(expression, substitutions):
        """Leave free identity variables free instead of recursing in evalf."""
        effective = {key: value for key, value in substitutions.items()
                     if sm.simplify(value - key) != 0}
        return expression.evalf(subs=effective)

'''

# Keep the v1 recipe byte-identical: existing derivatives authenticate against it.
HELPERS_V2 = HELPERS.replace('if sm.simplify(value - key) != 0}',
                            'if value != key and (value - key).is_zero is not True}')
HELPERS_BY_VERSION = {'symbolic_repairs_v1': HELPERS, 'symbolic_repairs_v2': HELPERS_V2}

ALIGNMENT = '''        if not non_DET_sppr.index.equals(SPPR_combined_raw.index):
            raise ValueError('Detritus basis recipient axes differ')
        omitted = m_eff.index.difference(non_DET_sppr.index)
        if len(omitted):
            weights = m_eff.loc[omitted]
            if not (np.isfinite(weights).all() and (weights == 0).all()):
                raise ValueError('Detritus collapse has unrepresented nonzero recipient weights: '
                                 + repr(omitted.tolist()))
        if len(non_DET_sppr.index.difference(m_eff.index)):
            raise ValueError('Detritus collapse is missing recipient weights')
        m_eff = m_eff.reindex(non_DET_sppr.index)
'''

TARGETS = ('_SPPR_symbolic_helper_diet_import_as_PP',
           '_SPPR_symbolic_helper_diet_import_as_DC', '_collapse_det_scaling')


def _methods(source):
    classes = [node for node in ast.parse(source).body
               if isinstance(node, ast.ClassDef) and node.name == 'PPRCalculator']
    if len(classes) != 1:
        raise ValueError('Engine source pattern requires one PPRCalculator class')
    return {node.name: node for node in classes[0].body if isinstance(node, ast.FunctionDef)}


def _replace(source, old, new, count=1):
    if source.count(old) != count:
        raise ValueError('Engine source pattern differs: ' + old[:100])
    return source.replace(old, new)


def repair_symbolic_source(source: str, *, repair='symbolic_repairs_v1'):
    """Return minimally repaired source and its content-addressed change record.

    Unknown/partial source patterns fail closed. Already repaired sources return
    unchanged only when both helper implementations and the guard match exactly.
    """
    if repair not in HELPERS_BY_VERSION:
        raise ValueError('Unknown symbolic repair version')
    helpers = HELPERS_BY_VERSION[repair]
    original = source
    normalized = source.replace('\r\n', '\n')
    methods = _methods(source)
    if any(name not in methods for name in TARGETS):
        raise ValueError('Engine source pattern lacks a required symbolic method')
    added = {'_group_sppr_symbols', '_eval_symbolic_substitutions'}
    changed_methods = []
    if added & methods.keys():
        existing_version = next((version for version, block in HELPERS_BY_VERSION.items()
                                 if block in normalized), None)
        if (not added.issubset(methods) or existing_version is None or ALIGNMENT not in normalized
                or (repair == 'symbolic_repairs_v1' and existing_version != repair)):
            raise ValueError('Partially repaired engine source pattern is unsupported')
        expected_counts = {"self._group_sppr_symbols(Regular_seq, 'SPPR')": 2,
                           "self._group_sppr_symbols(DET_seq, 'SPPR')": 2,
                           "self._group_sppr_symbols(PP_seq, 'SPPR')": 2,
                           "self._group_sppr_symbols(Import_seq, 'SPPR')": 1,
                           "self._group_sppr_symbols(index, 'DIET_SPPR')": 1,
                           'self._eval_symbolic_substitutions(x, subs_dict)': 3,
                           'self._eval_symbolic_substitutions(sol_dict2[det_sym], subs_dict)': 2}
        if any(source.count(text) != count for text, count in expected_counts.items()):
            raise ValueError('Repaired engine source pattern is incomplete')
        changes = []
        if existing_version != repair:
            old = HELPERS_BY_VERSION[existing_version]
            newline = '\n' if old in source else '\r\n'
            source = _replace(source, old.replace('\n', newline), helpers.replace('\n', newline))
            current = _methods(source)
            changed = {name for name in methods if ast.dump(methods[name]) != ast.dump(current[name])}
            if changed != {'_eval_symbolic_substitutions'} or set(current) != set(methods):
                raise ValueError('Symbolic version upgrade changed an unexpected method')
            changes = ['conservative_identity_substitution_filter']
            changed_methods = ['_eval_symbolic_substitutions']
    else:
        lines = source.splitlines(keepends=True)
        replacements = []
        for name in TARGETS:
            node = methods[name]
            old = ''.join(lines[node.lineno - 1:node.end_lineno])
            newline = '\r\n' if old.count('\r\n') > old.count('\n') / 2 else '\n'
            updated = old.replace('\r\n', '\n')
            if name == '_collapse_det_scaling':
                updated = _replace(updated, '        a = float(m_eff @ non_DET_sppr)',
                                   ALIGNMENT + '        a = float(m_eff @ non_DET_sppr)')
            else:
                anchor = ('equations = A @ sppr_vec - sppr_vec' if name.endswith('_PP') else
                          'equations = ((A.loc[index, index] @ sppr_vec).squeeze() + '
                          '(A.loc[index, Import_seq] * diet_sppr_vec).squeeze()) - sppr_vec.squeeze()')
                if updated.count(anchor) != 1:
                    raise ValueError('Symbolic equation source pattern differs')
                groups = ['Regular_seq', 'DET_seq', 'PP_seq']
                if name.endswith('_PP'):
                    groups.append('Import_seq')
                for group in groups:
                    updated = _replace(updated,
                        "sm.symbols([f'SPPR_{self.seq2name[s]}'.replace(' ', '_') for s in " + group + '])',
                        "self._group_sppr_symbols(" + group + ", 'SPPR')")
                if name.endswith('_DC'):
                    updated = _replace(updated,
                        "sm.symbols([f'DIET_SPPR_{self.seq2name[s]}'.replace(' ', '_') for s in index])",
                        "self._group_sppr_symbols(index, 'DIET_SPPR')")
                updated = _replace(updated, 'x.evalf(subs=subs_dict)',
                    'self._eval_symbolic_substitutions(x, subs_dict)', 1 if name.endswith('_PP') else 2)
                updated = _replace(updated, 'sol_dict2[det_sym].evalf(subs=subs_dict)',
                    'self._eval_symbolic_substitutions(sol_dict2[det_sym], subs_dict)')
                if name.endswith('_PP'):
                    updated = helpers + updated
            if newline == '\r\n':
                updated = updated.replace('\n', '\r\n')
            replacements.append((node.lineno - 1, node.end_lineno, updated))
        for start, end, updated in sorted(replacements, reverse=True):
            lines[start:end] = [updated]
        source = ''.join(lines)
        current = _methods(source)
        changed = {name for name in methods
                   if ast.dump(methods[name]) != ast.dump(current[name])}
        if changed != set(TARGETS) or set(current) - set(methods) != added:
            raise ValueError('Engine repair changed an unexpected method')
        changes = ['literal_group_symbols', 'identity_substitution_filter',
                   'zero_weight_recipient_alignment']
        if repair == 'symbolic_repairs_v2':
            changes[1] = 'conservative_identity_substitution_filter'
        changed_methods = list(TARGETS)
    digest = lambda text: hashlib.sha256(text.encode('utf-8')).hexdigest()
    return source, {'schema_version': 1, 'repair': repair,
                    'original_sha256': digest(original), 'derived_sha256': digest(source),
                    'changes': changes, 'changed_methods': changed_methods,
                    'source_preserved': True,
                    'nonzero_unrepresented_recycling': 'rejected; no coefficient invented'}
