import math

def select_regions(selected, available):
    ids = [r['unit_id'] for r in selected]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate selected ecosystem IDs')
    by_id = {r['unit_id']: r for r in available}
    missing = set(ids) - by_id.keys()
    if missing:
        raise ValueError(f'Missing ecosystem records: {sorted(missing)}')
    return [dict(by_id[i]) for i in ids]

def rank_regions(regions):
    rows = [dict(r) for r in regions]
    for r in rows:
        if r.get('ppr') is not None and (not math.isfinite(r['ppr']) or r['ppr'] < 0):
            raise ValueError('PPR must be nonnegative and finite, or missing')
    rows.sort(key=lambda r: (r.get('ppr') is None, -(r.get('ppr') or 0), r['unit_id']))
    total = math.fsum(r['ppr'] for r in rows if r.get('ppr') is not None)
    cumulative = 0
    previous, rank = None, None
    for index, r in enumerate(rows, 1):
        value = r.get('ppr')
        if value is None:
            r.update(ppr_rank=None, global_ppr_share=None, cumulative_ppr_share=None)
            continue
        if value != previous:
            rank = index
        previous = value
        cumulative += value
        r.update(ppr_rank=rank, global_ppr_share=value/total if total else 0, cumulative_ppr_share=cumulative/total if total else 0)
    return rows
