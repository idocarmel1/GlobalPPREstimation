"""Independent fixed-2019 catch-boundary control, using only frozen inputs."""
from pathlib import Path
import csv
import gzip
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    'LME_013': '13_2_Northern_Humboldt_Current_(1995-1998)',
    'LME_028': '28_646_Guinea_(1998)',
    'LME_034': '34_1_Bay_of_Bengal_(1978)',
    'LME_052': '52_1_Sea_of_Okhotsk_NE_(1980)',
}


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def evaluate(catches, coefficients):
    """Use exactly the same supported taxon set for each catch boundary."""
    pairs = [(row, coefficients.get(name)) for name, row in catches.items()
             if finite(coefficients.get(name)) and coefficients[name] >= 0]
    mass = {key: sum(row[key] * coefficient for row, coefficient in pairs) / 9
            for key in ('catch', 'landings', 'discards')}
    assert math.isclose(mass['catch'], mass['landings'] + mass['discards'], rel_tol=1e-12, abs_tol=1e-7)
    covered = {key: sum(row[key] for row, _ in pairs) for key in ('catch', 'landings', 'discards')}
    return mass, covered


def run():
    inputs = ROOT / 'inputs'
    network_path = inputs / 'PPRAtlas/data/network_ppr.json'
    network = json.loads(network_path.read_text(encoding='utf-8'))
    output, hashes = [], []
    for unit, model_id in MODELS.items():
        catch_path = inputs / f'SeaAroundUsExtraction/data/catch_by_taxon_year/{unit}.csv.gz'
        catches = {}
        with gzip.open(catch_path, 'rt', encoding='utf-8-sig', newline='') as stream:
            for row in csv.DictReader(stream):
                if int(row['year']) != 2019:
                    continue
                name = row['taxon']
                assert name not in catches, (unit, name)
                values = {k: float(row[k + '_tonnes']) for k in ('catch', 'landings', 'discards')}
                assert all(math.isfinite(v) and v >= 0 for v in values.values())
                assert math.isclose(values['catch'], values['landings'] + values['discards'], rel_tol=1e-10, abs_tol=1e-7)
                catches[name] = values
        total = {key: sum(row[key] for row in catches.values()) for key in ('catch', 'landings', 'discards')}
        record = network['units'][unit]
        model = next(m for m in record['models'] if m['id'] == model_id)
        assert model['verified']
        workbook = inputs / model['workbook']
        assert hashlib.sha256(workbook.read_bytes()).hexdigest() == model['workbook_sha256']
        scope = model['scopes']['all']
        methods = {method: dict(zip(record['taxa'], [row[i] for row in scope['values']]))
                   for i, method in enumerate(scope['methods']) if method != 'simple trophic chain'}
        species_path = inputs / f'SeaAroundUsExtraction/global_output/tables/regions/{unit}/species.csv'
        with species_path.open(encoding='utf-8-sig', newline='') as stream:
            methods['simple trophic chain'] = {r['taxon']: 10 ** (float(r['tl']) - 1)
                for r in csv.DictReader(stream) if r['tl'].strip()}
        npp = network['npp'][unit]['ens_median_tC_yr'][network['npp_years'].index(2019)]
        for method, coefficients in methods.items():
            status = 'ok' if method == 'simple trophic chain' else scope['status'].get(method, 'unavailable')
            mass, covered = evaluate(catches, coefficients) if status == 'ok' else ({k: None for k in total}, {k: None for k in total})
            result = {'unit_id': unit, 'model_id': model_id, 'year': 2019, 'method': method,
                      'scope': 'all', 'unidentified_treatment': 'method', 'status': status,
                      'npp_tC_yr': npp, 'discard_fraction_catch': total['discards'] / total['catch'] if total['catch'] else None}
            for key in total:
                result[key + '_tonnes'] = total[key]
                result[key + '_covered_tonnes'] = covered[key]
                result[key + '_ppr_tC_yr'] = mass[key]
                result[key + '_ppr_npp_percent'] = 100 * mass[key] / npp if finite(mass[key]) and finite(npp) and npp > 0 else None
            result['discard_share_ppr_percent'] = 100 * mass['discards'] / mass['catch'] if finite(mass['catch']) and mass['catch'] > 0 else None
            output.append(result)
        for p in (catch_path, species_path, workbook):
            hashes.append({'path': p.relative_to(inputs).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    with (ROOT / 'results/external_reference_audit.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output[0]))
        writer.writeheader(); writer.writerows(output)
    report = {'status': 'ok', 'year': 2019, 'evaluation': 'fixed frozen coefficients; direct catch-boundary control only',
              'network_sha256': hashlib.sha256(network_path.read_bytes()).hexdigest(), 'sources': hashes,
              'rows': len(output), 'checks': [r for r in output if r['method'] == 'SPPR_1995_TE0.1']}
    (ROOT / 'results/external_reference_audit.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'ok', 'rows': len(output), 'checks': [
        {k: r[k] for k in ('unit_id', 'discard_fraction_catch', 'discard_share_ppr_percent', 'landings_ppr_npp_percent')}
        for r in report['checks']]}))


if __name__ == '__main__':
    run()
