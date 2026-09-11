"""Explicit-label catch sensitivity classification; no taxonomic-rank inference."""
import math
import re

VERSION = 'explicit-labels-v1'
RULE = ('Catch taxon or common name contains the whole word unidentified, '
        'the phrase not identified, NEI (including N.E.I.), or not elsewhere included. '
        'Named genera/families, spp., miscellaneous and other aggregates are not '
        'classified unless one of those explicit markers is present.')
PATTERN = re.compile(r'\bunidentified\b|\bnot\s+identified\b|\bn\.?e\.?i\b\.?|\bnot\s+elsewhere\s+included\b', re.I)


def metadata(rows, years, trophic_levels):
    affected = []
    matched = []
    for row in rows:
        evidence = [(key, PATTERN.search(row.get(key, '') or '')) for key in ('taxon', 'common_name')]
        reasons = [f'{key}: {match.group()}' for key, match in evidence if match]
        if not reasons:
            continue
        tl = trophic_levels.get(row['taxon'])
        valid = isinstance(tl, (int, float)) and not isinstance(tl, bool) and math.isfinite(tl)
        coefficient = 10 ** (tl - 1) if valid else None
        affected.append({'name': row['taxon'], 'common_name': row.get('common_name', ''),
                         'reason': '; '.join(reasons), 'reference_tl': tl if valid else None,
                         'simple_sppr': coefficient})
        matched.append((row, coefficient))
    return {'classifier_version': VERSION, 'rule_description': RULE, 'taxa': affected,
            'catch': [round(sum(row['by_year'].get(y, 0) for row, _ in matched), 3) for y in years],
            'missing_simple_catch': [round(sum(row['by_year'].get(y, 0) for row, c in matched if c is None), 3) for y in years]}


def coefficients(taxa, original, affected, treatment):
    lookup = {row['name']: row['simple_sppr'] for row in affected}
    return [(0 if treatment == 'zero' else lookup[taxon]) if taxon in lookup else value
            for taxon, value in zip(taxa, original)]
