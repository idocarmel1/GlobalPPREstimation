"""Read-only reconstruction of the thirteen retained California W5 allocations."""
import ast
from collections import defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGION = ROOT / 'regions/LME_003'
MODEL = REGION / 'models/CAL-2016_California_Current_2000-2014'
REPORT = REGION / 'validation_reports/CAL-2016_California_Current_2000-2014'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))


def main():
    builder = MODEL / 'selected_pipeline/code/build_selected_mapping.py'
    source = ast.parse(builder.read_text(encoding='utf-8'))
    namespace = {}
    # Inspect only literal selector definitions and the reviewed pure predicate.
    # Never import/run the historical module: its top-level code writes a workbook.
    for node in source.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in {'bivalve', 'gastropod', 'composites'}:
                namespace[target.id] = ast.literal_eval(node.value)
        if isinstance(node, ast.FunctionDef) and node.name == 'in_composite':
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(builder), 'exec'), namespace)
    assert set(namespace) >= {'bivalve', 'gastropod', 'composites', 'in_composite'}
    decisions_path = MODEL / 'selected_pipeline/mapping_decisions.json'
    work_order = REGION / 'extraction_review_20260928/catch_work_order.json'
    decisions = {r['taxon']: r for r in read(decisions_path)}
    taxa = read(work_order)
    ledger_path = REPORT / 'allocation_evidence.json'
    ledgers = defaultdict(list)
    for row in read(ledger_path):
        if row.get('rule') == 'W5':
            ledgers[row['taxon']].append(row)
    assert len(ledgers) == 13
    prepared = []
    for target, rows in sorted(ledgers.items()):
        candidate_ids, description = namespace['composites'][target]
        donors, masses = [], defaultdict(float)
        for taxon in taxa:
            name = taxon['taxon']
            d = decisions.get(name)
            if not d or d['evidence'] == 'composite_split' or not namespace['in_composite'](target, name):
                continue
            for group, weight in d['assignments']:
                if group in candidate_ids:
                    mass = taxon['total'] * weight
                    masses[group] += mass
                    donors.append({'taxon': name, 'group_id': group, 'total_catch_t': taxon['total'],
                                   'assignment_weight': weight, 'donor_mass_t': mass})
        denominator = sum(masses[g] for g in candidate_ids)
        assert denominator > 0
        rebuilt = {g: masses[g] / denominator for g in candidate_ids}
        maximum = max(abs(row['weight'] - rebuilt.get(row['seq'], 0.0)) for row in rows)
        assert maximum <= 1e-14, (target, maximum)
        assert all(row['allocation_confidence'] == 'Low' for row in rows)
        prepared.append({'taxon': target, 'historical_candidate_ids': candidate_ids,
                         'current_candidate_ids': sorted(row['seq'] for row in rows),
                         'selector_description': description,
                         'donors': donors, 'candidate_donor_mass_t': dict(masses),
                         'denominator_t': denominator, 'reproduced_weights': rebuilt,
                         'maximum_difference_from_current_weights': maximum,
                         'allocation_confidence': 'Low'})
    needed = {r['taxon'] for r in prepared} | {d['taxon'] for r in prepared for d in r['donors']}
    raw_path = REGION / 'raw/LME_003-catch.zip'
    dimensions = ['fishing_entity', 'fishing_sector', 'catch_type', 'reporting_status', 'gear_type', 'decade']
    quantities = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    with ZipFile(raw_path) as z:
        names = [n for n in z.namelist() if n.endswith('.csv')]
        assert len(names) == 1
        with io.TextIOWrapper(z.open(names[0]), encoding='utf-8-sig', newline='') as stream:
            for row in csv.DictReader(stream):
                taxon = row['scientific_name']
                if taxon not in needed:
                    continue
                mass = float(row['tonnes'])
                assert math.isfinite(mass) and mass >= 0
                row['decade'] = str(int(row['year']) // 10 * 10)
                for dim in dimensions:
                    quantities[taxon][dim][row[dim]].append(mass)
    totals = {t: {dim: {key: math.fsum(vals) for key, vals in pairs.items()}
                  for dim, pairs in dims.items()} for t, dims in quantities.items()}
    for r in prepared:
        donors = {d['taxon']: d['assignment_weight'] for d in r['donors']}
        compare = {}
        for dim in dimensions:
            target_mass = totals.get(r['taxon'], {}).get(dim, {})
            donor_terms = defaultdict(list)
            for taxon, weight in donors.items():
                for key, value in totals.get(taxon, {}).get(dim, {}).items():
                    donor_terms[key].append(value * weight)
            donor_mass = {k: math.fsum(v) for k, v in donor_terms.items()}
            total_t, total_d = math.fsum(target_mass.values()), math.fsum(donor_mass.values())
            assert math.isclose(total_d, r['denominator_t'], rel_tol=1e-12, abs_tol=1e-7)
            target_share = {k: v / total_t for k, v in target_mass.items()} if total_t else {}
            donor_share = {k: v / total_d for k, v in donor_mass.items()}
            compare[dim] = {'target_total_t': total_t, 'donor_total_t': total_d,
                            'target_shares': target_share, 'donor_shares': donor_share,
                            'total_variation': 0.5 * math.fsum(abs(target_share.get(k, 0) - donor_share.get(k, 0))
                                                             for k in target_share.keys() | donor_share.keys()) if total_t else None}
        r['reporting_population_comparison'] = compare
    evidence = [builder, decisions_path, work_order, ledger_path, raw_path, REGION / 'LME_003.xlsx']
    result = {'status': 'PASS', 'scope': 'Retained W5 selectors, weight arithmetic and raw reporting populations; no parameter, mapping, confidence or result change.',
              'sources': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in evidence],
              'builder_locator': 'build_selected_mapping.py49–91; in_composite71–78 and direct-mass loop81–90',
              'source_csv_member': names[0], 'items': prepared,
              'finding': 'This builder filters some composite donors by explicit taxonomic genus lists, while default branches include all directly assigned taxa in the candidates. It is not the unrestricted historical Gulf builder. Existing Low confidence already discloses pooled taxonomic and reporting-population transfer. No observed target composition or better split is established by reproducibility.',
              'protected_workbook_unchanged': True}
    destination = HERE / 'verification/LME_003_donor_selector_reconstruction.json'
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'taxa': len(prepared), 'maximum_weight_difference': max(r['maximum_difference_from_current_weights'] for r in prepared),
                      'evidence': destination.relative_to(ROOT).as_posix()}), flush=True)


if __name__ == '__main__':
    main()
