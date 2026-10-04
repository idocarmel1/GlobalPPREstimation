"""Proportions for an explicitly approved assumption; never infer candidate membership.

Callers must establish and record eligible groups before calling this function.
The result describes allocation confidence only; membership uncertainty is separate.
No files, model parameters or saved group coefficients are modified.
"""
import math


def allocate(candidates, geographic=None):
    """Allocate reviewed candidates; optionally prefer applicable measured geography.

    ``geographic`` contains ``values_by_group`` (caught mass in common units),
    ``directly_measured=True``, and nonempty source, area_boundaries,
    group_correspondence, period, catch_basis, units and applicability fields.
    The caller establishes scientific applicability; map overlap alone does not
    meet this contract. Rejected evidence remains in attempts before fallback.
    """
    unresolved = dict(field=None, values=[], total=None, weights=None,
                      confidence='Unresolved')
    if not candidates or any(not c.get('eligibility') for c in candidates):
        return {**unresolved, 'reason': 'Eligible model groups are not established.'}
    # JSON object keys are strings. Normalize identifiers without collapsing
    # ambiguous aliases such as a simultaneous integer 1 and string "1".
    ids = [str(c['group_id']) for c in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate candidate group IDs')
    attempts = []
    if geographic is not None:
        required = ('source', 'area_boundaries', 'group_correspondence',
                    'period', 'catch_basis', 'units', 'applicability')
        raw_masses = geographic.get('values_by_group', {})
        masses = {str(k): v for k, v in raw_masses.items()}
        if len(masses) != len(raw_masses):
            raise ValueError('Duplicate geographic group ID aliases')
        values = [masses.get(i) for i in ids]
        complete = (set(masses) == set(ids)
                    and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                            and math.isfinite(v) and v >= 0 for v in values))
        total = math.fsum(values) if complete else None
        applicable = (geographic.get('directly_measured') is True
                      and all(isinstance(geographic.get(k), str)
                              and geographic[k].strip() for k in required))
        usable = complete and total > 0 and applicable
        attempts.append(dict(field='source_geographic_catch', values=values,
                             total=total, usable=usable, evidence=geographic))
        if usable:
            return dict(field='source_geographic_catch', values=values, total=total,
                        weights=[v / total for v in values], confidence='High',
                        evidence=geographic, attempts=attempts,
                        reason='Applicable measured caught mass by geographic stratum; '
                               'group correspondence and applicability established by caller.')
    for field in ('catch', 'biomass'):
        values = [c.get(field) for c in candidates]
        complete = all(isinstance(v, (int, float)) and not isinstance(v, bool)
                       and math.isfinite(v) and v >= 0 for v in values)
        total = math.fsum(values) if complete else None
        attempts.append(dict(field=field, values=values, total=total,
                             usable=complete and total > 0))
        if complete and total > 0:
            return dict(field=field, values=values, total=total,
                        weights=[v / total for v in values], confidence='Medium',
                        attempts=attempts,
                        reason='Assumed model ' + field + ' composition of eligible groups; not observed target-catch composition.')
    return {**unresolved, 'attempts': attempts,
            'reason': 'Neither model catch nor model biomass provides complete nonnegative proportions with a positive total.'}
