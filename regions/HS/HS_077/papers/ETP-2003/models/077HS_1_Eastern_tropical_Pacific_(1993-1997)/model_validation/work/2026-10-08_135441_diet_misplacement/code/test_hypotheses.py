"""Bounded, read-only diet-table placement hypotheses; no model adoption."""
from pathlib import Path
from decimal import Decimal
from itertools import permutations, combinations, product
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[11]
MODEL = ROOT / 'regions/HS/HS_077/papers/ETP-2003/models/077HS_1_Eastern_tropical_Pacific_(1993-1997)/model.json'
MODEL = MODEL.with_name('original_model.json') if MODEL.with_name('original_model.json').exists() else MODEL
PAPER = MODEL.parents[2] / 'sources/Olson_Watters_2003_ETP-c037fcbc.pdf'
RUN = Path(__file__).resolve().parents[1]
OUT = RUN / 'outputs'
OUT.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {'model': sha(MODEL), 'paper': sha(PAPER)}
data = json.loads(MODEL.read_text(encoding='utf-8'))
groups = {int(g['group_seq']): g for g in data['group']}
names = {i: g['group_name'] for i, g in groups.items()}

def milli(v):
    scaled = Decimal(str(v)) * 1000
    assert scaled == scaled.to_integral_value(), v
    return int(scaled)

# Only printed numeric diet entries are tested. Missing -9999 stays unknown.
# Printed blank table positions are represented by zero only within hypotheses.
matrix = {(r, c): 0 for r in range(1, 39) for c in range(1, 37)}
unknown = set()
imports = {}
for c in range(1, 37):
    imports[c] = milli(groups[c]['diet_imp'])
    assert imports[c] >= 0
    for e in groups[c]['diet_descr']['diet']:
        r, v = int(e['prey_seq']), Decimal(e['proportion'])
        if v < 0:
            unknown.add((r, c))
        elif r <= 38:
            matrix[r, c] = milli(v)

def totals(m):
    return {c: imports[c] + sum(m[r, c] for r in range(1, 39)) for c in range(1, 37)}

baseline = totals(matrix)
# Explicitly exclude the rounding-scale Albacore case, not a relaxed test tolerance.
excluded = {18}
assert baseline[18] == 1001
bad = {c for c in baseline if baseline[c] != 1000 and c not in excluded}
assert bad == {11, 12, 22, 23, 25, 26, 27, 28, 29}
assert sum(baseline[c] - 1000 for c in bad) == 0
controls = set(baseline) - bad - excluded
trials = []

def evaluate(family, label, edits):
    trial = matrix.copy()
    for cell, v in edits.items():
        assert cell not in unknown
        trial[cell] = v
    t = totals(trial)
    fixed = sorted(c for c in bad if t[c] == 1000)
    changed_controls = sorted(c for c in controls if t[c] != baseline[c])
    record = dict(family=family, hypothesis=label, fixed_material_count=len(fixed),
                  fixed_material_groups=','.join(map(str, fixed)),
                  changed_control_count=len(changed_controls),
                  changed_control_groups=','.join(map(str, changed_controls)),
                  remaining_material_groups=','.join(str(c) for c in sorted(bad) if t[c] != 1000),
                  all_nine_fixed=len(fixed) == 9 and not changed_controls,
                  excluded_albacore_unchanged=t[18] == baseline[18])
    trials.append(record)
    return record, t

# H1: an intact numeric entry moved within a predator column changes no total.
within_count = 0
for c in sorted(bad):
    for r in range(1, 39):
        if not matrix[r, c]:
            continue
        for target in range(1, 39):
            if target == r or matrix[target, c] or (target, c) in unknown:
                continue
            trial = matrix.copy()
            trial[target, c], trial[r, c] = trial[r, c], 0
            assert totals(trial) == baseline
            within_count += 1

# H2: all single same-prey moves into blanks, among the nine material consumers.
for r in range(1, 39):
    for source in sorted(bad):
        for target in sorted(bad):
            value = matrix[r, source]
            if source == target or not value or matrix[r, target] or (r, target) in unknown:
                continue
            evaluate('single_entry_move', f'prey {r}: {source}->{target}; {value/1000:.3f}',
                     {(r, source): 0, (r, target): value})

# H3: each adjacent same-prey cell swap, including blank-to-value swaps.
for r in range(1, 39):
    for c in range(1, 36):
        if c in excluded or c + 1 in excluded:
            continue
        a, b = matrix[r, c], matrix[r, c + 1]
        if a == b or (r, c) in unknown or (r, c + 1) in unknown:
            continue
        evaluate('adjacent_cell_swap', f'prey {r}: {c}<->{c+1}', {(r, c): b, (r, c + 1): a})

# H4: every distinct permutation of one row's entries within each affected block.
# Unaltered rows, imports, and all other columns are retained exactly.
block_solutions = {}
block_counts = {}
for block in [(11, 12), (22, 23), (25, 26, 27, 28, 29)]:
    key = ','.join(map(str, block))
    solutions = []
    count = 0
    for r in range(1, 39):
        old = tuple(matrix[r, c] for c in block)
        if any((r, c) in unknown for c in block):
            continue
        for new in sorted(set(permutations(old))):
            count += 1
            result, t = evaluate('local_row_permutation', f'prey {r}; block {key}; {old}->{new}',
                                 {(r, c): v for c, v in zip(block, new)})
            if all(t[c] == 1000 for c in block):
                solutions.append({'prey': r, 'before_milli': old, 'after_milli': new})
    block_solutions[key] = solutions
    block_counts[key] = count

# H5: shift a complete prey row by one column within either printed 18-column panel.
# Include only mass-preserving shifts (nothing nonzero falls off the panel).
for r in range(1, 39):
    for start in (1, 19):
        panel = tuple(range(start, start + 18))
        old = tuple(matrix[r, c] for c in panel)
        for direction in (-1, 1):
            if (direction == -1 and old[0]) or (direction == 1 and old[-1]):
                continue
            new = old[1:] + (0,) if direction == -1 else (0,) + old[:-1]
            if old == new or any((r, c) in unknown for c in panel):
                continue
            if any(new[panel.index(c)] != old[panel.index(c)] for c in excluded if c in panel):
                continue
            evaluate('whole_panel_row_shift', f'prey {r}; panel {start}; shift {direction:+}',
                     {(r, c): v for c, v in zip(panel, new)})

# H6: search minimum adjacent intact-entry relocations, affected consumers only.
# Nine affected columns require >= ceil(9/2)=5 moves. Enumerate every 5-edge
# subset and exact cut flows; each move may affect at most two diet totals.
edges = [(c, c + 1) for c in sorted(bad) if c + 1 in bad]
minimum_solutions = []
edge_sets_tested = 0
for selected in combinations(edges, 5):
    edge_sets_tested += 1
    adjacency = {c: set() for c in bad}
    for a, b in selected:
        adjacency[a].add(b)
        adjacency[b].add(a)
    seen = set()
    feasible = True
    components = []
    for c in sorted(bad):
        if c in seen:
            continue
        stack, component = [c], set()
        while stack:
            x = stack.pop()
            if x in component:
                continue
            component.add(x)
            stack.extend(adjacency[x] - component)
        seen |= component
        components.append(component)
        if sum(baseline[x] - 1000 for x in component):
            feasible = False
    if not feasible:
        continue
    options = []
    for a, b in selected:
        component = next(s for s in components if a in s)
        flow = sum(baseline[x] - 1000 for x in component if x <= a)
        source, target = (a, b) if flow > 0 else (b, a)
        candidates = [(r, source, target, abs(flow)) for r in range(1, 39)
                      if flow and matrix[r, source] == abs(flow) and (r, target) not in unknown]
        options.append(candidates)
    for moves in product(*options):
        source_cells = {(r, s) for r, s, t, v in moves}
        target_cells = {(r, t) for r, s, t, v in moves}
        if len(source_cells) != 5 or len(target_cells) != 5:
            continue
        if any(matrix[r, t] and (r, t) not in source_cells for r, s, t, v in moves):
            continue
        edits = {cell: 0 for cell in source_cells}
        edits.update({(r, t): v for r, s, t, v in moves})
        result, t = evaluate('joint_five_moves', str(moves), edits)
        if result['all_nine_fixed'] and result['excluded_albacore_unchanged']:
            minimum_solutions.append(moves)

assert len(minimum_solutions) == 1, minimum_solutions
moves = minimum_solutions[0]
assert set(moves) == {(22, 11, 12, 22), (32, 23, 22, 575), (32, 25, 26, 121),
                      (32, 26, 27, 30), (32, 28, 29, 70)}
edits = {(r, s): 0 for r, s, t, v in moves}
edits.update({(r, t): v for r, s, t, v in moves})
joint = matrix.copy()
joint.update(edits)
after_totals = totals(joint)
assert all(after_totals[c] == 1000 for c in bad)
assert all(after_totals[c] == baseline[c] for c in set(baseline) - bad)
assert all(sum(matrix[r, c] for c in range(1, 37)) == sum(joint[r, c] for c in range(1, 37))
           for r in range(1, 39))
assert sorted(v for v in matrix.values() if v) == sorted(v for v in joint.values() if v)
assert before == {'model': sha(MODEL), 'paper': sha(PAPER)}

def write_csv(name, rows):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

write_csv('hypothesis_trials.csv', trials)
write_csv('proposed_moves.csv', [dict(prey_id=r, prey_name=names[r], proportion=f'{v/1000:.3f}',
    from_predator_id=s, from_predator_name=names[s], to_predator_id=t, to_predator_name=names[t],
    source_table='Table 3a', printed_page=158 if r == 22 else 159,
    pdf_page=28 if r == 22 else 29, status='unadopted hypothesis') for r, s, t, v in moves])
write_csv('consumer_totals.csv', [dict(predator_id=c, predator_name=names[c],
    before=f'{baseline[c]/1000:.3f}', after_hypothesis=f'{after_totals[c]/1000:.3f}',
    classification='excluded rounding-scale case' if c in excluded else 'material discrepancy' if c in bad else 'balanced control')
    for c in range(1, 37)])
families = {}
for family in sorted({r['family'] for r in trials}):
    rows = [r for r in trials if r['family'] == family]
    families[family] = dict(tested=len(rows), max_material_fixed=max(r['fixed_material_count'] for r in rows),
        all_nine_fixed_without_control_changes=sum(r['all_nine_fixed'] for r in rows),
        two_fixed_without_control_changes=sum(r['fixed_material_count'] == 2 and r['changed_control_count'] == 0 for r in rows))
summary = dict(operation='Unadopted source-placement hypothesis tests', input_hashes=before,
    model=str(MODEL.relative_to(ROOT)), source=str(PAPER.relative_to(ROOT)),
    arithmetic='Exact integer thousandths; no rounding corrections or normalization',
    material_groups=sorted(bad), excluded=[dict(id=18, name=names[18], total='1.001')],
    within_column_moves_tested=within_count, families=families,
    block_permutation_counts=block_counts, block_solutions=block_solutions,
    minimum_adjacent_moves=5, minimum_solutions_found=len(minimum_solutions),
    five_edge_subsets_tested=edge_sets_tested,
    uniqueness_scope='Same-prey, unchanged-value moves between adjacent material-discrepancy columns; no splitting, merging, value edits or changes to imports/controls/Albacore.',
    verification=dict(canonical_source_hashes_unchanged=True, all_nine_exactly_one=True,
        all_other_consumers_unchanged=True, prey_row_totals_preserved=True, numeric_value_multiset_preserved=True,
        imports_and_unknowns_unchanged=True),
    interpretation='A unique minimal candidate within this bounded search, not author confirmation or proof of ecological validity.')
(OUT / 'test_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(summary, indent=2, ensure_ascii=False))
