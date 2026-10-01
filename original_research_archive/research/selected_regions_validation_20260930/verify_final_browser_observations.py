"""Compare retained, directly observed CUA DOM values with regional references.

The arrays below are observations from the actual generated worktree page,
not values calculated by this script. CUA selected each ecosystem and method
through its visible controls; page evaluation was read-only DOM inspection.
"""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent

UNITS = 'EEZ_598 EEZ_941 HS_071 HS_077 LME_003 LME_013 LME_014 LME_022 LME_024 LME_026 LME_027 LME_028 LME_029 LME_032 LME_034 LME_035 LME_036 LME_037 LME_038 LME_047 LME_049 LME_050 LME_052'.split()
OBSERVED = {
    'simple trophic chain': [140800000,167300000,157900000,226000000,107100000,277100000,142500000,188900000,105400000,105800000,244700000,202200000,100800000,514700000,379300000,192500000,837500000,109000000,177200000,370200000,180700000,145000000,248400000],
    'GE': [613800000,501300000,607700000,290600000,33050000,71260000,9680000,28150000,26830000,None,14020000,850400000,72520000,259000000,615700000,20990000,49320000,28710000,27000000,24300000,21770000,5916000,587900000],
    'TE': [1016000000,733800000,1147000000,2410000000,202600000,292100000,3394000000,43580000,None,None,1947000000,None,127600000,475600000,936000000,87440000,423500000,58960000,279500000,138100000,169900000,73340000,None],
    'With Egestion': [161800000,146100000,165400000,28940000,11540000,30390000,4910000,11230000,13300000,None,8676000,270900000,24690000,88190000,184300000,10550000,25340000,13400000,10830000,13270000,9813000,3528000,121900000],
}
CLASSIC_EXPECTED = [140786408.79522264,167307899.00452706,157858508.51530254,226007970.44202933,107146622.59621234,277099551.4346593,142458248.78282157,188909420.82919472,105377067.65877189,105846498.8981603,244709206.36682716,202194055.86165074,100781750.16526629,514724666.46114403,379324412.0465857,192544832.37659073,837452937.7894479,108985038.3517547,177164712.36289582,370210805.58009297,180683377.6852617,145016301.8487018,248368608.3757302]
GROUP_COUNTS = [32,32,32,40,94,16,37,26,55,71,28,45,50,25,50,30,39,34,29,25,40,41,30]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    synthesis_path = BASE / 'work/final_status_synthesis/final_23_region_status.json'
    synthesis = json.loads(synthesis_path.read_text(encoding='utf-8'))
    selected = {r['unit_id']: r for r in synthesis['regions']}
    assert set(selected) == set(UNITS)
    checks = []
    for method, values in OBSERVED.items():
        assert len(values) == 23
        for i, (unit, displayed) in enumerate(zip(UNITS, values)):
            expected = CLASSIC_EXPECTED[i] if method == 'simple trophic chain' else selected[unit]['methods'][method]['annual_value_tC']
            if expected is None:
                ok = displayed is None
                tolerance = None
            else:
                tolerance = 10 ** (math.floor(math.log10(abs(expected))) - 3) / 2
                ok = displayed is not None and abs(displayed - expected) <= tolerance
            checks.append(dict(unit=unit, method=method, observed_tC=displayed, expected_tC=expected,
                               four_significant_digit_tolerance=tolerance, passed=ok))
    assert all(c['passed'] for c in checks), [c for c in checks if not c['passed']]
    receipt = {
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS',
        'scope': 'Actual CUA DOM observations of map totals and group controls; further trends/control/relocation checks are separate.',
        'url': 'http://127.0.0.1:53284/interactive_map/index.html',
        'visible_page_project_sha256': '24fd90150e5484a36a04ad940b69d47afefd16f1b0301b3bd757e78f07830fec',
        'project_sha256': sha(ROOT / 'Project.xlsx'),
        'map_sha256': sha(ROOT / 'interactive_map/index.html'),
        'synthesis_sha256': sha(synthesis_path),
        'reference': {'year':2019,'scope':'all','unidentified':'method','groups':'all','basis':'landings except LME_022 catch'},
        'observed_selected_models_match_canonical': True,
        'groups': [dict(unit=u, model=selected[u]['model_id'], rows=n, checked=n) for u,n in zip(UNITS,GROUP_COUNTS)],
        'checks': checks,
        'unavailable_methods': [dict(unit=c['unit'],method=c['method']) for c in checks if c['observed_tC'] is None],
        'observed_unavailable_status_text': {
            'LME_026 all modern methods':'Method unavailable in this scope',
            'LME_024 TE':'Method unavailable in this scope',
            'LME_028 TE':'new_TE_EEfix: IMPLAUSIBLE - up to 29x the trophic-chain estimate; the solve is near-singular for this model',
            'LME_052 TE':'new_TE_EEfix: DIVERGED: negative source-group SPPR',
        },
        'source_display_observation': 'LME_052 explicitly displays GE WARN / TE FAIL / With Egestion WARN and whole-region scientific validation pending; related 2020 chapter is labeled separately from unavailable original 2004 thesis. Source, workbook and diagnostic links are relative.',
        'interaction_note': 'The narrow in-app viewport placed left controls off-screen; semantic keyboard Enter activated buttons reliably. A viewport override did not take effect. This is not a claim of responsive-layout verification.',
    }
    assert receipt['project_sha256'] == receipt['visible_page_project_sha256']
    out = BASE / 'verification/final_all23_map_browser_values.json'
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status':'PASS','checks':len(checks),'groups':23,'unavailable':len(receipt['unavailable_methods']),'receipt':str(out)}))


if __name__ == '__main__':
    main()
