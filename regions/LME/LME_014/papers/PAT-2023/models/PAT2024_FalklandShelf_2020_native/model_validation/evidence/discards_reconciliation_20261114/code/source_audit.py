"""Read-only native fisheries/source audit; writes only this authorized work run."""
from __future__ import annotations

import hashlib
import json
import logging
import math
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from zipfile import ZipFile
from xml.etree import ElementTree as ET

RUN = Path(__file__).resolve().parents[1]
ROOT = next(p for p in RUN.parents if (p / 'Project.xlsx').is_file())
MODEL = RUN.parents[2]
PAPER = MODEL.parents[1]
SOURCE = next((PAPER / 'sources').glob('*.eweaccdb'))
OUT = RUN / 'outputs/source'
QA = RUN / 'qa/source'
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


pdf = next((PAPER / 'sources').glob('*.pdf'))
docx = next((PAPER / 'sources').glob('*.docx'))
csv_path = next((PAPER / 'sources').glob('*.csv'))
source_variant = MODEL.parent / (MODEL.name + '__source')
protected = [SOURCE, pdf, docx, csv_path, MODEL / 'model.json', source_variant / 'model.json']
protected += list((source_variant / 'extracted_tables').glob('*.csv'))
before = {rel(p): sha(p) for p in protected}
save(QA / 'protected_before.json', before)

# Native ODBC uses SELECT only and ReadOnly=1. Cast Single to Double before JSON
# serialization so binary Single precision is preserved, not rounded to 7 digits.
ps = r'''
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false)
$conn=[System.Data.Odbc.OdbcConnection]::new('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+$env:PPR_SOURCE_DB+';ReadOnly=1;')
$conn.Open()
try {
  $tables=@($conn.GetSchema('Tables').Rows | Where-Object { $_.TABLE_TYPE -eq 'TABLE' } | ForEach-Object { [string]$_.TABLE_NAME })
  $wanted=@('EcopathModel','EcopathGroup','EcopathFleet','EcopathCatch','EcopathDiscardFate','EcopathDietComp','UpdateLog')
  $data=[ordered]@{}
  foreach ($name in $wanted) {
    $cmd=$conn.CreateCommand();$cmd.CommandText='SELECT * FROM ['+$name+']'
    $reader=$cmd.ExecuteReader();$rows=[System.Collections.Generic.List[object]]::new()
    try {
      while ($reader.Read()) {
        $row=[ordered]@{}
        for ($i=0;$i -lt $reader.FieldCount;$i++) {
          $v=$reader.GetValue($i)
          if ($v -is [DBNull]) {$v=$null}
          elseif ($v -is [single]) {$v=[double]$v}
          elseif ($v -is [datetime]) {$v=$v.ToString('o')}
          $row[$reader.GetName($i)]=$v
        }
        $rows.Add($row)
      }
    } finally {$reader.Close()}
    $data[$name]=$rows.ToArray()
  }
  $inventory=[System.Collections.Generic.List[object]]::new()
  foreach ($name in $tables) {
    $cmd=$conn.CreateCommand();$cmd.CommandText='SELECT COUNT(*) FROM ['+$name+']'
    $count=[int64]$cmd.ExecuteScalar()
    $inventory.Add([ordered]@{name=$name;row_count=$count})
  }
  [ordered]@{read_only=$true;provider='Microsoft Access ODBC via System.Data.Odbc';tables=$data;table_inventory=$inventory.ToArray()} | ConvertTo-Json -Depth 20 -Compress
} finally {$conn.Close()}
'''
env = dict(os.environ, PPR_SOURCE_DB=str(SOURCE))
proc = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', ps],
                      env=env, capture_output=True, timeout=180)
(QA / 'native_read_stderr.txt').write_bytes(proc.stderr)
if proc.returncode:
    raise RuntimeError(proc.stderr.decode('utf-8', errors='replace'))
native = json.loads(proc.stdout.decode('utf-8-sig'))
save(OUT / 'native_readonly_tables.json', native)
t = native['tables']
groups = {int(g['GroupID']): g for g in t['EcopathGroup']}
byseq = {int(g['Sequence']): g for g in groups.values()}
fleets = {int(f['FleetID']): f for f in t['EcopathFleet']}
fates = {}
for r in t['EcopathDiscardFate']:
    fates.setdefault(int(r['FleetID']), []).append(r)

rows = []
for c in sorted(t['EcopathCatch'], key=lambda c: (groups[int(c['GroupID'])]['Sequence'], c['FleetID'])):
    g = groups[int(c['GroupID'])]
    fid = int(c['FleetID'])
    discarded = float(c['Discards'])
    mortality = float(c['DiscardMortality'])
    recipients = []
    for f in sorted(fates[fid], key=lambda f: groups[int(f['GroupID'])]['Sequence']):
        dst = groups[int(f['GroupID'])]
        frac = float(f['DiscardFate'])
        recipients.append({'recipient_group_id': int(f['GroupID']), 'recipient_seq': int(dst['Sequence']),
                           'recipient_name': dst['GroupName'], 'fraction': frac,
                           'amount': discarded * mortality * frac,
                           'source_keys': {'EcopathDiscardFate': {'FleetID': fid, 'GroupID': int(f['GroupID'])}}})
    rows.append({'donor_group_id': int(c['GroupID']), 'donor_seq': int(g['Sequence']),
                 'donor_name': g['GroupName'], 'fleet_id': fid, 'fleet_name': fleets[fid]['FleetName'],
                 'landings': float(c['Landing']), 'discards': discarded,
                 'discard_mortality': mortality, 'dead_discards': discarded * mortality,
                 'recipients': recipients,
                 'source_keys': {'EcopathCatch': {'GroupID': int(c['GroupID']), 'FleetID': fid}}})

accepted = {int(g['group_seq']): g for g in json.loads((MODEL / 'model.json').read_text(encoding='utf-8-sig'))['group']}
consumer_rows = []
for dc in t['EcopathDietComp']:
    prey = groups[int(dc['PreyID'])]
    consumer = groups[int(dc['PredID'])]
    if int(prey['Sequence']) == 35 and float(dc['Diet']) > 0:
        s = int(consumer['Sequence'])
        ag = accepted[s]
        b, qb, frac = float(ag['biomass']), float(ag['qb']), float(dc['Diet'])
        consumer_rows.append({'consumer_group_id': int(dc['PredID']), 'consumer_seq': s,
                              'consumer_name': consumer['GroupName'], 'prey_group_id': int(dc['PreyID']),
                              'prey_seq': 35, 'diet_fraction': frac,
                              'native_biomass': consumer['Biomass'], 'native_qb': consumer['ConsBiom'],
                              'accepted_biomass': b, 'accepted_qb': qb,
                              'accepted_completed_annual_demand': b * qb * frac,
                              'demand_calculation': 'accepted completed B * unchanged native Q/B * native diet fraction; arithmetic only, no solver',
                              'source_keys': {'EcopathDietComp': {'PredID': int(dc['PredID']), 'PreyID': int(dc['PreyID'])}}})

ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(docx) as z:
    xml = ET.fromstring(z.read('word/document.xml'))
tables = xml.findall('./w:body/w:tbl', ns)
s4_rows = [[" ".join(n.text or '' for n in cell.findall('.//w:t', ns)) for cell in row.findall('./w:tc', ns)]
           for row in tables[2].findall('./w:tr', ns)]
s4 = {'citation': 'Büring et al. (2024), supplementary DOCX, Table S4 (historical rendered page 5)',
      'caption_units_verbatim': 'Landings and Discards used for the Ecopath model (in t per km2)',
      'rows': s4_rows, 'printed_totals': {'trawling_landings': 0.5899, 'jigging_landings': 0.3451,
                                        'total_landings': 0.935, 'trawling_discards': 0.0059,
                                        'jigging_discards': None, 'jigging_discards_literal': '-',
                                        'total_discards': 0.0059}}
save(OUT / 'supplement_s4.json', s4)

historical = MODEL / 'model_validation/evidence/source_review/diet_reextraction_20261002/primary_readonly_audit_tables.json'
old = json.loads(historical.read_text(encoding='utf-8'))
same_groups = sorted(old['EcopathGroup'], key=lambda g:g['GroupID']) == sorted(t['EcopathGroup'], key=lambda g:g['GroupID'])
same_diets = sorted(old['EcopathDietComp'], key=lambda g:(g['PredID'],g['PreyID'])) == sorted(t['EcopathDietComp'], key=lambda g:(g['PredID'],g['PreyID']))

total_d = math.fsum(r['discards'] for r in rows)
total_l = math.fsum(r['landings'] for r in rows)
demand = math.fsum(r['accepted_completed_annual_demand'] for r in consumer_rows)
byrecipient = {str(s): math.fsum(d['amount'] for r in rows for d in r['recipients'] if d['recipient_seq'] == s) for s in [35,36]}
keys = [(r['donor_seq'], r['fleet_id']) for r in rows]
expected = {(s,fid) for s in byseq for fid in fleets}
group_crosswalk = [{'group_id': gid, 'seq': int(g['Sequence']), 'name': g['GroupName']} for gid,g in sorted(groups.items(), key=lambda kv:kv[1]['Sequence'])]
ledger = {
    'schema_version': 1, 'run_id': RUN.name, 'created_utc': datetime.now(timezone.utc).isoformat(),
    'model_id': MODEL.name, 'source_identity': {'path': rel(SOURCE), 'sha256': sha(SOURCE),
                                             'method': 'fresh read-only ODBC SELECT from original author database'},
    'source_hashes': before,
    'units': {'native_model_area_km2': t['EcopathModel'][0]['Area'],
              'native_first_year': t['EcopathModel'][0]['FirstYear'], 'native_num_years': t['EcopathModel'][0]['NumYears'],
              'source_table_units': 'S4 prints t per km2; Methods p.9 states 2020 discards.',
              'amount_basis': '2020 fishery amount normalized by model area, t/km2; annualized as t/km2/year for this one-year model.',
              'wet_weight_explicit_in_inspected_source': False,
              'stock_vs_flow': 'Discards B is a source stock-density field equal to annual discarded amount numerically; no residence-time observation is supplied.'},
    'group_crosswalk': group_crosswalk, 'rows': rows,
    'totals': {'landings': total_l, 'discards': total_d, 'dead_discards': math.fsum(r['dead_discards'] for r in rows),
               'recipient_inflow': byrecipient, 'discards_accepted_completed_demand': demand,
               'demand_to_total_fishery_discards_ratio': demand/total_d,
               'hypothetical_rerouting_to_35_residual': total_d-demand,
               'hypothetical_rerouting_performed': False},
    'completeness': {'groups': len(groups), 'fleets': len(fleets), 'catch_rows': len(rows),
                     'all_group_fleet_pairs_present_once': set(keys)==expected and len(keys)==len(set(keys)),
                     'finite_nonnegative_catches': all(math.isfinite(r[k]) and r[k]>=0 for r in rows for k in ['landings','discards']),
                     'all_discard_mortality_one': all(r['discard_mortality']==1 for r in rows),
                     'fleet_recipient_fractions_sum_one': {str(fid): math.fsum(float(r['DiscardFate']) for r in rr)==1 for fid,rr in fates.items()},
                     'fresh_groups_equal_retained_primary_audit': same_groups, 'fresh_diets_equal_retained_primary_audit': same_diets},
    'discards_consumers': consumer_rows,
    'native_pool_rows': {'35': byseq[35], '36': byseq[36]},
    'source_narrative': [
        {'locator': 'Main PDF p.9, Ecopath Methods', 'finding': 'Separate Discards prey category for discard feeders/scavengers, such as birds; B equals all fisheries discards in 2020.'},
        {'locator': 'Main PDF p.15, Table 4 continuation', 'finding': 'Discards sequence35 B=0.01 t/km2 after rounding; Detritus sequence36 is separate, EE=0.05. Native Detritus EE=0 differs.'},
        {'locator': 'Main PDF p.8, Table 2; separate S2 CSV', 'finding': 'Detritus category combines POM, detritus and discards; printed and native model structures differ.'},
        {'locator': 'Main PDF p.9 Methods and p.12 Results', 'finding': 'Authors describe PREBAL balancing and call final model balanced; this does not independently verify the current reconstruction.'},
        {'locator': 'Main PDF p.16 Discussion', 'finding': 'Birds feed on vessel fish guts and heads. No annual processing-offal mass or quantified additional supply to group35 is identified in the inspected source.'},
        {'locator': 'Main PDF p.9 Methods', 'finding': 'External diet imports for migratory consumers are described separately; no explicit Discards drawdown, negative BA or detritus import is prescribed.'}],
    'original_balance_availability': {
        'fresh_EwE_run_performed': False,
        'stored_native_export_for_discards': byseq[35]['Export'],
        'stored_native_export_is_finite_negative': byseq[35]['Export'] < 0,
        'stored_export_plus_independent_accepted_demand': byseq[35]['Export'] + demand,
        'interpretation': 'The native database itself stores negative Export for Discards while native BiomAcc, BiomAccRate and DtImports are zero. This is saved source evidence, not proof of a freshly reproduced native EwE balance or of author intent; input/output status of this saved field requires native-engine inspection.',
        'dedicated_balance_result_table': 'No explicitly named Ecopath result/balance table in complete user-table inventory; EcopathGroup contains saved flow fields.',
        'table_inventory': native['table_inventory']},
    'scientific_inputs_changed': False, 'new_offal_flow_adopted': False,
    'citations': {'paper_doi': '10.1017/S0025315423000887', 'paper_pdf': rel(pdf), 'supplement_s4': rel(docx),
                  's4_output': 'supplement_s4.json', 'fresh_native_tables': 'native_readonly_tables.json'},
}
save(OUT / 'source_fisheries_ledger.json', ledger)
after = {rel(p):sha(p) for p in protected}
save(QA / 'source_integrity.json', {'unchanged': before==after, 'before':before, 'after':after})
assert before==after, 'A protected input changed during the audit'
assert ledger['completeness']['all_group_fleet_pairs_present_once']
assert ledger['completeness']['finite_nonnegative_catches']
print(json.dumps({'ledger': rel(OUT / 'source_fisheries_ledger.json'), 'totals': ledger['totals'],
                  'stored_native_discards_export': byseq[35]['Export'], 'source_unchanged':before==after}, indent=2))
