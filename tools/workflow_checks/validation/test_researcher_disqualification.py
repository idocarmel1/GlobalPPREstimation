"""Rejected researcher decisions are current reviews, never validated models."""
import copy
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as E

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.project_core.validation.researcher_review import read_report, register_review, approved_review, review_display, sha
from tools.project_core.workbooks.workbooks import write_book, read_book, records
from tools.project_core.maps.build_html import linked_layout, refresh_reviews
from tools.project_core.maps.original_atlas_data import add_source_reviews

ROOT = Path(__file__).resolve().parents[3]
REASON = 'Reason – too strong living compartments recycling due to near-zero EE values (rho_living = 0.99).'
STATUS = 'Disqualified by researcher'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def report_fixture(root, decision='MODEL DISQUALIFIED', reason=REASON, identity_label='Selected model'):
    doc = E.Element(W+'document'); body = E.SubElement(doc, W+'body')
    table = E.SubElement(body, W+'tbl')
    def row(parent, values):
        tr = E.SubElement(parent, W+'tr')
        for value in values:
            tc = E.SubElement(tr, W+'tc'); p = E.SubElement(tc, W+'p')
            E.SubElement(E.SubElement(p, W+'r'), W+'t').text = value
    for key, value in [(identity_label, 'm; exact reviewed model'),
                       ('Model extraction', 'Source extraction'), ('GE diagnostics', 'GE WARN'),
                       ('TE diagnostics', 'TE WARN'), ('SPPR calculation', 'Removed groups from calculation:\nFish (GE=0.1%)'),
                       ('Geographic fit', 'Source geography'),
                       ('Review and reproducibility', 'Researcher name: Reviewer | review date: 02/10/2026\n'+decision+'\n'+reason)]:
        row(table, [key, value])
    confidence = E.SubElement(body, W+'tbl')
    row(confidence, ['Overall confidence', 'PPR percentage'])
    for level in ['High', 'Medium', 'Low', 'Very low', 'Unresolved']:
        row(confidence, [level, '0%'])
    report = root/'review.docx'
    with zipfile.ZipFile(report, 'w') as z:
        z.writestr('word/document.xml', E.tostring(doc))
        z.writestr('word/_rels/document.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
    return report


class DisqualificationTests(unittest.TestCase):
    def test_unselected_validation_uses_own_snapshot_groups_and_freshness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = report_fixture(root, decision='MODEL VALIDATED', reason='', identity_label='Candidate model')
            model = root/'regions/LME/LME_001/papers/P/models/m/model.json'
            model.parent.mkdir(parents=True); model.write_text('{}')
            region_book = {'Overview': {'Settings': (['field','value'], [['selected_model_id','default'], ['calculation_input_sha256','default-inputs']])},
                           'Selected model groups': {'Groups': (['seq','group_name'], [[1,'Default fish']])}}
            regional = root/'regions/LME/LME_001/LME_001.xlsx'; write_book(regional, region_book)
            saved = {'Overview': {'Settings': (['field','value'], [['selected_model_id','default'], ['results_model_id','m'], ['results_model_sha256',sha(model)], ['calculation_input_sha256','candidate-inputs']])},
                     'Selected model groups': {'Groups': (['seq','group_name'], [[1,'Fish']])}}
            snapshot = model.parent/'results/regional_snapshot.xlsx'
            snapshot.parent.mkdir(); write_book(snapshot, saved)
            project = root/'Project.xlsx'
            write_book(project, {'Models & coverage': {'Models': (['unit_id','model_id','model_path'], [['LME_001','m',model.relative_to(root).as_posix()]])}})
            prior = root/'before.xlsx'; prior.write_bytes(project.read_bytes())
            protected = {p: sha(p) for p in [report, regional, snapshot, model]}
            values = register_review(project, report, 'LME_001', 'm', [1])
            self.assertEqual(values['reviewed_calculation_input_sha256'], 'candidate-inputs')
            metadata = records(read_book(project), 'Models & coverage', 'Models')[0]
            review = approved_review(root, metadata, region_book)
            self.assertEqual(review['status'], 'Validated by researcher')
            self.assertEqual(review['excluded_group_ids'], ['Fish'])
            rebuilt = [{'default_model': 'default', 'models': [{'id':'default'}]}]
            add_source_reviews(root, 'LME_001', {('LME_001','m'):metadata}, rebuilt)
            self.assertEqual(rebuilt[0]['default_model'], 'default')
            self.assertEqual(rebuilt[0]['models'][1]['researcher_review'], review)
            self.assertFalse(rebuilt[0]['models'][1]['verified'])
            # A valid signoff for the snapshot cannot approve different retained
            # calculations. Both candidates remain available in model controls.
            numerical = {'id':'m', 'verified':True, 'scopes':{'full':{'ppr':[999]}},
                         'workbook_sha256':'different-displayed-workbook',
                         'recorded_review_pending':{'reason':'old warning'}}
            matching = copy.deepcopy(numerical); matching['workbook_sha256'] = sha(snapshot)
            retained = [{'default_model':'default', 'models':[{'id':'default'}, copy.deepcopy(numerical)]},
                        {'default_model':'default', 'models':[{'id':'default'}, copy.deepcopy(matching)]}]
            add_source_reviews(root, 'LME_001', {('LME_001','m'):metadata}, retained)
            self.assertNotIn('researcher_review', retained[0]['models'][1])
            self.assertNotIn('display_ppr_excluded_group_ids', retained[0]['models'][1])
            self.assertEqual(retained[0]['models'][1]['recorded_review_pending']['recorded_status'], 'Validated by researcher')
            self.assertEqual(retained[0]['models'][1]['scopes'], numerical['scopes'])
            self.assertEqual(retained[1]['models'][1]['researcher_review'], review)
            self.assertNotIn('recorded_review_pending', retained[1]['models'][1])
            for page, variable, candidate in [('index.html','DB',numerical), ('trends.html','SERIES_DB',matching)]:
                unit = {'default_model':'default', 'models':[{'id':'default'}, copy.deepcopy(candidate)]}
                payload = {'network':{'units':{'LME_001':unit}}} if variable == 'DB' else {'units':{'LME_001':unit}}
                text = linked_layout((ROOT/'tools/project_core/maps/original_html_layout'/page).read_text(encoding='utf-8'))
                text = text.replace('__PPR_DATA__', json.dumps(payload))
                text = text.replace('</head>', '<meta name="ppr-project-sha256" content="'+sha(prior)+'"></head>', 1)
                (root/page).write_text(text, encoding='utf-8')
            refresh_reviews(project, prior, ['LME_001'], root, model_ids={'LME_001':'m'})
            for page, variable in [('index.html','DB'), ('trends.html','SERIES_DB')]:
                text = (root/page).read_text(encoding='utf-8')
                start = text.index('const '+variable+'=')+len('const '+variable+'=')
                payload, _ = json.JSONDecoder().raw_decode(text, start)
                unit = (payload['network']['units'] if variable == 'DB' else payload['units'])['LME_001']
                self.assertEqual(unit['default_model'], 'default')
                self.assertEqual(unit['models'][0], {'id':'default'})
                candidate = unit['models'][1]
                self.assertEqual(candidate['scopes'], numerical['scopes'])
                if variable == 'DB':
                    self.assertNotIn('researcher_review', candidate)
                    self.assertNotIn('display_ppr_excluded_group_ids', candidate)
                    self.assertEqual(candidate['recorded_review_pending']['recorded_status'], 'Validated by researcher')
                else:
                    self.assertEqual(candidate['researcher_review'], review)
                    self.assertNotIn('recorded_review_pending', candidate)
            self.assertEqual({p:sha(p) for p in protected}, protected)
            saved['Overview']['Settings'][1][-1][1] = 'changed-candidate-inputs'
            write_book(snapshot, saved)
            with self.assertRaisesRegex(ValueError, 'calculation inputs changed'):
                approved_review(root, metadata, region_book)

    def test_candidate_identity_is_reviewable_and_still_rejects_another_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); report = report_fixture(root, identity_label='Candidate model')
            self.assertEqual(read_report(root, report, 'm')[2]['reason'], REASON)
            with self.assertRaisesRegex(ValueError, 'different model'):
                read_report(root, report, 'another')

    def test_unselected_rejection_is_switchable_without_default_results_or_input_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); report = report_fixture(root, identity_label='Candidate model')
            model = root/'regions/LME/LME_001/papers/P/models/m/model.json'
            model.parent.mkdir(parents=True); model.write_text('{}', encoding='utf-8')
            default = model.parent.parent/'default/model.json'
            default.parent.mkdir(); default.write_text('{}', encoding='utf-8')
            regional = root/'regions/LME/LME_001/LME_001.xlsx'
            region_book = {'Overview': {'Settings': (['field', 'value'], [['selected_model_id', 'default'], ['calculation_input_sha256', 'default-input-hash']])},
                           'Selected model groups': {'Groups': (['seq', 'group_name'], [[1, 'Default fish']])}}
            write_book(regional, region_book)
            project = root/'Project.xlsx'; prior = root/'before.xlsx'
            write_book(project, {'Models & coverage': {'Models': (['unit_id', 'model_id', 'model_path', 'selected'], [
                ['LME_001', 'm', model.relative_to(root).as_posix(), False],
                ['LME_001', 'default', default.relative_to(root).as_posix(), True]])},
                'Science': {'Values': (['value'], [[1.23456789012345]])}})
            prior.write_bytes(project.read_bytes())
            original_model = {'id': 'default', 'verified': True, 'values': [1.23456789012345, None]}
            payloads = {'DB': {'network': {'units': {'LME_001': {'default_model': 0, 'models': [original_model]}}}},
                        'SERIES_DB': {'units': {'LME_001': {'default_model': 'default', 'models': [original_model]}}}}
            for page, variable in [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]:
                text = linked_layout((ROOT/'tools/project_core/maps/original_html_layout'/page).read_text(encoding='utf-8'))
                text = text.replace('__PPR_DATA__', json.dumps(payloads[variable]))
                text = text.replace('</head>', '<meta name="ppr-project-sha256" content="'+sha(prior)+'"></head>', 1)
                (root/page).write_text(text, encoding='utf-8')
            protected = {p: sha(p) for p in [report, regional, model, default]}
            values = register_review(project, report, 'LME_001', 'm', [])
            self.assertFalse(values['reviewed_calculation_input_sha256'], 'A candidate must never inherit the default calculation identity')
            metadata = records(read_book(project), 'Models & coverage', 'Models')[0]
            review = approved_review(root, metadata, region_book)
            changed_book = copy.deepcopy(region_book)
            changed_book['Overview']['Settings'][1][1][1] = 'new-default-input-hash'
            self.assertEqual(approved_review(root, metadata, changed_book), review, 'Default inputs do not invalidate a source-only candidate rejection')
            refresh_reviews(project, prior, ['LME_001'], root, model_ids={'LME_001': 'm'})
            for page, variable in [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]:
                text = (root/page).read_text(encoding='utf-8')
                start = text.index('const '+variable+'=')+len('const '+variable+'=')
                payload, _ = json.JSONDecoder().raw_decode(text, start)
                unit = (payload['network']['units'] if variable == 'DB' else payload['units'])['LME_001']
                self.assertEqual(unit['models'][0], original_model)
                self.assertEqual(unit['default_model'], 0 if variable == 'DB' else 'default')
                candidate = unit['models'][1]
                self.assertEqual(candidate['id'], 'm')
                self.assertFalse(candidate['verified'])
                self.assertEqual(candidate['scopes'], {})
                self.assertEqual(candidate['researcher_review'], review)
                self.assertEqual(candidate['display_ppr_excluded_group_ids'], [])
                self.assertNotIn('values', candidate)
                self.assertNotIn('workbook', candidate, 'Candidate must not borrow the default workbook')
            self.assertEqual({p: sha(p) for p in protected}, protected)
            rows = records(read_book(project), 'Models & coverage', 'Models')
            self.assertFalse(rows[0]['selected']); self.assertTrue(rows[1]['selected'])
            with zipfile.ZipFile(prior) as before, zipfile.ZipFile(project) as after:
                self.assertEqual(before.read('xl/worksheets/sheet2.xml'), after.read('xl/worksheets/sheet2.xml'))
            # A future full build starts from retained source context. It must
            # retain the candidate's decision even when another model is default.
            rebuilt = [{'default_model': 'default', 'models': [copy.deepcopy(original_model)]},
                       {'default_model': 0, 'models': [copy.deepcopy(original_model)]}]
            add_source_reviews(root, 'LME_001', {('LME_001', 'm'): metadata}, rebuilt)
            for unit in rebuilt:
                self.assertEqual(unit['models'][0], original_model)
                self.assertEqual(unit['models'][1]['researcher_review'], review)
            tampered = copy.deepcopy(metadata)
            tampered['researcher_review_status'] = 'Validated by researcher'
            with self.assertRaisesRegex(ValueError, 'source-only rejection'):
                approved_review(root, tampered, region_book)
            tampered = copy.deepcopy(metadata)
            tampered['reviewed_calculation_input_sha256'] = 'default-input-hash'
            with self.assertRaisesRegex(ValueError, 'source-only rejection'):
                approved_review(root, tampered, region_book)
            model.write_text('{"changed":true}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'source changed'):
                approved_review(root, metadata, region_book)
            add_source_reviews(root, 'LME_001', {('LME_001', 'm'): metadata}, rebuilt)
            for unit in rebuilt:
                self.assertNotIn('researcher_review', unit['models'][1])
                self.assertEqual(unit['models'][1]['recorded_review_pending']['recorded_status'], STATUS)
                self.assertFalse(unit['models'][1]['verified'])

    def test_disqualified_signed_source_has_exact_reason_and_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); report = report_fixture(root)
            name, date, summary = read_report(root, report, 'm')
            self.assertEqual((name, date), ('Reviewer', '2026-10-02'))
            self.assertEqual(summary['status'], STATUS)
            self.assertEqual(summary['verdict'], 'MODEL DISQUALIFIED')
            self.assertEqual(summary['reason'], REASON)
            self.assertEqual(summary['sections'], [])

    def test_rejection_without_reason_or_conflicting_verdict_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, '[Rr]eason'):
                read_report(root, report_fixture(root, reason=''), 'm')
            with self.assertRaisesRegex(ValueError, '[Dd]ecision|[Vv]erdict'):
                read_report(root, report_fixture(root, decision='MODEL DISQUALIFIED\nMODEL VALIDATED'), 'm')

    def test_validated_snapshot_schema_remains_compatible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = read_report(root, report_fixture(root, decision='MODEL VALIDATED', reason=''), 'm')[2]
            self.assertEqual(summary['schema_version'], 1)
            self.assertNotIn('status', summary)
            self.assertEqual(len(summary['sections']), 5)

    def test_registration_red_styles_freshness_and_bounded_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); report = report_fixture(root)
            model = root/'regions/LME/LME_001/papers/P/models/m/model.json'; model.parent.mkdir(parents=True)
            model.write_text('{}', encoding='utf-8')
            regional = root/'regions/LME/LME_001/LME_001.xlsx'
            region_book = {'Overview': {'Settings': (['field', 'value'], [['selected_model_id', 'm'], ['calculation_input_sha256', 'input-hash']])},
                           'Selected model groups': {'Groups': (['seq', 'group_name'], [[1, 'Fish']])}}
            write_book(regional, region_book)
            project = root/'Project.xlsx'; prior = root/'before.xlsx'
            book = {'Models & coverage': {'Models': (['unit_id', 'model_id', 'model_path'], [['LME_001', 'm', model.relative_to(root).as_posix()]])},
                    'Science': {'Values': (['value'], [[1.23456789012345]])}}
            write_book(project, book); prior.write_bytes(project.read_bytes())
            payloads = {'DB': {'network': {'units': {'LME_001': {'models': [{'id': 'm', 'values': [1.23456789012345, None]}]}}}},
                        'SERIES_DB': {'units': {'LME_001': {'models': [{'id': 'm', 'values': [1.23456789012345, None]}]}}}}
            for page, variable in [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]:
                text = linked_layout((ROOT/'tools/project_core/maps/original_html_layout'/page).read_text(encoding='utf-8'))
                text = text.replace('__PPR_DATA__', json.dumps(payloads[variable]))
                text = text.replace('</head>', '<meta name="ppr-project-sha256" content="'+sha(prior)+'"></head>', 1)
                (root/page).write_text(text, encoding='utf-8')
            protected = {p: sha(p) for p in [report, regional, model]}
            values = register_review(project, report, 'LME_001', 'm', [])
            self.assertEqual(values['researcher_review_status'], STATUS)
            metadata = records(read_book(project), 'Models & coverage', 'Models')[0]
            review = approved_review(root, metadata, region_book)
            self.assertEqual(review['reason'], REASON)
            self.assertEqual(review['excluded_group_ids'], [], 'Rejection does not adopt draft group-removal notes')
            wb = openpyxl.load_workbook(project, read_only=True)
            self.assertEqual(wb['Models & coverage']['B3'].font.color.rgb, 'FFB42318'); wb.close()
            refresh_reviews(project, prior, ['LME_001'], root)
            for page, variable in [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]:
                text = (root/page).read_text(encoding='utf-8')
                start = text.index('const '+variable+'=')+len('const '+variable+'=')
                payload, _ = json.JSONDecoder().raw_decode(text, start)
                units = payload['network']['units'] if variable == 'DB' else payload['units']
                entry = units['LME_001']['models'][0]
                self.assertEqual(entry.pop('researcher_review'), review)
                self.assertEqual(entry.pop('display_ppr_excluded_group_ids'), [])
                self.assertEqual(payload, payloads[variable])
            self.assertEqual({p: sha(p) for p in protected}, protected)
            changed = copy.deepcopy(metadata)
            changed['researcher_review_summary'] = changed['researcher_review_summary'].replace('0.99', '0.50')
            with self.assertRaisesRegex(ValueError, 'snapshot differs'):
                approved_review(root, changed, region_book)
            before=copy.deepcopy(metadata)
            stale_book=copy.deepcopy(region_book)
            stale_book['Overview']['Settings'][1][1][1]='changed-input-hash'
            with self.assertRaisesRegex(ValueError,'calculation inputs changed'):
                approved_review(root,metadata,stale_book)
            active,pending=review_display(root,metadata,stale_book)
            self.assertIsNone(active)
            self.assertEqual(pending['recorded_status'],STATUS)
            self.assertEqual((pending['researcher_name'],pending['review_date']),('Reviewer','2026-10-02'))
            self.assertEqual(pending['report_path'],metadata['validation_report_path'])
            self.assertIn('calculation inputs changed',pending['reason'])
            self.assertNotIn('excluded_group_ids',pending)
            self.assertEqual(metadata,before,'Pending presentation preserves the recorded human decision')
            write_book(project, read_book(project))
            wb = openpyxl.load_workbook(project, read_only=True)
            try:
                self.assertTrue(wb['Models & coverage']['B3'].font.color.rgb.endswith('B42318'))
            finally:
                wb.close()
            with self.assertRaisesRegex(ValueError, '[Ee]xclusion'):
                register_review(project, report, 'LME_001', 'm', [1])


if __name__ == '__main__':
    unittest.main()
