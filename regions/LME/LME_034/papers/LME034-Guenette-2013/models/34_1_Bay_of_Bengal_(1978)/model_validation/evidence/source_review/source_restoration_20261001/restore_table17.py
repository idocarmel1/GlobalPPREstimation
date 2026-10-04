"""Restore printed Table 17 diets without changing any other scientific input."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import sys
from decimal import Decimal
from pathlib import Path

import numpy as np
import pymupdf
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
MODEL = ROOT / 'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json'
PDF = ROOT / 'regions/LME_034/papers/LME034-Guenette-2013/009031359-84f3dc3d.pdf'
BLOCKS = [(25, list(range(1, 16))), (26, list(range(16, 30))),
          (27, list(range(30, 42)) + [46, 47, 48])]
NUMBER = r'\d+(?:\.\d*)?(?:[Ee][+-]?\d+)?'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def extract():
    """Cross-check every cell using geometry and an independent text extractor."""
    doc = pymupdf.open(PDF)
    reader = PdfReader(PDF)
    cells = []
    by_key = {}
    pages = []
    for page_no, predators in BLOCKS:
        words = doc[page_no - 1].get_text('words')
        header = next(w for w in words if w[4] == 'Prey')
        anchors = sorted([w for w in words if abs(w[1] - header[1]) < 2
                          and w[4].isdigit() and w[0] > 120], key=lambda w: w[0])
        assert [int(w[4]) for w in anchors] == predators
        markers = sorted([w for w in words if w[4].isdigit() and w[0] < 50
                          and w[1] > header[1] + 3 and 1 <= int(w[4]) <= 50],
                         key=lambda w: w[1])
        text_rows = {}
        for line in (reader.pages[page_no - 1].extract_text() or '').splitlines():
            match = re.match(r'^\s*(\d+)\s+(.+)$', line)
            if not match:
                continue
            tokens = match[2].split()
            if len(tokens) <= len(predators):
                continue
            values = tokens[-len(predators):]
            if not all(re.fullmatch(NUMBER, v) for v in values):
                continue
            name = ' '.join(tokens[:-len(predators)])
            prey = 49 if name == 'Detritus' else 50 if name == 'Import' else int(match[1])
            text_rows[prey] = (name, values)
        assert len(markers) == len(text_rows) == (47 if page_no == 27 else 50)
        for marker in markers:
            row = sorted([w for w in words if abs(w[1] - marker[1]) < 2], key=lambda w: w[0])
            name = ' '.join(w[4] for w in row if marker[2] + 1 < w[0] < 125)
            prey = 49 if name == 'Detritus' else 50 if name == 'Import' else int(marker[4])
            assert prey in text_rows, (page_no, marker, name)
            values = {}
            for w in row:
                if w[0] <= 120 or not re.fullmatch(NUMBER, w[4]):
                    continue
                idx = min(range(len(anchors)), key=lambda i: abs(w[2] - anchors[i][2]))
                assert abs(w[2] - anchors[idx][2]) < 1.8, (page_no, prey, w, anchors[idx])
                pred = predators[idx]
                assert pred not in values
                values[pred] = w
            assert len(values) == len(predators), (page_no, prey, len(values))
            for pred, expected in zip(predators, text_rows[prey][1]):
                w = values[pred]
                assert w[4] == expected, (page_no, prey, pred, w[4], expected)
                cell = {'pdf_page': page_no, 'printed_page': page_no, 'table': '17',
                        'printed_prey_seq': int(marker[4]), 'prey_seq': prey,
                        'printed_prey_name': text_rows[prey][0], 'predator_seq': pred,
                        'printed_value': w[4], 'bbox_points': list(w[:4]),
                        'state': 'printed_zero' if Decimal(w[4]) == 0 else 'printed_value',
                        'independent_extractors_agree_exactly': True}
                key = (pred, prey)
                assert key not in by_key
                by_key[key] = cell
                cells.append(cell)
        pages.append({'pdf_page': page_no, 'predator_ids': predators,
                      'printed_prey_rows': len(markers),
                      'caption': 'Diet matrix from balanced model; bold values differ from original diet by 0.1% or more'})
        doc[page_no - 1].get_pixmap(matrix=pymupdf.Matrix(200 / 72, 200 / 72)).save(OUT / f'Table17_p{page_no}_200dpi.png')
    doc.close()
    missing = [{'pdf_page': 27, 'table': '17', 'predator_seq': pred, 'prey_seq': prey,
                'state': 'biological_prey_row_absent_unknown', 'canonical_proportion': None if pred == 40 else '-9999',
                'canonical_representation': 'Absent from unchanged researcher group40 Detritus1 override' if pred == 40 else 'Explicit -9999 unknown sentinel',
                'runtime_loading': 'Numerically zero under the explicit researcher group40 override' if pred == 40 else 'ModelData converts unknown sentinel to numerical zero, not a source biological zero'}
               for pred in BLOCKS[-1][1] for prey in (46, 47, 48)]
    assert len(cells) == 2155 and len(missing) == 45
    return cells, by_key, missing, pages


def non_diet(model):
    result = copy.deepcopy(model)
    for g in result['group']:
        g.pop('diet_imp', None)
        g.pop('diet_descr', None)
    return result


def main():
    sys.dont_write_bytecode = True
    OUT.mkdir(exist_ok=True)
    baseline = OUT / 'baseline'
    baseline.mkdir(exist_ok=True)
    if not (baseline / 'canonical_normalized_model.json').exists():
        for src, target in [(MODEL, 'canonical_normalized_model.json'),
                            (MODEL.parent / 'sppr_source.xlsx', 'sppr_source.xlsx'),
                            (ROOT / 'regions/LME_034/LME_034.xlsx', 'LME_034.xlsx')]:
            shutil.copy2(src, baseline / target)
    old = json.loads((baseline / 'canonical_normalized_model.json').read_text(encoding='utf-8'))
    cells, lookup, missing, pages = extract()
    new = copy.deepcopy(old)
    consumers = {p for _, ps in BLOCKS for p in ps}
    names = {int(g['group_seq']): g['group_name'] for g in old['group']}
    source_sums = {}
    changes = []
    for g in new['group']:
        pred = int(g['group_seq'])
        if pred not in consumers:
            source_sums[str(pred)] = '0'
            continue
        if pred == 40:
            # Explicit researcher-authored override: preserve it exactly.
            # Table 17's printed column is zero; source evidence remains separate.
            source_sums[str(pred)] = str(sum((Decimal(lookup[pred, prey]['printed_value'])
                                             for prey in range(1, 51) if (pred, prey) in lookup), Decimal(0)))
            continue
        old_g = next(x for x in old['group'] if int(x['group_seq']) == pred)
        diets = (old_g.get('diet_descr') or {}).get('diet', [])
        diets = diets if isinstance(diets, list) else [diets]
        existing = {int(float(d['prey_seq'])): d for d in diets}
        rebuilt = []
        total = Decimal(lookup[pred, 50]['printed_value'])
        for prey in range(1, 50):
            entry = copy.deepcopy(existing.get(prey, {'prey_seq': str(prey), 'detritus_fate': '0'}))
            entry['proportion'] = lookup[pred, prey]['printed_value'] if (pred, prey) in lookup else '-9999'
            if (pred, prey) in lookup:
                total += Decimal(entry['proportion'])
            prior = existing.get(prey, {}).get('proportion', '0')
            if Decimal(prior) != Decimal(entry['proportion']):
                changes.append({'predator_seq': pred, 'predator_name': names[pred], 'prey_seq': prey,
                                'prior_proportion': prior, 'restored_proportion': entry['proportion'],
                                'reason': 'unknown omitted row retained explicitly' if entry['proportion'] == '-9999'
                                else 'printed source value restored without normalization'})
            rebuilt.append(entry)
        g['diet_descr']['diet'] = rebuilt
        g['diet_imp'] = lookup[pred, 50]['printed_value']
        source_sums[str(pred)] = str(total)
    assert non_diet(new) == non_diet(old)
    # Retain all original detritus-fate routing, independently from diet proportions.
    for before, after in zip(old['group'], new['group']):
        def routing(g):
            ds = (g.get('diet_descr') or {}).get('diet', [])
            ds = ds if isinstance(ds, list) else [ds]
            return {int(float(d['prey_seq'])): Decimal(d['detritus_fate']) for d in ds if Decimal(d['detritus_fate']) != 0}
        assert routing(before) == routing(after)
    MODEL.write_text(json.dumps(new, ensure_ascii=False, indent=4) + '\n', encoding='utf-8')
    sys.path.insert(0, str(ROOT / 'tools/scientific_code/PPREstimation'))
    from ModelData import ModelData
    md = ModelData(str(MODEL))
    sums = md.DC.sum(axis=1)
    deltas = {seq: float(sums.loc[int(seq)]) - (1.0 if seq == '40' else float(Decimal(total)))
              for seq, total in source_sums.items()}
    assert max(abs(v) for v in deltas.values()) < 1e-12
    assert sums.loc[40] == 1 and md.DC.loc[40, 49] == 1
    assert md.DC.loc[:, [46, 47, 48]].abs().to_numpy().max() == 0
    ledger = {'schema_version': 1, 'run_id': 'LME034_source_restoration_20261001',
              'source_pdf': PDF.relative_to(ROOT).as_posix(), 'source_sha256': sha(PDF),
              'canonical_model': MODEL.relative_to(ROOT).as_posix(), 'canonical_sha256': sha(MODEL),
              'prior_normalized_sha256': sha(baseline / 'canonical_normalized_model.json'),
              'source_orientation': 'prey rows x predator columns',
              'modeldata_orientation': 'predator rows x prey columns', 'pages': pages,
              'printed_cells': cells, 'source_missing_diet_cells': missing,
              'source_missing_cell_count': 45, 'printed_cell_count': len(cells),
              'canonical_unknown_sentinel_count': 42, 'source_unknown_cells_in_researcher_override_row': 3,
              'unprinted_nonfeeding_predator_columns': [42, 43, 44, 45, 49],
              'crosswalk': [{'pdf_page': 27, 'printed_seq': 46, 'prey_seq': 49, 'name': 'Detritus'},
                            {'pdf_page': 27, 'printed_seq': 47, 'prey_seq': 50, 'name': 'Import'}],
              'source_sums_exact_decimal_including_import': source_sums,
              'modeldata_sums': {str(k): float(v) for k, v in sums.items()},
              'max_abs_modeldata_sum_delta': max(abs(v) for v in deltas.values()),
              'restorations': changes, 'non_diet_parameters_unchanged': True,
              'detritus_fate_unchanged': True,
              'researcher_overrides': [{'predator_seq': 40, 'predator_name': names[40], 'prey_seq': 49,
                                       'source_printed_proportion': '0', 'source_column_sum': '0',
                                       'researcher_proportion': '1', 'canonical_column_sum': '1',
                                       'authorization': 'Researcher explicitly confirmed on 2026-10-01 that this intentional edit must remain in canonical JSON',
                                       'unchanged_from_prior_canonical': True,
                                       'source_based_justification': json.loads((OUT / 'meiobenthos_source_justification.json').read_text(encoding='utf-8'))}],
              'runtime_policy': 'Raw ModelData preserves printed totals except the explicit researcher group40 Detritus=1 override. Calculator normalization operates on a separate copy; missing sentinel cells are numerically zero. No missing diet was reconstructed.'}
    (OUT / 'table17_source_ledger.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: ledger[k] for k in ['printed_cell_count', 'source_missing_cell_count',
                       'max_abs_modeldata_sum_delta', 'canonical_sha256', 'non_diet_parameters_unchanged']}))
    print('Selected source totals:', {k: source_sums[k] for k in ['30','32','33','36','38','39','40','41','46','47','48']})


if __name__ == '__main__':
    main()
